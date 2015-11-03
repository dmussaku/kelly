from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets, status

from alm_vcard.serializers import VCardSerializer
from alm_vcard.models import VCard

from alm_crm.serializers import ContactSerializer
from alm_crm.models import Contact, SalesCycle

from . import CompanyObjectAPIMixin


class ContactViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = ContactSerializer

    def get_queryset(self):
        return Contact.objects.filter(company_id=self.request.company.id)

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

    @list_route(methods=['get'], url_path='state')
    def get_cached_state(self, request, *args, **kwargs):	
    	contact_ids = self.get_queryset().values_list('id', flat=True)
    	return Response(Contact.get_by_ids(*contact_ids))
