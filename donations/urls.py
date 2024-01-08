from django.urls import path, include
from .views import (
    send_otp,
    verify_otp_and_generate_token,
    update_payment_gateway,
    donate_amount,
    success_checkout,
    cancel_checkout,
    get_donation_data,
    update_payment_status,
    donation_chart,
)

urlpatterns = [
    path("send_otp/", send_otp, name="send_otp"),
    path("verify_otp/", verify_otp_and_generate_token, name="verify_otp"),
    path(
        "update_payment_gateway/", update_payment_gateway, name="update_payment_gateway"
    ),
    path("donate_amount/", donate_amount, name="donate_amount"),
    path("get_donation_data/", get_donation_data, name="get_donation_data"),
    path("update_payment_status/", update_payment_status, name="update_payment_status"),
    path("donation_chart/", donation_chart, name="donation_chart"),
    path("success/", success_checkout, name="success_checkout"),
    path("cancel/", cancel_checkout, name="cancel_checkout"),
]
