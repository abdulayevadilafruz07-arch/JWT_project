from django.shortcuts import render

from rest_framework.generics import CreateAPIView
from rest_framework import permissions,status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
from .serializers import SignupSerializer
from .models import CustomUser, NEW, DONE, CODE_VERIFY,PHOTO_DONE
from rest_framework.exceptions import ValidationError


class SignUpView(CreateAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignupSerializer
    queryset = CustomUser

class CodeVerify(APIView):
    def post(self, request):
        user=request.user
        code=self.request.data.get('code')

        codes=user.verify_codes.filter(code=code, expiration_time_gte=datetime.now(),is_active=False)
        if not codes.exists():
            raise ValidationError({"message":'Kodingiz xato yoki eskirgan','status':status.HTTP_400_BAD_REQUEST})
        else:
            codes.update(is_active=True)
        if user.auth_status==NEW:
            user.auth_status=CodeVerify
            user.save()
        response_data = {
            "message":'kod tasdiqlandi',
            "status":status.HTTP_200_OK,
            'access':user.token()['access'],
            'refresh':user.token()['refresh'],
        }
        return Response(response_data)
