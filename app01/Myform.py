#! -*- coding:utf-8 -*-

from django import  forms
from django.forms import widgets
from django.core.exceptions import NON_FIELD_ERRORS,ValidationError
from app01.models import UserInfo
class UserForm(forms.Form):

    """Form组件"""
    username = forms.CharField(max_length=32,widget=widgets.TextInput(attrs={"class":"form-control","placeholder":"用户名"}),error_messages={"required":"请输入用户名"})
    email = forms.CharField(max_length=32, widget=widgets.EmailInput(attrs={"class": "form-control","placeholder":"电子邮箱"}),error_messages={"required":"请输入电子邮箱"})
    password = forms.CharField(max_length=32, widget=widgets.PasswordInput(attrs={"class": "form-control","placeholder":"密码"}),error_messages={"required":"请输入密码"})
    re_password = forms.CharField(max_length=32, widget=widgets.PasswordInput(attrs={"class": "form-control","placeholder":"确认密码"}),error_messages={"required":"请确认密码"})


    def clean_username(self):
        """用户名是否存在的校验"""
        username = self.cleaned_data.get("username")
        user = UserInfo.objects.filter(username=username).first()
        if not user:
            return username
        else:
            raise ValidationError("该用户已注册!")

    def clean(self):
        """两次密码一致性的校验"""
        password = self.cleaned_data.get("password")
        re_password = self.cleaned_data.get("re_password")
        if password and re_password:
            if password == re_password:
                return self.cleaned_data
            else:
                raise ValidationError("两次密码不一致!")
        else:
            return self.cleaned_data