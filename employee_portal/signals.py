from django.db.models.signals import post_save
from django.dispatch import receiver
from company.models import Company
from employee_portal.models import AttendanceSettings

@receiver(post_save, sender=Company)
def create_attendance_settings(sender, instance, created, **kwargs):
    if created:
        AttendanceSettings.objects.create(company=instance)
