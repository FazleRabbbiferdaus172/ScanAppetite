from django import forms
from .models import Meal

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        # The vendor is set automatically, so we don't include it in the form
        fields = ['name', 'description', 'price', 'image']