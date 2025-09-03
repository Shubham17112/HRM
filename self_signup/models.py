import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from company.models import Company

import uuid
from django.conf import settings
from django.db import models
from company.models import Company
from django.utils import timezone


class EmployeeInvite(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="invites"
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_invites"
    )

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Invite for {self.company.name} (expires {self.expires_at})"
