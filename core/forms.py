from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django import forms
from .models import *


class UserRegisterForm(UserCreationForm):

	email = forms.EmailField(widget = forms.TextInput(attrs = {
		'type' : 'text',
		'placeholder' : 'Email address'
	}), max_length = 100)

	username = forms.CharField(widget = forms.TextInput(attrs = {
		'type' : 'text',
		'placeholder' : 'Your Name'
	}), max_length = 100)

	password1 = forms.CharField(widget = forms.PasswordInput(attrs = {
		'type': 'password',
		'placeholder' : 'Password'
	}), max_length = 100)

	password2 = forms.CharField(widget = forms.PasswordInput(attrs = {
		'type': 'password',
		'placeholder' : 'Confirm your password'
	}), max_length = 100)

	class Meta:
		model = User

		fields = ['email', 'username', 'password1', 'password2'] 

class ProfileUpdateForm(forms.ModelForm):
	class Meta:
		model = Profile

		profile_photo = forms.ImageField(widget = forms.FileInput(attrs = {
			'type': 'file',
			'class' : 'profile_photo_browse',
			'name' : 'profile_photo',
		}))

		fields = ['profile_photo']