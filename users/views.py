from django.shortcuts import render

from rest_framework.generics import CreateAPIView
from rest_framework import permissions
from .serializers import SignupSerializer
from .models import CustomUser

class SignUpView(CreateAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignupSerializer
    queryset = CustomUser
