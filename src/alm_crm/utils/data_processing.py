from alm_crm.models import (
	Product, 
	CustomField,
	CustomSection,
	)
from alm_vcard.models import VCard

def processing_custom_section_data(custom_sections_data, content_object):
    for section_data in custom_sections_data:
    	custom_section = CustomSection.build_new( title=section_data.get('title', None), 
	    										content_class=content_object.__class__, 
	    										object_id=content_object.id, save=True)

    	if section_data.get('custom_fields', None):
	    	for field_data in section_data['custom_fields']:
	    		field = CustomField(title=field_data.get('title', None), 
	    							value=field_data.get('value', None), 
	    							section=custom_section)
	    		field.save()

def processing_custom_field_data(custom_fields_data, content_object):
    for field_data in custom_fields_data:
    	custom_field = CustomField.build_new( title=field_data.get('title', None),
    											value=field_data.get('value', None),
    											section=section, 
	    										content_class=content_object.__class__, 
	    										object_id=content_object.id, save=True)


# def from_object_to_data(content_object):
# 	return processing_object_data(content_object.custom_fields.filter(parent_field=None))

# def processing_object_data(object_data):
# 	fields_list = []
# 	for custom_field in object_data.all():
# 		field_dict = {}
# 		field_dict['title'] = custom_field.title
# 		subfields = []
# 		if custom_field.subfields:
# 			subfields = processing_object_data(custom_field.subfields.all())
# 			field_dict['subfields'] = subfields
# 		field_values = []
# 		for value in custom_field.field_values.all():
# 			values_dict = {}
# 			values_dict['value'] = value.value
# 			value_attrs = []
# 			for attr in value.field_value_attributes.all():
# 				attrs_dict = {}
# 				attrs_dict['title'] = attr.title
# 				attrs_dict['value'] = attr.value
# 				value_attrs.append(attrs_dict)
# 			values_dict['attrs'] = value_attrs
# 			field_values.append(values_dict)
# 		field_dict['field_values'] = field_values
# 		fields_list.append(field_dict)
# 	return fields_list