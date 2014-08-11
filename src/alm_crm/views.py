from django.views.generic import ListView
from alm_user.models import User
from almanet.models import Product, Subscription

class UserProductView(ListView):
	template_name = 'crm/dashboard.html'

	def get_context_data(self, **kwargs):
		context = super(UserProductView, self).get_context_data(**kwargs)
		context['user'] = User.objects.get(id=self.request.user.id)
		p = Product.filter(slug=kwargs['slug'])
		u = self.request.user
		if (kwargs['slug'] != None and p):
			subscr = u.get_active_subscriptions().filter(product__slug=kwargs['slug'])
			if subscr:
				context['product'] = subscr.product
		return context