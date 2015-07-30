from django.db import models
from copy import copy
from django.db.models.signals import post_save


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



def is_db_expression(value):
    try:
        # django < 1.8
        from django.db.models.expressions import ExpressionNode
        return isinstance(value, ExpressionNode)
    except ImportError:
        # django >= 1.8  (big refactoring in Lookup/Expressions/Transforms)
        from django.db.models.expressions import BaseExpression, Combinable
        return isinstance(value, (BaseExpression, Combinable))


# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django
class DirtyFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(
            reset_state, sender=self.__class__,
            dispatch_uid='{name}-DirtyFieldsMixin-sweeper'.format(
                name=self.__class__.__name__))
        reset_state(sender=self.__class__, instance=self)

    def _as_dict(self, check_relationship):
        all_field = {}

        for field in self._meta.fields:
            if field.rel:
                if not check_relationship:
                    continue

            field_value = getattr(self, field.attname)

            # If current field value is an expression, we are not evaluating it
            if is_db_expression(field_value):
                continue

            # Explanation of copy usage here :
            # https://github.com/smn/django-dirtyfields/commit/efd0286db8b874b5d6bd06c9e903b1a0c9cc6b00
            all_field[field.name] = copy(field.to_python(field_value))

        return all_field

    def get_dirty_fields(self, check_relationship=False):
        # check_relationship indicates whether we want to check for foreign keys
        # and one-to-one fields or ignore them
        new_state = self._as_dict(check_relationship)
        all_modify_field = {}

        for key, value in new_state.items():
            original_value = self._original_state[key]
            if value != original_value:
                all_modify_field[key] = original_value

        return all_modify_field

    def is_dirty(self, check_relationship=False):
        # in order to be dirty we need to have been saved at least once, so we
        # check for a primary key and we need our dirty fields to not be empty
        if not self.pk:
            return True
        return {} != self.get_dirty_fields(check_relationship=check_relationship)


def reset_state(sender, instance, **kwargs):
    # original state should hold all possible dirty fields to avoid
    # getting a `KeyError` when checking if a field is dirty or not
    instance._original_state = instance._as_dict(check_relationship=True)