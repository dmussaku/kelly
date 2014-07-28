from django.forms import ModelForm
from user.models import User

class UserBaseSettingsForm(ModelForm):

	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'city', 'country']