import re
from rest_framework import status
from rest_framework.exceptions import ValidationError

email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
phone_regex = re.compile(r'^998([378]{2}|(9[013-57-9]))\d{7}$')

def check_email_or_phone(user_input):
    if re.fullmatch(email_regex, user_input):
        data = 'email'
    elif re.fullmatch(phone_regex, user_input):
        data = 'phone'
    else:
        response = {
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Phone or email address not valid"
        }
        raise ValidationError(response)

    return data