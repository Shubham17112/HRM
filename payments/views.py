from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from datetime import date
import razorpay

from company.models import Subscription, SubscriptionPlan
from payments.models import Payment


# ------------------------------- Razorpay setup ----------------------------------
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


# ------------------------------- Create Razorpay Order ---------------------------
@login_required
def create_order(request, plan_id):
    """
    Step 1: User selects a plan.
    Step 2: Create Razorpay order on backend.
    Step 3: Store order + subscription + payment in DB.
    Step 4: Render template for Razorpay Checkout.
    """
    company = request.user.companies.first()

    if not company:
        messages.error(request, "No company linked with your account.")
        return redirect("company:dashboard")

    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    # Razorpay requires amount in paise (₹1 = 100 paise)
    amount = int(float(plan.price) * 100)
    currency = "INR"

    try:
        # Create a Razorpay order
        order = razorpay_client.order.create({
            "amount": amount,
            "currency": currency,
            "payment_capture": 1,  # Auto-capture after payment
            "receipt": f"order_rcptid_{company.id}_{plan.id}",
            "notes": {"plan_name": plan.name, "company": company.name},
        })
    except Exception as e:
        messages.error(request, f"Error creating Razorpay order: {e}")
        return redirect("company:subscription_error")  # optional

    # ------------------ Create subscription entry ------------------
    subscription = Subscription.objects.create(
        company=company,
        plan=plan,
        active=True,
        start_date=date.today(),
    )

    # ------------------ Create payment record ------------------
    Payment.objects.create(
        subscription=subscription,
        amount=plan.price,
        currency=currency,
        status="Pending",
        razorpay_order_id=order.get("id"),
    )

    # ------------------ Render payment page ------------------
    context = {
        "subscription": subscription,
        "order": order,
        "plan": plan,
        "company": company,
        "razorpay_key": settings.RAZORPAY_KEY_ID,  # from settings, not hard-coded
    }

    return render(request, "subscription/payment.html", context)
