from django.contrib import admin

from .models import CodeVerify,CustomUser

admin.site.register(CodeVerify)
admin.site.register(CustomUser)
