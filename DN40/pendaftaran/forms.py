from django import forms

from .models import Registration


class RegistrationForm(forms.ModelForm):
    cohort_year = forms.TypedChoiceField(
        label='Tahun Angkatan',
        choices=[(year, year) for year in range(2026, 1984, -1)],
        coerce=int,
    )

    class Meta:
        model = Registration
        fields = [
            'full_name',
            'whatsapp_number',
            'cohort_year',
            'study_program',
            'ticket_quantity',
            'shirt_size',
        ]
        labels = {
            'full_name': 'Nama Lengkap',
            'whatsapp_number': 'Nomor WhatsApp',
            'study_program': 'Program Studi',
            'ticket_quantity': 'Jumlah Tiket',
            'shirt_size': 'Ukuran Baju',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'whatsapp_number': forms.TextInput(
                attrs={'inputmode': 'numeric', 'pattern': '[0-9]+', 'autocomplete': 'tel'}
            ),
            'ticket_quantity': forms.NumberInput(attrs={'min': 1, 'max': 20}),
        }

    def __init__(self, *args, package, **kwargs):
        super().__init__(*args, **kwargs)
        self.package = package
        if package == Registration.Package.NON_PAKET:
            self.fields.pop('shirt_size')
        else:
            self.fields['ticket_quantity'].disabled = True
            self.fields['ticket_quantity'].initial = 1
            self.fields['ticket_quantity'].help_text = 'Paket hanya dapat dibeli satu per transaksi.'

    def clean_whatsapp_number(self):
        number = self.cleaned_data['whatsapp_number']
        if not number.isdigit():
            raise forms.ValidationError('Nomor WhatsApp hanya boleh berisi angka.')
        return number

    def clean_ticket_quantity(self):
        quantity = self.cleaned_data['ticket_quantity']
        if self.package != Registration.Package.NON_PAKET:
            return 1
        if not 1 <= quantity <= 20:
            raise forms.ValidationError('Jumlah tiket harus antara 1 sampai 20.')
        return quantity
