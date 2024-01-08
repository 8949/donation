import random
import string
from django.utils.text import slugify
from twilio.rest import Client
from io import BytesIO
import os
import stripe
import razorpay
from django.conf import settings


def generate_random_otp():
    otp = random.randint(999, 9999)
    return otp


def send_otp_via_twilio(phone_number, otp):
    # Initialize Twilio client with your Twilio account SID and authentication token
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    # Send OTP message
    message = client.messages.create(
        body=f"Your OTP is: {otp}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number,
    )

    return message.sid if message.sid else None


def pay_with_strip(price, product_name, success_url, cancel_url):
    print("YEHHH STRIPE IS CALLED .", price, product_name)
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": product_name,
                        },
                        "unit_amount": price,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url or "http://localhost:8000/api/success/",
            cancel_url=cancel_url or "http://localhost:8000/api/cancel/",
        )

        print("checkout_session :", checkout_session)
        context = {
            "payment_url": "https://buy.stripe.com/test_bIY28n3ejgyxbBK9AA",
            "payment_page": checkout_session.get("url"),
        }
        return context
    except Exception as e:
        print("ERROR ::", e)
        return False


def pay_with_razorpay(price, product_name, success_url, cancel_url):
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )
    try:
        # razorpay_order = client.order.create(
        #     {"amount": int(price) * 100, "currency": "INR", "payment_capture": "1"}
        # )
        # print("razorpay_order :", razorpay_order)
        context = {
            "payment_url": "https://razorpay.com/payment-button/pl_NLykEZP1nZfHMU/view/?utm_source=payment_button&utm_medium=button&utm_campaign=payment_button",
            "payment_page": "https://rzp.io/l/P3abGar",
        }

        return context

    except Exception as e:
        print("ERROR ::0", e)
        return False
