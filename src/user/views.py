from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse_lazy

from user.models import User
from user.forms import UserBaseSettingsForm, UserPasswordSettingsForm

class UserListView(ListView):
    pass

class UserProfileView(TemplateView):
	"""
	Shows users profile info
	"""

	def get_context_data(self, **kwargs):
		ctx = super(UserProfileView, self).get_context_data(**kwargs)
		# should be:
		# kwargs['user'] = self.request.user
		ctx['user'] = User.objects.get(id=1)
		return ctx

class UserProfileSettings(UpdateView):
	"""
	Profile settings base view
	"""

	model = User
	form_class = UserBaseSettingsForm
	success_url = reverse_lazy('user_profile_url')

	def get_object(self, **kwargs):
		return User.objects.get(id=1)