from alm_crm.models import (
    Contact,
    Product, 
    CustomField,
    CustomFieldValue
    )

def processing_custom_field_data(custom_fields_data, content_object):
    content_object.custom_field_values.clear()
    for field_id, field_value in custom_fields_data.iteritems():
        custom_field_value = CustomFieldValue.build_new(field = CustomField.objects.get(id=field_id),
                                                        value=field_value, 
                                                        object_id=content_object.id, 
                                                        save=True)
