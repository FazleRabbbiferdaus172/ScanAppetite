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
        fields = ['bank_account_number', 'bank_routing_number'] # Add fields here later, e.g., ['address', 'phone_number']


class StoreProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['store_open_time', 'store_close_time', 'certificate', 'bank_account_number', 'bank_routing_number']
        widgets = {
            'store_open_time': TimeInput(attrs={'type': 'time'}),
            'store_close_time': TimeInput(attrs={'type': 'time'}),
        }