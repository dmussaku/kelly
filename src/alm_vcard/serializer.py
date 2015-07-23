import inspect
import sys
from django.db.models import Model
from alm_vcard import models
from preserialize.serialize import serialize
from almanet.utils.metaprogramming import SerializableModel

def is_target(obj):
	return (
		inspect.isclass(obj) and
		issubclass(obj, SerializableModel) and
		obj is not SerializableModel
	)

def vcard_rel_components():
	return inspect.getmembers(sys.modules[models.__name__], is_target)

def build_tmpl_for(vcard_comp):
	meta = vcard_comp._ser_meta
	return meta

def serialize_objs(vcards):
	comps = vcard_rel_components()
	related_tmpls, aliases = {}, {}
	for comp_name, comp in comps:
		key = "{}_set".format(comp._meta.model_name)
		aliases[comp._ser_meta.alias] = key
		related_tmpls[key] = build_tmpl_for(comp)
	return serialize(vcards, **{
		'fields': aliases.keys() + [':local'],
		'related': related_tmpls,
		'aliases': aliases
	})


def test():
	return serialize_objs(models.VCard.objects.first())