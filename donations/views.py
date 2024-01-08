from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from rest_framework.authtoken.models import Token
import json
from datetime import datetime
from django.conf import settings
from .utils import generate_random_otp, send_otp_via_twilio
from .models import OtpValidate, User, DonationType
from .constants import PAYMENT_GATEWAY
from functools import wraps


def error_handling_decorator(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)

        except Exception as e:
            return Response(
                {
                    "message": "Internal Server Error",
                    "error": f"An error occurred: {e}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return wrapper


@api_view(["POST"])
@permission_classes([AllowAny])
@error_handling_decorator
def send_otp(request):
    """Send Otp to Phone

    Args:
        request (phone): Valid phone number for get otp.

    Returns:
        success/failed message
    """

    phone_number = request.data.get("phone_number")
    otp = generate_random_otp()

    user_obj = User.objects.filter(phone=phone_number).first()
    if not user_obj:
        user_obj = User()
        user_obj.phone = phone_number
        user_obj.save()

    otp_validate_obj = OtpValidate.objects.filter(user__id=user_obj.id).first()
    if otp_validate_obj:
        otp_validate_obj.otp = otp
        otp_validate_obj.save()
    else:
        otp_validate_obj = OtpValidate()
        otp_validate_obj.user = user_obj
        otp_validate_obj.otp = otp
        otp_validate_obj.save()

    sid = send_otp_via_twilio(phone_number, otp)

    if sid:
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"message": "Failed to send OTP"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
@error_handling_decorator
def verify_otp_and_generate_token(request):
    """Verify OTP for the Phone number.

    Args:
        phone: Valid phone number for get otp,
        otp: OTP user get on provided phone number.

    Returns:
        success/failed message
    """
    phone_number = request.data.get("phone_number")
    otp_entered = str(request.data.get("otp"))

    user = User.objects.get(phone=phone_number)
    user_otp = OtpValidate.objects.filter(user__id=user.id).first()
    stored_otp = user_otp.otp
    if stored_otp == otp_entered:
        token, created = Token.objects.get_or_create(user=user)
        user.password = token.key
        user.save()
        print("token ::", token.key)

        return Response({"token": token.key}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"message": "OTP verification failed"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@error_handling_decorator
def update_payment_gateway(request, format=None):
    """Choose payment Gateway method.

    Args:
        payment_method (string, required): The payment method

    Returns:
        success/failed message
    """

    payment_method = request.data.get("payment_method")
    user = User.objects.filter(id=int(request.user.id)).first()
    user.payment_gateway = payment_method
    user.save()
    content = {
        "message": f"User payment gateway is update to :{user.payment_gateway} ",
    }
    return Response(content, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
@error_handling_decorator
def success_checkout(request):
    return render(request, "success.html")


@api_view(["GET"])
@permission_classes([AllowAny])
@error_handling_decorator
def cancel_checkout(request):
    return render(request, "cancel.html")


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@error_handling_decorator
def get_donation_data(request, format=None):
    """Get Donation History

    Args:
        from (string): The start date for the donation data retrieval.
        to (string): The end date for the donation data retrieval.

    Returns:
       Get list of donation data.
    """

    user = User.objects.filter(id=int(request.user.id)).first()
    from_date = request.data.get("from")
    to_date = request.data.get("to")
    donation_type_obj = DonationType.objects.filter(
        user__id=user.id, date__range=[from_date, to_date]
    )
    donation_data = [
        {
            "id": data.id,
            "donation_type": data.donation_type,
            "amount": data.amount,
            "date": data.date,
            "status": data.status,
        }
        for data in donation_type_obj
    ]
    return Response(donation_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@error_handling_decorator
def update_payment_status(request, format=None):
    """Update payment status based of the payment status

    Args:
        donation_type_id (string): The ID of the donation type for which the payment status needs to be updated.
        payment_status (string): The new payment status to be set for the donation.

    Returns:
        success/failed message.
    """

    id = request.data.get("donation_type_id")
    payment_status = request.data.get("payment_status")

    donation_type_obj = DonationType.objects.get(id=int(id))
    print("donation_type_obj ::", donation_type_obj)
    if not donation_type_obj:
        content = {
            "message": "Id is not valid !!!!",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    donation_type_obj.status = payment_status
    donation_type_obj.save()
    content = {
        "message": f"Payment status is updated to :{payment_status} ",
    }
    return Response(content, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@error_handling_decorator
def donate_amount(request, format=None):
    """Donate Amount of your choice

    Args:
        donation_type (string, required): The type of donation.
        amount (number, required): The donation amount.

    Returns:
        Link for checkout session.
    """

    donation_type = request.data.get("donation_type")
    amount = request.data.get("amount")
    success_url = request.data.get("success_url")
    cancel_url = request.data.get("cancel_url")

    user = User.objects.filter(id=int(request.user.id)).first()
    payment_gateway_obj = PAYMENT_GATEWAY.get(user.payment_gateway)
    if not payment_gateway_obj:
        content = {
            "message": f"Please update payment gateway method for :{user.phone} ",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    payment_res = payment_gateway_obj(amount, donation_type, success_url, cancel_url)

    if not payment_res:
        content = {
            "message": f"Unable to do Payment, Please try again or update the payment method !!!! ",
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    donation_type_obj = DonationType()
    donation_type_obj.donation_type = donation_type
    donation_type_obj.user = request.user
    donation_type_obj.amount = int(amount)
    donation_type_obj.save()

    return Response(payment_res, status=status.HTTP_200_OK)


@error_handling_decorator
def donation_chart(request):
    donations = [
        {"id": 10, "donation_type": "education", "amount": 2500.0, "status": "success"},
        {"id": 11, "donation_type": "xyz", "amount": 2500.0, "status": "Pending"},
    ]

    return render(request, "donation_chart.html", {"donations": json.dumps(donations)})
