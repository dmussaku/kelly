from django.db import models

class SerializerOptions(dict):
    """
    Options for API extensions
    """
    # Used in get_api_choices(), and _get_api_data()
    api_model = None

    # Each field named here is turned in to a @property, which calls the API
    # when accessed
    api_fields = []

    def __init__(self, klass_name, opts):
        """
        Set any options provided, replacing the default values
        """
        self._options_of = klass_name
        if opts:
            for key, value in opts.__dict__.iteritems():
            	self[key] = value
                setattr(self, key, value)

    def __unicode__(self):
    	return u"Options for %s" % self._options_of


class SerializerOptionsMetaclass(models.base.ModelBase):

	def __new__(mcs, name, bases, attrs):
		new = super(SerializerOptionsMetaclass, mcs).__new__(mcs, name, bases, attrs)
		opts = attrs.pop('SerializerMeta', None)
		setattr(new, '_ser_meta', SerializerOptions(name, opts))
		return new


class SerializableModel(models.Model):
	__metaclass__ = SerializerOptionsMetaclass

	class Meta:
		abstract = True