from models import Contact, SalesCycle, Mention
from alm_user.models import User
from django import forms
from django.forms import ModelForm


class ContactForm(ModelForm):

    class Meta:
        model = Contact
        exclude = ['date_created', 'latest_activity']
        
class SalesCycleForm(ModelForm):
	
	class Meta:
		model = SalesCycle
		exclude = ['status','date_created', 'from_date', 'to_date', 'latest_activity']

class MentionForm(ModelForm):
	
	class Meta:
		model=Mention
		exclude = ['context_type', 'context_id']
