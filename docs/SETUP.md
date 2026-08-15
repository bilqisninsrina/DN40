# Panduan DN40 — Pendaftaran Fun Walk Dies Natalis

Prototipe Django untuk landing page, registrasi/login alumni, pintu masuk SSO UI, history, dan halaman awal checkout.

## Menjalankan secara lokal

Persyaratan: Python 3.12+.

```bash
# Jalankan dari folder root repository (folder yang berisi requirements.txt)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python DN40/manage.py migrate
python DN40/manage.py runserver
```

Buka <http://127.0.0.1:8000>. Hentikan server dengan `Ctrl+C`. Jalankan pengujian
dari root repository dengan `python DN40/manage.py test`.

Alternatifnya, setelah dependency terpasang, masuk ke folder project dengan
`cd DN40`, lalu gunakan perintah Django yang lebih pendek: `python manage.py
migrate` dan `python manage.py runserver`.

## Alur login

- **Alumni:** masukkan email dan password. Bila email belum ada, aplikasi membuat akun; bila sudah ada, password diverifikasi. Untuk produksi, pisahkan form daftar/masuk, tambahkan verifikasi email, persetujuan privasi, rate limiting, dan reset password.
- **Mahasiswa aktif:** tombol SSO memulai Authorization Code Flow OIDC. Scaffold saat ini sengaja tidak menukar kode menjadi token sebelum kredensial dan metadata resmi UI tersedia.

### Integrasi SSO UI secara aman

1. Daftarkan aplikasi ke Direktorat STI UI dan minta metadata OIDC, `client_id`, `client_secret`, scope yang diizinkan, serta whitelist callback HTTPS produksi.
2. Atur variabel lingkungan (jangan commit secret):

   ```bash
   export SSO_UI_AUTHORIZE_URL='https://<host-resmi-ui>/authorize'
   export SSO_UI_CLIENT_ID='<client-id>'
   export SSO_UI_REDIRECT_URI='http://localhost:8000/auth/sso/callback/'
   ```

3. `sso_start` membuat `state` acak dan mengarah ke authorization endpoint. Di `sso_callback`, validasi `state`, tukar `code` ke token endpoint **melalui POST dari server**, validasi signature/issuer/audience/expiry ID token memakai JWKS UI, lalu ambil claim email/NPM.
4. Cocokkan hanya domain/claim mahasiswa yang disetujui UI; buat atau hubungkan `User`, panggil `login(request, user)`, dan simpan identitas minimum. Gunakan library OIDC yang dipelihara (misalnya Authlib atau social-auth-app-django), bukan implementasi kriptografi sendiri.
5. Produksi wajib memakai HTTPS, secret manager, cookie `Secure`/`HttpOnly`/`SameSite`, rotasi session setelah login, serta logout/revocation resmi bila disediakan UI.

## Payment Gateway UI

Halaman checkout masih berupa batas integrasi. Setelah memperoleh dokumentasi dan sandbox resmi UI: buat transaksi di backend, simpan external transaction ID dan status, arahkan pengguna ke hosted payment page, verifikasi signature callback/webhook, dan selalu query status server-to-server sebelum menandai pembayaran lunas. Jangan menerima nominal atau status dari browser sebagai sumber kebenaran. Gunakan idempotency key dan audit log.

## Catatan aset

Font Poppins dimuat dari Google Fonts dan foto acara memakai URL Unsplash sementara. Ganti dengan aset resmi panitia di `static/` sebelum deploy agar tampilan identik dan tidak bergantung pada layanan eksternal.
