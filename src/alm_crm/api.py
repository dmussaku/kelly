from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization
from .models import Contact
from django.conf.urls import url
from tastypie.utils import trailing_slash

class ContactResource(ModelResource):

	class Meta:
		queryset = Contact.objects.all()
		resource_name = 'contact'
		authentication = SessionAuthentication()
		authorization = Authorization()

	def prepend_urls(self):
		return [
			url(
				r"^(?P<resource_name>%s)/last_contacted%s$" % 
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('get_last_contacted'),
				name = 'api_last_contacted'
			),
			url(
				r"^(?P<resource_name>%s)/cold_base%s$" % 
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('get_cold_base'),
				name = 'api_cold_base'
			),
			url(
				r"^(?P<resource_name>%s)/leads%s$" % 
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('get_leads'),
				name = 'api_leads'
			),
			url(
				r"^(?P<resource_name>%s)/search%s$" % 
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('search'),
				name = 'api_search'
			),
		]
	'''
	receives a queryset and returns a list of bundles
	'''
	def get_bundle_list(self,obj_list,request):
		objects=[]
		for obj in obj_list:
			bundle = self.build_bundle(obj=obj, request=request)
			bundle = self.full_dehydrate(bundle)
			objects.append(bundle)
		return objects

	def get_last_contacted(self, request, **kwargs):
		contacts = Contact().get_contacts_by_last_activity_date(request.user.id)
		return self.create_response(
				request, {'objects':self.get_bundle_list(contacts,request)}
			)

	def get_cold_base(self, request, **kwargs):
		contacts = Contact().get_cold_base()
		return self.create_response(
				request, {'objects':self.get_bundle_list(contacts,request)}
			)

	def get_leads(self, request, **kwargs):
		contacts = Contact().get_contacts_by_status(1,20)
		return self.create_response(
				request, {'objects':self.get_bundle_list(contacts,request)}
			)
	'''
	Api implementation of search, pass search_params in this format:
	[('fn', 'startswith'), ('org__organization_unit', 'icontains'), 'bday']
	'''
	def search(self, request, **kwargs):
		query = request.GET.get('query','')
		search_params = request.GET.get('search_params','')
		contacts = Contact().filter_contacts_by_vcard(query,search_params)
