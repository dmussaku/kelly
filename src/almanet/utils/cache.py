from django.conf import settings


def build_key(prefix, key):
	return "{}::{}".format(prefix, key)

def extract_id(key, coerce=str):
	return coerce(key.split('::')[1])