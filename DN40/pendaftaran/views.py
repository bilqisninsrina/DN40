import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .exports import xlsx_response
from .forms import RegistrationForm
from .models import Registration

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
    registrations = request.user.registrations.all()
    return render(request, 'pendaftaran/history.html', {'registrations': registrations})


@login_required
def buy(request, kategori):
    valid_packages = {value for value, _label in Registration.Package.choices}
    if kategori not in valid_packages:
        return redirect('home')

    unit_price = Registration.UNIT_PRICES[kategori]
    form = RegistrationForm(request.POST or None, package=kategori)
    if request.method == 'POST' and form.is_valid():
        registration = form.save(commit=False)
        registration.user = request.user
        registration.package = kategori
        registration.unit_price = unit_price
        registration.total_price = unit_price * registration.ticket_quantity
        registration.save()
        messages.success(request, 'Data pendaftaran tersimpan dan siap dilanjutkan ke pembayaran.')
        return redirect('history')

    context = {
        'form': form,
        'package': kategori,
        'package_name': Registration.Package(kategori).label,
        'unit_price': unit_price,
        'formatted_unit_price': f'Rp{unit_price:,}'.replace(',', '.'),
    }
    return render(request, 'pendaftaran/checkout.html', context)


@staff_member_required
def export_registrations(request):
    columns = [
        'ID', 'Tanggal', 'Kategori Paket', 'Nama Lengkap', 'Email', 'Nomor WhatsApp',
        'Tahun Angkatan', 'Program Studi', 'Jumlah Tiket', 'Ukuran Baju',
        'Harga Satuan', 'Total Harga',
    ]
    rows = [columns]
    for item in Registration.objects.select_related('user').all():
        rows.append([
            item.pk,
            item.created_at.astimezone().strftime('%Y-%m-%d %H:%M'),
            item.get_package_display(),
            item.full_name,
            item.user.email,
            item.whatsapp_number,
            item.cohort_year,
            item.get_study_program_display(),
            item.ticket_quantity,
            item.get_shirt_size_display() or '-',
            item.unit_price,
            item.total_price,
        ])
    return xlsx_response(rows)


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
