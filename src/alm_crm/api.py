from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization
from .models import Contact
from django.conf.urls import url
from tastypie.utils import trailing_slash

class ContactResource(ModelResource):
	vcard = fields.ToOneField('alm_vcard.api.VCardResource','vcard', null=True, full=True)

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
	
	def get_bundle_list(self,obj_list,request):
		'''
		receives a queryset and returns a list of bundles
		'''
		objects=[]
		for obj in obj_list:
			bundle = self.build_bundle(obj=obj, request=request)
			bundle = self.full_dehydrate(bundle)
			objects.append(bundle)
		return objects

	def get_last_contacted(self, request, **kwargs):
		'''
		pass limit, offset, owned (True by default, assigned, 
	    followed and include_activities with GET request
		'''
		limit = int(request.GET.get('limit', 20))
		offset = int(request.GET.get('offset', 0))
		include_activities = bool(request.GET.get('include_activities', False))
		owned = bool(request.GET.get('owned', True))
		assigned = bool(request.GET.get('assigned', False))
		followed = bool(request.GET.get('followed', False))
		contacts = Contact().get_contacts_by_last_activity_date(
			userd_id=request.user.id, 
			include_activities=include_activities,
			owned=owned,
			assigned=assigned,
			followed=followed, 
			limit=limit, 
			offset=offset)
		if not bool(include_activities):
			return self.create_response(
					request, {'objects':self.get_bundle_list(contacts, request)}
				)
		else:
			obj_dict={}
			obj_dict['contacts'] = self.get_bundle_list(contacts[0], request)
			obj_dict['activities'] = self.get_bundle.list(contacts[1], request)
			obj_dict['dict'] = contacts[2]
			return self.create_response(request, obj_dict) 

	def get_cold_base(self, request, **kwargs):
		'''
		pass limit and offset  with GET request
		'''
		limit = int(request.GET.get('limit',20))
		offset = int(request.GET.get('offset',0))
		contacts = Contact().get_cold_base(limit, offset)
		return self.create_response(
				request, {'objects':self.get_bundle_list(contacts,request)}
			)

	def get_leads(self, request, **kwargs):
		'''
		pass limit and offset through GET request
		'''
		STATUS_LEAD = 1
		limit = int(request.GET.get('limit',20))
		offset = int(request.GET.get('offset',0))
		contacts = Contact().get_contacts_by_status(STATUS_LEAD, limit, offset)
		return self.create_response(
				request, {'objects':self.get_bundle_list(contacts,request)}
			)

	def search(self, request, **kwargs):
		'''
		Api implementation of search, pass search_params in this format:
		[('fn', 'startswith'), ('org__organization_unit', 'icontains'), 'bday']
		will search by the beginning of fn if search_params are not provided
		ast library f-n literal_eval converts the string representation of a
		list to a python list
		pass limit and offset through GET request
		'''
		import ast
		limit = int(request.GET.get('limit',20))
		offset = int(request.GET.get('offset',0))
		search_text = request.GET.get('search_text','').encode('utf-8')
		search_params = ast.literal_eval(
			request.GET.get('search_params',"[('fn', 'startswith')]"))
		contacts = Contact().filter_contacts_by_vcard(
			search_text=search_text,
			search_params=search_params,
			limit=limit,
			offset=offset)
		return self.create_response(
				request, {'objects':self.get_bundle_list(contacts,request)}
			)
