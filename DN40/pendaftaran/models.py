from django.db import models
from django.contrib.auth.models import User


class Registration(models.Model):
    class Package(models.TextChoices):
        ALUMNI = 'alumni', 'Paket Alumni'
        MAHASISWA = 'mahasiswa', 'Paket Mahasiswa Aktif'
        NON_PAKET = 'non-paket', 'Non-Paket'

    class StudyProgram(models.TextChoices):
        ILMU_KOMPUTER = 'ilmu-komputer', 'Ilmu Komputer'
        SISTEM_INFORMASI = 'sistem-informasi', 'Sistem Informasi'
        KECERDASAN_ARTIFISIAL = 'kecerdasan-artifisial', 'Kecerdasan Artifisial'
        KELAS_INTERNASIONAL = 'kelas-internasional', 'Kelas Internasional'

    class ShirtSize(models.TextChoices):
        XS = 'XS', 'XS'
        S = 'S', 'S'
        M = 'M', 'M'
        L = 'L', 'L'
        XL = 'XL', 'XL'
        XXL = 'XXL', 'XXL'
        XXXL = 'XXXL', 'XXXL'
        XXXXL = 'XXXXL', 'XXXXL'

    UNIT_PRICES = {
        Package.ALUMNI: 275_000,
        Package.MAHASISWA: 175_000,
        Package.NON_PAKET: 50_000,
    }

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='registrations')
    package = models.CharField(max_length=20, choices=Package.choices)
    full_name = models.CharField(max_length=150)
    whatsapp_number = models.CharField(max_length=20)
    cohort_year = models.PositiveSmallIntegerField()
    study_program = models.CharField(max_length=30, choices=StudyProgram.choices)
    ticket_quantity = models.PositiveSmallIntegerField(default=1)
    shirt_size = models.CharField(max_length=5, choices=ShirtSize.choices, blank=True)
    unit_price = models.PositiveIntegerField()
    total_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} — {self.get_package_display()}'
