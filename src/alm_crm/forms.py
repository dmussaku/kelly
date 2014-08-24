from models import Contact, Goal
from django import forms
from django.forms import ModelForm


class ContactForm(ModelForm):

    class Meta:
        model = Contact
        exclude = ['date_created']


class GoalForm(ModelForm):

    class Meta:
        model = Goal
        exclude = ['status', 'date_created']
