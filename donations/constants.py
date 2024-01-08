from .utils import pay_with_strip, pay_with_razorpay


PAYMENT_GATEWAY = {
    "Stripe_payment": pay_with_strip,
    "Razorpay_payment": pay_with_razorpay,
}
