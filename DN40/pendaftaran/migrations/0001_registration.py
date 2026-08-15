from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('package', models.CharField(choices=[('alumni', 'Paket Alumni'), ('mahasiswa', 'Paket Mahasiswa Aktif'), ('non-paket', 'Non-Paket')], max_length=20)),
                ('full_name', models.CharField(max_length=150)),
                ('whatsapp_number', models.CharField(max_length=20)),
                ('cohort_year', models.PositiveSmallIntegerField()),
                ('study_program', models.CharField(choices=[('ilmu-komputer', 'Ilmu Komputer'), ('sistem-informasi', 'Sistem Informasi'), ('kecerdasan-artifisial', 'Kecerdasan Artifisial'), ('kelas-internasional', 'Kelas Internasional')], max_length=30)),
                ('ticket_quantity', models.PositiveSmallIntegerField(default=1)),
                ('shirt_size', models.CharField(blank=True, choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL'), ('XXXXL', 'XXXXL')], max_length=5)),
                ('unit_price', models.PositiveIntegerField()),
                ('total_price', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='registrations', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
