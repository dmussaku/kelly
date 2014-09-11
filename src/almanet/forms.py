from django.forms import ModelForm
from models import Service



class ServiceCreateForm(ModelForm):

	class Meta:
		model = Service
		fields = ['title', 'description']


