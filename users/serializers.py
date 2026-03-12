from django.db.models import Q
from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import CodeVerify, CustomUser, VIA_EMAIL, VIA_PHONE, CODE_VERIFY, DONE, PHOTO_DONE
from rest_framework.exceptions import ValidationError
from shared.utility import check_email_or_phone, check_email_or_phone_or_username


class SignupSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_status = serializers.CharField(read_only=True)
    auth_type = serializers.CharField(read_only=True)

    def __init__(self, instance=None, **kwargs):
        super().__init__(instance, **kwargs)
        self.fields['email_or_phone']= serializers.CharField(write_only=True, required=True)


    class Meta:
        model = CustomUser
        fields = ('id', 'auth_status', 'auth_type')


    def create(self, validated_data):
        user=super().create(validated_data)
        if user.auth_type==VIA_EMAIL:
            code=user.generate_code(VIA_EMAIL)
            print(code,'||||||||||||||||||')
        elif user.auth_type==VIA_PHONE:
            code=user.generate_code(VIA_PHONE)
            print(code,'||||||||||||||||||')
        else:
            raise ValidationError('Email yoki telefon raqami xato')
        user.save()
        return user



    def validate(self, attrs):
        super().validate(attrs)
        data=self.auth_validate(attrs)
        return data

    @staticmethod
    def auth_validate(user_input):
        user_input=user_input.get('email_or_phone')
        user_input_type = check_email_or_phone(user_input)

        if user_input_type == 'phone':
            data={
                'auth_type':VIA_PHONE,
                'phone_number':user_input
            }
        elif user_input_type == 'email':
            data={
                'auth_type':VIA_EMAIL,
                'email':user_input
            }
        else:
            response = {
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Phone or email address not valid"
            }
            raise ValidationError(response)
        return data

    def validate_email_or_phone(self, email_or_phone):
        user=CustomUser.objects.filter(Q(email=email_or_phone) | Q(phone=email_or_phone)).first()
        if user:
            raise ValidationError(detail='bu email yoki telefon raqami bilan oldin royxatdan otilgan')
        return email_or_phone




    def to_representation(self, instance):
        data=super().to_representation(instance)
        data['message']='kodingiz yuborildi'
        data['refresh']=instance.token()['refresh']
        data['access']=instance.token()['access']
        return data




class UserChangeInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if not password or not confirm_password or password != confirm_password:
            raise ValidationError({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Parollar mos emas yoki xato kiritildi'
            })

        if ' ' in password:
            raise ValidationError({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Parolda probel bo‘lmasligi kerak'
            })
        return attrs

    def validate_username(self, username):
        if len(username) < 6:
            raise ValidationError({'message': 'Username kamida 6 ta belgidan iborat bo‘lishi kerak'})
        if not username.isalnum():
            raise ValidationError({'message': 'Username faqat harf va raqamlardan iborat bo‘lishi kerak'})
        if username[0].isdigit():
            raise ValidationError({'message': 'Username raqam bilan boshlanmasligi kerak'})
        return username

    def validate_first_name(self, value):
        if len(value) < 2:
            raise ValidationError({'message': 'Ism juda qisqa'})
        if not value.isalpha():
            raise ValidationError({'message': 'Ism faqat harflardan iborat bo‘lishi kerak'})
        return value

    def validate_last_name(self, value):
        if len(value) < 2:
            raise ValidationError({'message': 'Familiya juda qisqa'})
        if not value.isalpha():
            raise ValidationError({'message': 'Familiya faqat harflardan iborat bo‘lishi kerak'})
        return value



    def update(self, instance, validated_data):

        if instance.auth_status != CODE_VERIFY:
            raise ValidationError({
                "message": "Siz hali tasdiqlanmagansiz",
                "status_code": status.HTTP_400_BAD_REQUEST
            })

        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.username = validated_data.get('username')

        password = validated_data.get('password')
        instance.set_password(password)

        instance.auth_status = DONE
        instance.save()

        return instance


class UserPhotoStatusSerializer(serializers.Serializer):
    photo=serializers.ImageField()

    def update(self,instance,validated_data):
        photo=validated_data.get['photo',None]
        if photo:
            instance.photo=photo
        if instance.auth_status== DONE:
            instance.auth_status = PHOTO_DONE
        instance.save()
        return instance




class LoginSerializer(TokenObtainPairSerializer):
    password=serializers.CharField(required=True,write_only=True)

    def __init__(self,*args,**kwargs):
        super(LoginSerializer).__init__(*args,**kwargs)
        self.fields['user_input']=serializers.CharField(required=True,write_only=True)
        self.fields['username']=serializers.CharField(read_only=True)


    def validate(self, attrs):
        data = self.check_user_type(attrs)
        return data








    @staticmethod
    def check_user_type(self,data):
        password=data.get('password')
        user_input_data=data.get('user_input')
        user_type=check_email_or_phone_or_username(user_input_data)
        if user_type=='username':
            user= CustomUser.objects.filter(username=user_input_data)
            self.get_object(user)
            username=user_input_data
        elif user_type=='email':
            user=CustomUser.objects.filter(email_icontains=user_input_data.lower())
            self.get_object(user)
            username=user.username
        elif user_type=='phone':
            user=CustomUser.objects.filter(photo_number=user_input_data)
            self.get_object(user)
            username=user.username
        else:
            raise ValidationError(detail='malumot topilmadi')

        authentication_kwargs = {
            "password": password,
            self.username_field: username
        }

        if user.auth_status not in [DONE,PHOTO_DONE]:
            raise ValidationError(detail='siz hali toliq royxatdan otmagansiz')

        user=authenticate(**authentication_kwargs)

        if not user:
            raise ValidationError(detail='login yoki parol xato')




    def get_object(user):
        if not user:
            raise ValidationError({"message": "login ni xato kiritdingiz","status": status.HTTP_400_BAD_REQUEST  })
        return True


# ChangePhoto api va login(oddiy usulda va tokenobtaion dan foydalanib, 2 xil usulda yozilsin) apilarni toliq tugatib yozish

