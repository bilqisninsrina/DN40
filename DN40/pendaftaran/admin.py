from django.contrib import admin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'package',
        'study_program',
        'cohort_year',
        'ticket_quantity',
        'total_price',
        'created_at',
    )
    list_filter = ('package', 'study_program', 'cohort_year', 'shirt_size', 'created_at')
    search_fields = ('full_name', 'whatsapp_number', 'user__email')
    date_hierarchy = 'created_at'
