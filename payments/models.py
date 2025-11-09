# payments/models.py
from django.db import models
from company.models import Subscription


class Payment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        company_name = getattr(self.subscription, 'company', None)
        if company_name and hasattr(company_name, 'name'):
            return f"{company_name.name} - {self.amount} {self.status}"
        return f"Payment {self.id} - {self.amount} {self.status}"
