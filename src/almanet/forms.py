from django.forms import ModelForm
from models import Product
from alm_crm.models import Value


class ProductCreateForm(ModelForm):

	class Meta:
		model = Product
		fields = ['title', 'description']


class ValueCreateForm(ModelForm):

	class Meta:
		model = Value
		field = ['salary', 'amount', 'currency']