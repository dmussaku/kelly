from django.views.generic import ListView
from django.views.generic.edit import CreateView
from alm_user.models import User
from django.core.urlresolvers import reverse_lazy

class UserListView(ListView):
    pass


class UserRegistrationView(CreateView):
	model=User
	fields=['first_name','last_name','email', 'password']
	success_url=reverse_lazy('list')
	template_name='user/user_registration.html'



