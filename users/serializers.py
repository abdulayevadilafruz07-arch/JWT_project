from django.db.models import Q
from rest_framework import serializers, status
from .models import CodeVerify, CustomUser, VIA_EMAIL, VIA_PHONE, CODE_VERIFY, DONE
from rest_framework.exceptions import ValidationError
from shared.utility import check_email_or_phone


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

        # Parollarni tekshirish
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
        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.username = validated_data.get('username')
        instance.password.set_password = (validated_data.get('password'))
        if instance.auth_status != CODE_VERIFY:
            raise ValidationError({"message":"siz hali tasdiqlanmagansiz",'status_code':status.HTTP_400_BAD_REQUEST})
        instance.auth_status=DONE
        instance.save()
        return instance

    # def update(self, instance, validated_data):
    #
    #     if instance.auth_status != CODE_VERIFY:
    #         raise ValidationError({
    #             "message": "Siz hali tasdiqlanmagansiz",
    #             "status_code": status.HTTP_400_BAD_REQUEST
    #         })
    #
    #     instance.first_name = validated_data.get('first_name')
    #     instance.last_name = validated_data.get('last_name')
    #     instance.username = validated_data.get('username')
    #
    #     password = validated_data.get('password')
    #     instance.set_password(password)
    #
    #     instance.auth_status = DONE
    #     instance.save()
    #
    #     return instance