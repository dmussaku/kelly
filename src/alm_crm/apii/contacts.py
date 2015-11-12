from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets, status

from alm_vcard.serializers import VCardSerializer
from alm_vcard.models import VCard

from rest_framework import filters
from alm_crm.filters import ContactFilter


from alm_crm.serializers import ContactSerializer
from alm_crm.models import Contact, SalesCycle, Share

from . import CompanyObjectAPIMixin


class ContactViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = ContactSerializer
    # pagination_class = None
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ContactFilter

    def get_queryset(self):
        return Contact.objects.filter(company_id=self.request.company.id).order_by('vcard__fn')

    def list(self, request, *args, **kwargs):
        query_params = request.query_params
        if(query_params.has_key('ids')):
            self.pagination_class = None
            ids = query_params.get('ids', None).split(',') if query_params.get('ids', None) else []
            queryset = self.filter_queryset(self.get_queryset())
            queryset = queryset.filter(id__in=ids)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return super(ContactViewSet, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
    	data = request.data
    	company_id = request.company.id

    	# create vcard for contact
    	vcard_data = data.pop('vcard')
    	vcard_serializer = VCardSerializer(data=vcard_data)
        vcard_serializer.is_valid(raise_exception=True)
        vcard = vcard_serializer.save()

        # save contact
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        contact = self.perform_create(serializer, vcard=vcard)

        # create global sales_cycle for this contact
        SalesCycle.create_globalcycle(
                    **{
                     'company_id': company_id,
                     'owner_id': request.user.id,
                     'contact_id': contact.id
                    }
                )

        # create parent if neccessary
        parent_name = data.get('company_name','').strip()
        if parent_name:
            contact, parent = contact.create_company_for_contact(parent_name)

        headers = self.get_success_headers(serializer.data)
        serializer = self.get_serializer(contact, 
        								 global_sales_cycle=True,
        								 parent=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
    	data = request.data

    	# update vcard for contact
    	vcard = instance.vcard
    	if vcard:
    		vcard.delete()
    	vcard_data = data.pop('vcard')
    	vcard_serializer = VCardSerializer(data=vcard_data)
        vcard_serializer.is_valid(raise_exception=True)
        vcard = vcard_serializer.save()

        # save contact
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save(vcard=vcard)

        # create parent if neccessary
        parent_name = data.get('company_name','').strip()
        if parent_name:
            contact, parent = contact.create_company_for_contact(parent_name)

        serializer = self.get_serializer(contact, 
        								 parent=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)

    @list_route(methods=['post'], url_path='delete_contacts')
    def delete_contats(self, request, *args, **kwargs):
        obj_ids = request.data.get('ids', [])
        objects = Contact.delete_contacts(obj_ids)
        return Response(objects)

    @list_route(methods=['get'], url_path='state')
    def get_cached_state(self, request, *args, **kwargs):	
    	contact_ids = self.get_queryset().values_list('id', flat=True)
    	return Response(Contact.get_by_ids(*contact_ids))

    @list_route(methods=['get'], url_path='statistics')
    def get_statistics(self, request, *args, **kwargs):
        statistics = Contact.get_statistics(company_id=request.company.id, user_id=request.user.id)
        return Response(statistics)

    @list_route(methods=['get'], url_path='all')
    def all(self, request, *args, **kwargs): 
        queryset = Contact.get_all(company_id=request.company.id)
        contact_filter = ContactFilter(request.GET, queryset)
        contact_ids = contact_filter.qs.values_list('id', flat=True)
        return Response(contact_ids)

    @list_route(methods=['get'], url_path='recent')
    def recent(self, request, *args, **kwargs):   
        queryset = Contact.get_recent_base(
            company_id=request.company.id, user_id=request.user.id)
        contact_filter = ContactFilter(request.GET, queryset)
        contact_ids = contact_filter.qs.values_list('id', flat=True) 
        return Response(contact_ids)

    @list_route(methods=['get'], url_path='cold')
    def cold(self, request, *args, **kwargs):    
        queryset = Contact.get_cold_base(
            company_id=request.company.id, user_id=request.user.id)
        contact_filter = ContactFilter(request.GET, queryset)
        contact_ids = contact_filter.qs.values_list('id', flat=True) 
        return Response(contact_ids)

    @list_route(methods=['get'], url_path='lead')
    def lead(self, request, *args, **kwargs):    
        queryset = Contact.get_lead_base(
            company_id=request.company.id, user_id=request.user.id)
        contact_filter = ContactFilter(request.GET, queryset)
        contact_ids = contact_filter.qs.values_list('id', flat=True) 
        return Response(contact_ids)

