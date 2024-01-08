from django.contrib import admin
from .models import User, OtpValidate, DonationType


admin.site.register(User)
admin.site.register(OtpValidate)
admin.site.register(DonationType)
