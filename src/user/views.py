from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.template.response import TemplateResponse

from user.models import User


class UserListView(ListView):
    pass

class UserProfileView(TemplateView):
	"""
	Shows users profile info
	"""

	# should be:
	# user = request.user

	def get_context_data(self, **kwargs):
		ctx = super(UserProfileView, self).get_context_data(**kwargs)
		# should be:
		# kwargs['user'] = self.request.user
		ctx['user'] = User.objects.get(id=1)
		return ctx

def user_profile_settings():
	pass
