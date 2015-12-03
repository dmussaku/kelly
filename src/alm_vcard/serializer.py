import inspect
import sys
import time
from django.db.models import Model
from django.db import connection
from preserialize.serialize import serialize
from almanet.utils.metaprogramming import SerializableModel

def is_target(obj):
	return (
		inspect.isclass(obj) and
		issubclass(obj, SerializableModel) and
		obj is not SerializableModel
	)

def vcard_rel_components():
	return inspect.getmembers(sys.modules['alm_vcard.models'], is_target)

def vcard_rel_fields():
	return [comp[1]._ser_meta.alias
	        for comp in vcard_rel_components()]

def serialize_objs(vcards):
	comps = vcard_rel_components()
	related_tmpls, aliases = {}, {}
	for i in xrange(len(comps)):
		comp_name, comp = comps[i]
		key = comp._ser_meta.alias
		aliases[key] = key
		related_tmpls[key] = comp._ser_meta
	return serialize(vcards, **{
		'fields': aliases.keys() + [':local'],
		'related': related_tmpls,
		'aliases': aliases
	})

# def test():
# 	return serialize_objs(models.VCard.objects.first())

# def stress_test():
# 	t1 = time.time()
# 	vcs = models.VCard.objects.all().prefetch_related(
# 		'tel_set', 'category_set',
# 		'adr_set', 'title_set', 'url_set',
# 		'org_set', 'email_set', 'custom_sections',
# 		'note_set')[1:1000]
# 	serialize_objs(vcs)
# 	t2 = time.time()
# 	print "Objects: {}, SQL Queries: {}, seconds: {}".format(len(vcs), len(connection.queries), (t2 - t1))