from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator

ORDINARY_USER, ADMIN, MANAGER = ('ordinary_user', 'admin', 'manager')
NEW, CODE_VERIFY, DONE, PHOTO_DONE = ('new', 'code_verify', 'done', 'photo_done')
VIA_EMAIL, VIA_PHOTO = ('via_email', 'via_photo')


class CustomUser(AbstractUser):

    USER_ROLE = (
        (ORDINARY_USER, ORDINARY_USER),
        (ADMIN, ADMIN),
        (MANAGER, MANAGER)
    )

    USER_AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFY, CODE_VERIFY),
        (DONE, DONE),
        (PHOTO_DONE, PHOTO_DONE)
    )

    USER_AUTH_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHOTO, VIA_PHOTO)
    )

    user_role = models.CharField(
        max_length=20,
        choices=USER_ROLE,
        default=ORDINARY_USER
    )

    auth_status = models.CharField(
        max_length=20,
        choices=USER_AUTH_STATUS,
        default=NEW
    )

    auth_type = models.CharField(
        max_length=20,
        choices=USER_AUTH_TYPE
    )
    email = models.EmailField(max_length=50, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=13,unique=True, blank=True, null=True)
    photo = models.ImageField(upload_to='/user_photos/',  \
            validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png','heic'])])
