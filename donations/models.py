from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None):
        if not phone:
            raise ValueError("User must have a phone number")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(phone=phone)
        user.set_password(password)
        user.is_staff = False
        user.is_admin = False
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None):
        user = self.create_user(phone, password=password)
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


PAYMENT_GATEWAY = [
    ("Stripe_payment", "Stripe_payment"),
    ("Razorpay_payment", "Razorpay_payment"),
]


class User(AbstractBaseUser):
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,14}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed.",
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_gateway = models.CharField(
        max_length=50, choices=PAYMENT_GATEWAY, default="Stripe_payment"
    )

    USERNAME_FIELD = "phone"
    objects = CustomUserManager()

    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class OtpValidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)

    def __str__(self) -> str:
        return super().__str__()


class DonationType(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    donation_type = models.CharField(max_length=999999)
    amount = models.FloatField(default=0)
    status = models.CharField(max_length=999999, default="Pending")
    date = models.DateField(default=timezone.now)

    def __str__(self) -> str:
        return self.user.phone
