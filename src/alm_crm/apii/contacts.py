import base64

from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework import viewsets, status, filters

from alm_vcard.serializers import VCardSerializer
from alm_vcard.models import VCard
from alm_crm.filters import ContactFilter
from alm_crm.serializers import (
    ContactSerializer,
    ContactListSerializer,
    SalesCycleSerializer,
)
from alm_crm.models import (
    Contact,
    ImportTask, 
    SalesCycle, 
    Share,
    )
from alm_crm.tasks import (
    grouped_contact_import_task, 
    check_task_status,
)
from alm_crm.utils.data_processing import (
    processing_custom_field_data,
    )

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
            serializer = self.get_serializer(queryset, children=True, parent=True, many=True)
            return Response(serializer.data)
        return super(ContactViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, products=True, children=True, parent=True, global_sales_cycle=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
    	data = request.data
    	company_id = request.company.id

    	# create vcard for contact
    	vcard_data = data.pop('vcard')
        custom_fields = data.pop('custom_fields') if data.get('custom_fields') else {}
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

        if custom_fields:
            processing_custom_field_data(custom_fields, contact)

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
        custom_fields = data.pop('custom_fields') if data.get('custom_fields') else {}
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
        if custom_fields:
            processing_custom_field_data(custom_fields, contact)
        serializer = self.get_serializer(contact,
                                         products=True,
                                         
                                         children=True, 
                                         parent=True, 
                                         global_sales_cycle=True)
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

    @detail_route(methods=['get'], url_path='sales_cycles')
    def sales_cycles(self, request, *args, **kwargs):
        contact = self.get_object()
        sales_cycles = SalesCycleSerializer(contact.sales_cycles.all(), many=True)

        include_children = request.query_params.get('include_children', False)
        if include_children:
            children = ContactSerializer(contact.children.all(), sales_cycles=True, many=True)

            return Response({
                'sales_cycles': sales_cycles.data,
                'children': children.data,
            })
        return Response({
            'sales_cycles': sales_cycles.data,
        })

    @list_route(methods=['post'], url_path='import')
    def import_contacts(self, request, **kwargs):
        objects = []
        data = request.data
        decoded_string = base64.b64decode(data['uploaded_file'])
        filename_chunks = data['filename'].split('.')
        filename = filename_chunks[len(filename_chunks)-1]
        if filename=='xls' or filename=='xlsx':
            xls_meta = Contact.get_xls_structure(data['filename'], decoded_string)
            xls_meta['type'] = 'excel'
            return Response(xls_meta)
        return Response({'success': False})

    @list_route(methods=['post'], url_path='import_from_structure')
    def import_from_structure(self, request, **kwargs):
        data = request.data
        col_structure = data.get('col_structure')
        filename = data.get('filename')
        contact_list_name = data.get('contact_list_name')
        ignore_first_row = data.get('ignore_first_row', False)
        if not col_structure or not filename:
            return Response(
                    {'success':False, 'message':'Invalid parameters'})
        """
        col structure:
        {0:'Adr__postal', 1:'VCard__fn', 2:'Adr__home', 3:'Org', 4:'Nickname'}
        """
        col_hash = []
        for key, value in col_structure.viewitems():
            obj_dict = {'num':key}
            obj_dict['model'] = value.split('__')[0]
            if len(value.split('__'))>1:
                obj_dict['attr'] = value.split('__')[1]
            col_hash.append(obj_dict)
        import_task_id = grouped_contact_import_task(
            col_hash, filename, contact_list_name, request.user, request.company.id, request.user.email, ignore_first_row)
        return Response(
                {'success':True,'task_id':import_task_id}
            )

    @list_route(methods=['get'], url_path='check_import_status')
    def check_import_status(self, request, **kwargs):
        objects = []
        # self.method_check(request, allowed=['get'])
        # self.is_authenticated(request)
        # self.throttle_check(request)
        task_id = request.GET.get('task_id', "")
        if not task_id:
            return Response(
                {'success':False, 'message':'No task was entered'})
        if not check_task_status(task_id):
            return Response(
                {'success':False, 'status':'PENDING'})
        try:
            import_task = ImportTask.objects.get(uuid=task_id)
        except ObjectDoesNotExist:
            return Response(
                {'success':False, 'message':'The task with particular id does not exist'})
        contacts = import_task.contacts.all()
        contact_list = import_task.contactlist
        contact_list_data = ContactListSerializer(
            contact_list).data
        imported_num = import_task.imported_num
        not_imported_num = import_task.not_imported_num
        email_sent = True if not_imported_num != 0 else False
        import_task.delete()
        
        return Response({
            'success':True, 
            'status':'FINISHED', 
            'contact_list': contact_list_data,
            'imported_num':imported_num, 
            'not_imported_num':not_imported_num, 
            'email_sent':email_sent
        })

    @list_route(methods=['post'], url_path='contacts_merge')
    def contacts_merge(self, request, **kwargs):
        """
        POST METHOD
        example
        {"merged_contacts":[1,2,3], "merge_into_contact":1, "delete":True/False}
        """
        data = request.data
        merged_contacts_ids = data.pop("merged_contacts", [])
        merge_into_contact_id = data.pop("merge_into_contact", "")
        delete_merged = merged_contacts_ids
        if not merged_contacts_ids or not merge_into_contact_id:
            return Response(
                {'success':False, 'message':'Contact ids have not been appended'})
        try:
            primary_object = Contact.objects.get(id=merge_into_contact_id)
        except ObjectDoesNotExist:
            return Response({
                        'success':False,
                        'message':'Contact with %s id doesnt exist' % merge_into_contact_id
                        }
                    )
        alias_objects = Contact.objects.filter(id__in=merged_contacts_ids)
        # response = primary_object.merge_contacts(alias_objects, delete_merged)
        # if not response['success']:
        #     return Response(response)
        # contact = response['contact']
        contact = primary_object.merge_contacts(alias_objects=alias_objects, delete_merged=delete_merged, **data)
        serializer = self.get_serializer(contact, 
                                         global_sales_cycle=True,
                                         parent=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='contact_dict')
    def contact_dict(self, request, **kwargs):
        tp = request.GET.get('tp','user')
        contact_dict = Contact.objects.filter(
            company_id=request.company.id, tp=tp).values_list('id', 'vcard__fn')
        return Response(contact_dict)
