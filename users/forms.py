from django.contrib.auth.forms import UserCreationForm

from .models import User

#dejango 內置的用戶註冊表單
#class UserCreationForm(forms.ModelForm):
#    class Meta:
#        model = User   # 關聯的是 django 内置的 User 模型 auth.User
#        fields = ("username",)
#        field_classes = {'username': UsernameField}

#繼承上面的 改成自己定義的User類
class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User #users.User
        fields = ("username", )