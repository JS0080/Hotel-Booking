from django import forms
    
class HotelSearchForm(forms.Form):
    place = forms.CharField(widget=forms.TextInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Where To', 'tabindex': 1}))
    checkin = forms.CharField(widget=forms.TextInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Check-in', 'autocomplete':'off', 'tabindex': 2}), label='Check-in')
    checkout = forms.CharField(widget=forms.TextInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Check-out', 'autocomplete':'off', 'tabindex': 3}), label='Check-out')
