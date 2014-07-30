from django.views.generic import ListView
from django.views.generic.edit import CreateView, FormView
from alm_user.models import User
from alm_user.forms import RegistrationForm, LoginForm
from django.core.urlresolvers import reverse_lazy
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect

class UserListView(ListView):
	def get_context_data(self, **kwargs):
		if self.request.session.test_cookie_worked():
			print "Cookie worked"
			self.request.session.delete_test_cookie()
		else:
			print "Cookie didn't work"
		return super(UserListView,self).get_context_data(**kwargs)


class UserRegistrationView(CreateView):
	form_class=RegistrationForm
	success_url=reverse_lazy('list')
	template_name='user/user_registration.html'
'''
class UserLoginView(FormView):
	form_class=LoginForm
	success_url=reverse_lazy('list')
	template_name='user/user_login.html'

	def get_context_data(self, **kwargs):
		self.request.session.set_test_cookie()
		return super(UserLoginView,self).get_context_data(**kwargs)
'''
def login(request):
	template_name='user/user_login.html'
	email=request.POST.get('email','')
	password=request.POST.get('password','')
	user = auth.authenticate(email=email, password=password)
	if user is not None and user.is_active:
		auth.login(request, user)
		return HttpResponseRedirect(reverse_lazy('list'))
	else:
		return HttpResponse("Invalid email and login")


def password_reset(request):
	template_name='user/password_reset.html'
	email=request.POST.get('email','')
	if email:
		try:
			u=User.objects.get(email=email)
			#make a user reset the password
		except:
			return HttpResponse("A user with input email doesn't exist")


