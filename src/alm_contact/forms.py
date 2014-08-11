from models import Contact
from django import forms
from django.forms import ModelForm

class ContactForm(ModelForm):

    class Meta:
        model = Contact
        