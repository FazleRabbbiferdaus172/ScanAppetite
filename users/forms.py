from django.contrib.auth.forms import UserCreationForm
from django.forms import forms, ModelForm, TimeInput

from .models import CustomUser, Profile

class CustomerRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email')

class VendorProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['certificate']

class VendorRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email')


class CustomerProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = []


class StoreProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = [
            'certificate', 
            'store_open_time', 
            'store_close_time', 
            'bank_account_number', 
            'bank_routing_number',
            'timezone'
        ]
        widgets = {
            'store_open_time': TimeInput(attrs={'type': 'time'}),
            'store_close_time': TimeInput(attrs={'type': 'time'}),
        }