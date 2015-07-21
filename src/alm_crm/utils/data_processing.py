from alm_crm.models import (
    Contact,
    Product, 
    CustomField,
    CustomFieldValue
    )

def processing_custom_field_data(custom_fields_data, content_object):
    content_object.custom_field_values.clear()
    for field_data in custom_fields_data:
        custom_field_value = CustomFieldValue.build_new(field = CustomField.objects.get(id=field_data.get('id', -1)),
                                                        value=field_data.get('value', None), 
                                                        object_id=content_object.id, 
                                                        save=True)
