import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

def home(request):
    return render(request, 'pendaftaran/home.html')


def login_register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        if not email or not password:
            messages.error(request, 'Email dan password wajib diisi.')
        else:
            user = authenticate(request, username=email, password=password)
            if user is None and not User.objects.filter(username=email).exists():
                user = User.objects.create_user(username=email, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(request.GET.get('next') or 'home')
            messages.error(request, 'Password salah untuk email tersebut.')
    return render(request, 'pendaftaran/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def history(request):
    return render(request, 'pendaftaran/history.html')


@login_required
def buy(request, kategori):
    labels = {'alumni': 'Paket Alumni', 'mahasiswa': 'Paket Mahasiswa Aktif', 'non-paket': 'Non-Paket'}
    return render(request, 'pendaftaran/checkout.html', {'paket': labels.get(kategori, kategori.title())})


def sso_start(request):
    if not settings.SSO_UI_AUTHORIZE_URL or not settings.SSO_UI_CLIENT_ID:
        messages.info(request, 'SSO UI belum dikonfigurasi. Lihat panduan di README.md.')
        return redirect('login')
    state = secrets.token_urlsafe(24)
    request.session['sso_state'] = state
    query = urlencode({'client_id': settings.SSO_UI_CLIENT_ID, 'redirect_uri': settings.SSO_UI_REDIRECT_URI,
                       'response_type': 'code', 'scope': 'openid email profile', 'state': state})
    return redirect(f'{settings.SSO_UI_AUTHORIZE_URL}?{query}')


def sso_callback(request):
    """Callback scaffold: tukarkan `code` di server sesuai metadata OIDC resmi UI."""
    if request.GET.get('state') != request.session.pop('sso_state', None):
        messages.error(request, 'Sesi SSO tidak valid. Silakan coba kembali.')
    else:
        messages.info(request, 'Kode SSO diterima. Konfigurasikan token endpoint UI sesuai README.')
    return redirect('login')
