from django.views.generic import ListView
from alm_user.models import User
from almanet.models import Product, Subscription

class UserProductView(ListView):
	template_name = 'crm/dashboard.html'

	def get_context_data(self, **kwargs):
		context = super(UserProductView, self).get_context_data(**kwargs)
		context['user'] = User.objects.get(id=self.request.user.id)
		if (kwargs['slug'] != None):
			if (Product.filter(slug=kwargs['slug']) and 
				Product.get(slug=kwargs['slug']) in self.request.user.get_active_subscriptions()):
				context['product'] = Product.get(slug=kwargs['slug'])
		return context