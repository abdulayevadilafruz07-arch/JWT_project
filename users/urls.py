from django.urls import path
from .views import SignUpView,CodeVerifyView,GetNewCodeView,UserChangeInfoView

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('code-verify/',CodeVerifyView.as_view()),
    path('get-new-code/', GetNewCodeView.as_view()),
    path('user-change-view/', UserChangeInfoView.as_view()),
]