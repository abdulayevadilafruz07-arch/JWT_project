from rest_framework import serializers, status
from .models import CodeVerify, CustomUser, VIA_EMAIL,VIA_PHONE
from rest_framework.exceptions import ValidationError
from shared.utility import check_email_or_phone


class SignupSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_status = serializers.CharField(read_only=True)
    verify_type = serializers.CharField(read_only=True)

    def __init__(self):
        super().__init__()
        self.fields['email_or_phone']= serializers.CharField(write_only=True, required=True)


    class Meta:
        model = CustomUser
        fields = ('id', 'auth_status', 'verify_type')

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





