from rest_framework import viewsets, permissions
from rest_framework.decorators import list_route
from rest_framework.response import Response

from django.contrib.contenttypes.models import ContentType
from alm_crm.serializers import (
    CustomFieldSerializer,
    ProductSerializer,
    ContactSerializer,
    )
from alm_crm.models import (
    CustomField,
    Product,
    Contact,
    )

from . import CompanyObjectAPIMixin

class CustomFieldViewSet(CompanyObjectAPIMixin, viewsets.ModelViewSet):
    
    serializer_class = CustomFieldSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return CustomField.objects.filter(company_id=self.request.company.id)

    def get_for_model(self, request, **kwargs):
        'at django rest framework get_for_model'
        try:
            content_type = ContentType.objects.get(app_label='alm_crm', model=kwargs.get("class", ""))
        except ContentType.DoesNotExist:
            return http.HttpNotFound()
        else:
            objects = CustomField.objects.filter(company_id=request.company.id,
                                                content_type=content_type)

        return Response([self.serializer_class(obj).data for obj in objects])

    @list_route(methods=['post'], url_path='bulk_edit')
    def bulk_edit(self, request, **kwargs):
        data = request.data
        fields_set = []
        content_class = data['content_class']
        changed_objects = []

        for object in data['custom_fields']:
            try:
                field = CustomField.objects.get(id=object.get('id', -1))
            except CustomField.DoesNotExist:
                field = CustomField()
            finally:
                field.title = object['title']
                field.content_type = ContentType.objects.get(app_label="alm_crm", model=content_class)
                field.company_id = request.company.id
                field.save()
                fields_set.append(field)

        for field in CustomField.objects.filter(company_id=request.company.id,
                                                content_type=ContentType.objects.get(app_label="alm_crm", model=content_class)):
            if field not in fields_set:
                if field.values.all().count() != 0:
                    for field_value in field.values.all():
                        if content_class.lower() == "contact":
                            if field_value.content_object not in changed_objects:
                                vcard_note = Note(vcard=field_value.content_object.vcard, data='')
                            else:
                                vcard_note = field_value.content_object.vcard.note_set.last()
                            vcard_note.data += field.title+': '+field_value.value+'\n'
                            vcard_note.save()
                        changed_objects.append(field_value.content_object)
                        field_value.delete()
                field.delete()

        changed_objects_bundle = []

        if content_class.lower() == "product":
            changed_objects_bundle = [ProductSerializer(obj).data for obj in changed_objects]
        elif content_class.lower() == "contact":
            changed_objects_bundle = [ContactSerializer(obj).data for obj in changed_objects]

        bundle = {'content_class': content_class,
                    'custom_fields': [self.serializer_class(field).data for field in fields_set],
                    'changed_objects': changed_objects_bundle}

        return Response(bundle)

    @list_route(methods=['get'], url_path='get_for_model/contact')
    def get_for_model_contact(self, request, **kwargs):
        return self.get_for_model(request, **{'class':'contact'})

    @list_route(methods=['get'], url_path='get_for_model/product')
    def get_for_model_product(self, request, **kwargs):
        return self.get_for_model(request, **{'class':'product'})
    