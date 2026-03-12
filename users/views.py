from django.shortcuts import render

from rest_framework.generics import CreateAPIView
from rest_framework import permissions,status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
from .serializers import SignupSerializer, UserPhotoStatusSerializer,UserChangeInfoSerializer,LoginSerializer
from .models import CustomUser, NEW, DONE, CODE_VERIFY, PHOTO_DONE, VIA_EMAIL, VIA_PHONE
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView
from .serializers import UserChangeInfoSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class SignUpView(CreateAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignupSerializer
    queryset = CustomUser.objects.all()

class CodeVerifyView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    def post(self, request):
        user=request.user
        code=self.request.data.get('code')

        codes=user.verify_codes.filter(code=code, expiration_time__gte=datetime.now(),is_active=False)
        if not codes.exists():
            raise ValidationError({"message":'Kodingiz xato yoki eskirgan','status':status.HTTP_400_BAD_REQUEST})
        else:
            codes.update(is_active=True)
        if user.auth_status==NEW:
            user.auth_status=CODE_VERIFY
            user.save()
        response_data = {
            "message":'kod tasdiqlandi',
            "status":status.HTTP_200_OK,
            'access':user.token()['access'],
            'refresh':user.token()['refresh'],
        }
        return Response(response_data)

class GetNewCodeView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    def get(self, request):
        user=request.user
        code = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_active=False)
        if code.exists():
            raise ValidationError({"message": 'Sizda hali active kod bor', 'status': status.HTTP_400_BAD_REQUEST})
        else:
            if user.auth_type==VIA_EMAIL:
                code=user.generate_code(VIA_EMAIL)
                print(code,'|||||||||')
            elif user.auth_type== VIA_PHONE:
                code=user.generate_code(VIA_PHONE)
                print(code,'||||||||||')

        response_data = {
            "message":'kod yuboroldi',
            "status":status.HTTP_201_CREATED,
        }
        return Response(response_data)



class UserChangeInfoView(UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request):
        user=request.user
        serializer = UserChangeInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=user, validated_data=serializer.validated_data)
        response={
            'message':'malumot qoshildi',
            'status':status.HTTP_200_OK,
            'access':user.token(['access']),
            'refresh':user.token(['refresh'])
        }
        return Response(response)


class UserChangePhotoView(UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request):
        user = request.user
        serializer = UserPhotoStatusSerializer(data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=user, validated_data=serializer.validated_data)
        response = {
            'message': 'rasm qoshildi',
            'status': status.HTTP_200_OK,
            'access': user.token(['access']),
            'refresh': user.token(['refresh'])
        }
        return Response(response)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer