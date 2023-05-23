from django import forms

class NetworkForm(forms.Form):
    user_image = forms.ImageField(required=False, label='Your pictrue')