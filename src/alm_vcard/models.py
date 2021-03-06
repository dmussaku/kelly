import re
# from os import *
import datetime
import json
from datetime import *
from time import *
from django.db import models, transaction as tx
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import get_models, Model
from django.db.models.signals import post_save, post_delete
from django.contrib.contenttypes.generic import GenericForeignKey
from django.core.cache import cache
from django.contrib.contenttypes.generic import GenericForeignKey

import vobject
from vobject.vcard import *
from almanet.utils.metaprogramming import SerializableModel
from almanet.utils.cache import build_key, extract_id
from almanet.utils.json import date_handler
from .serializer import serialize_objs, vcard_rel_fields

class VObjectImportException(Exception):
    message = _("The vCard could not be converted into a vObject")


class AttributeImportException(Exception):
    def __init__(self, attribute):

        self.attribute = attribute

        self.message = "Could not load " + attribute


class BadVCardError(Exception):
    pass


class VCard(models.Model):
    """
    import export functionality is done via vobject

    vobject is not the greatest lib in the world, but its on python.org
    it's poorly documented; had to find some functions using introspection...
    such as accessing plural properties...

    properties of vobject are probably best iterated using getChildren()
         then you check what type of property type and store it in the
         right place


    a fundamental queation is naming;
        do I pick sensible full names, making the code more readable
        do I use the vCard names, making it easier to relate the code to
        the original vCard
    """
    # required
    fn = models.CharField(
        max_length=1024, blank=False, null=False,
        verbose_name=_("formatted name"),
        help_text=_("The formatted string associated with the vCard object"))
    family_name = models.CharField(max_length=1024,
                                   verbose_name=_("family name"))
    given_name = models.CharField(max_length=1024,
                                  verbose_name=_("given name"))
    # n = models.OneToOneField('N', unique=True, blank=False, null=False, verbose_name=_("Name"), help_text=_("A structured representation of the name of the person, place or thing associated with the vCard object."))

    # bday can be formulated in various ways
    # some ways are dates, but according
    # to the vcard specs 'koninginnendag'
    # is perfectly fine. That is why bday
    # is stored as a CharField

    additional_name = models.CharField(max_length=1024,
                                       verbose_name=_("additional name"),
                                       blank=True)
    honorific_prefix = models.CharField(max_length=1024,
                                        verbose_name=_("honorific prefix"),
                                        blank=True)
    honorific_suffix = models.CharField(max_length=1024,
                                        verbose_name=_("honorific suffix"),
                                        blank=True)
    bday = models.DateField(blank=True, null=True, verbose_name=_("birthday"))
    classP = models.CharField(max_length=256, blank=True,
                              null=True, verbose_name=_("class"))
    rev = models.DateTimeField(blank=True, null=True,
                               verbose_name=_("last revision"))
    sort_string = models.CharField(max_length=256, blank=True,
                                   null=True, verbose_name=_("sort string"))
    # a uid is a URI. A URI consists of both
    # a URL and a URN. So using a URLField is
    # incorrect. Given that no URIField is available
    # a common CharField was used
    uid = models.CharField(max_length=256, blank=True,
                           null=True, verbose_name=_("unique identifier"))

    class Meta:
        verbose_name = _("vcard")
        verbose_name_plural = _("vcards")
        db_table = settings.DB_PREFIX.format('vcard')

    def __unicode__(self):
        return self.fn

    def save(self, **kwargs):
        # if not self.fn or self.fn == '':
        self.fill_fn()
        super(self.__class__, self).save(**kwargs)

    @classmethod
    def after_delete(cls, sender, instance, **kwargs):
        cache.delete(build_key(cls._meta.model_name, instance.pk))

    def fill_fn(self):
        if self.fn and (not self.given_name) and (not self.family_name):
            return
        self.fn = '' 
        if self.given_name:
            self.fn += self.given_name
        if self.family_name:
            self.fn += (' ' if self.fn else '') + self.family_name
        if not self.fn and self.emails.first():
            self.fn = self.emails.first().value.split('@')[0].replace('.', ' ')
        if not self.fn:
            raise BadVCardError('This is bad vcard since user does not know anything about this contact.')

    @classmethod
    def importFromVCardMultiple(cls, data, autocommit=False):
        """Return imported vcard objects as generator"""
        return cls.fromVCard(data, multiple=True, autocommit=autocommit)

    @classmethod
    def exportToVCardMultiple(cls, vcards):
        """Return exported vcards as generator"""
        return (vcard.toVCard() for vcard in vcards)

    # @classmethod
    # def importFrom(cls, tp, data, multiple=False, autocommit=False):
    #     """
    #     The contact sets its properties as specified in the argument 'data'
    #     according to the specification given in the string passed as
    #     argument 'tp'

    #     'tp' can be either 'vCard' or 'vObject'

    #     'vCard' is a string containing containing contact information
    #     formatted according to the vCard specification

    #     'vObject' is a vobject containing vcard contact information

    #     It returns a Contact object.
    #     """
    #     if tp.lower() == "vcard":
    #         return cls.fromVCard(data, multiple=multiple)

    #     if tp.lower() == "vobject":
    #         return cls.fromVObject(data)

    def exportTo(self, tp):
        """
        The contact returns an object with its properties in a format as
        defined by the argument tp.

        'tp' can be either 'vCard' or 'vObject'

        'vCard' is a string containing containing contact information
        formatted according to the vCard specification

        'vObject' is a vobject containing vcard contact information
        """
        if tp.lower() == "vcard":
            return self.toVCard()

        if tp.lower() == "vobject":
            return self.toVObject()

    @classmethod
    @transaction.atomic
    def fromVObject(cls, vObject, autocommit=False):
        """
        Contact sets its properties as specified by the supplied
        vObject. Returns a contact object.
        """

        # Instantiate a new Contact
        contact = cls()

        contact.errorList = []

        properties = vObject.getChildren()

        contact.childModels = []

        fnFound = False
        nFound = False

        for property in properties:
            # ----------- REQUIRED PROPERTIES --------------
            if property.name.upper() == "FN":

                try:
                    contact.fn = property.value
                    fnFound = True

                except Exception as e:
                    contact.errorList.append(contact._meta.get_field_by_name('fn')[0].verbose_name)

                continue

            if property.name.upper() == "N":

                # nObject = N()

                # nObject.contact = contact

                try:
                    contact.family_name = property.value.family
                    contact.given_name = property.value.given
                    contact.additional_name = property.value.additional
                    contact.honorific_prefix = property.value.prefix
                    contact.honorific_suffix = property.value.suffix

                    nFound = True

                except Exception as e:
                    contact.errorList.append(_("name"))
                continue
                # contact.childModels.append(nObject)

            # ----------- OPTIONAL MULTIPLE VALUE TABLE PROPERTIES -------
            if property.name.upper() == "TEL":
                t = Tel()

                t.contact = contact

                try:
                    for key in property.params.iterkeys():
                        if key.upper() == "TYPE":
                            t.type = property.params[key][0]

                    t.value = property.value

                    contact.childModels.append(t)

                except Exception as e:
                    contact.errorList.append(Tel._meta.verbose_name)

                continue

            if property.name.upper() == "ADR":
                adr = Adr()

                adr.contact = contact

                try:
                    adr.post_office_box = property.value.box
                    adr.extended_address = property.value.extended
                    adr.street_address = property.value.street
                    adr.locality = property.value.city
                    adr.region = property.value.region
                    adr.postal_code = property.value.code
                    adr.country_name = property.value.country

                    for key in property.params.iterkeys():
                        if key.upper() == "TYPE":
                            adr.type = property.params[key][0]
                        # if key.upper() == "VALUE"):
                        #    adr.value = property.params[ key ][ 0 ]

                    contact.childModels.append(adr)

                except Exception as e:
                    contact.errorList.append(Adr._meta.verbose_name)

                continue

            if property.name.upper() == "EMAIL":
                email = Email()  # email (type, value)

                email.contact = contact

                try:
                    for key in property.params.iterkeys():
                        if (key.upper() == "TYPE"):
                            email.type = property.params[key][0]

                    email.value = property.value

                    contact.childModels.append(email)

                except Exception as e:
                    contact.errorList.append(Email._meta.verbose_name)

                continue

            if property.name.upper() == "ORG":
                org = Org()  # org (organization_name, organization_unit)

                try:
                    org.organization_name = property.value[0]
                    if len(property.value) > 1:
                        org.organization_unit = property.value[1]

                    contact.childModels.append(org)

                except Exception as e:
                    contact.errorList.append(Org._meta.verbose_name)

                continue

            # ---------- OPTIONAL SINGLE VALUE NON TABLE PROPERTIES ---
            # these values can simply be assigned to the member value
            if property.name.upper() == "BDAY":

                try:
                    year  = int(property.value[0:4])
                    month = int(property.value[4:6])
                    day   = int(property.value[6:8])

                    contact.bday = date(year, month, day)

                except Exception as e:
                    try:
                        year  = int(property.value[0:4])
                        month = int(property.value[5:7])
                        day   = int(property.value[8:10])

                        contact.bday = date(year, month, day)

                    except:
                        contact.errorList.append(contact._meta.get_field_by_name('bday')[0].verbose_name)

                continue

            if property.name.upper() == "CLASS":
                try:
                    contact.classP = property.value

                except Exception as e:
                    contact.errorList.append(Contact._meta.get_field_by_name('classP')[0].verbose_name)

                continue

            if property.name.upper() == "REV":
                try:
                    contact.rev = datetime.fromtimestamp(int(re.match('\\d+', property.value).group(0)))

                except:
                    Contact.errorList.append(Contact._meta.get_field_by_name('rev')[0].verbose_name)

                continue

            # note there is still a distinct possibility the timestamp is misread!
            # many formats exist for timestamps, that all have different starting times etc.
            # supporting rev is in my opinion doomed to fail...

            if property.name.upper() == "SORT-STRING":
                try:
                    contact.sort_string = property.value

                except:
                    contact.errorList.append(Contact._meta.get_field_by_name('sort_string')[0].verbose_name)

                continue

            if property.name.upper() == "UID":
                try:
                    contact.uid = property.value

                except:
                    contact.errorList.append(Contact._meta.get_field_by_name('uid')[0].verbose_name)

                continue

            # ---------- MULTI VALUE NON TABLE PROPERTIES-----------
            if property.name.upper() == "AGENT":

                try:
                    agent = Agent()
                    agent.data = property.value
                    contact.childModels.append(agent)

                except:
                    contact.errorList.append(Agent._meta.verbose_name)

                continue

            if property.name.upper() == "CATEGORIES":
                try:

                    for catVal in property.value:

                        category = Category()

                        category.data = catVal

                        contact.childModels.append(category)

                except:
                    contact.errorList.append(Category._meta.verbose_name)

                continue

            if property.name.upper() == "GEO":
                try:

                    geo = Geo()
                    geo.data = property.value

                    contact.childModels.append(geo)

                except:
                    contact.errorList.append(Geo._meta.verbose_name)

                continue

            if property.name.upper() == "TZ":
                try:

                    tz = Tz()
                    tz.data = property.value

                    contact.childModels.append(tz)

                except:
                    contact.errorList.append(Tz._meta.verbose_name)

                continue

            if property.name.upper() == "KEY":
                try:

                    key = Key()
                    key.data = property.value

                    contact.childModels.append(key)

                except:
                    contact.errorList.append(Key._meta.verbose_name)

                continue

            if property.name.upper() == "LABEL":
                try:

                    label = Label()
                    label.data = property.value

                    contact.childModels.append(label)

                except:
                    contact.errorList.append(Label._meta.verbose_name)

                continue

            if property.name.upper() == "MAILER":
                try:

                    mailer = Mailer()
                    mailer.data = property.value

                    contact.childModels.append(mailer)

                except:
                    contact.errorList.append(Mailer._meta.verbose_name)

                continue

            if property.name.upper() == "NICKNAME":
                try:

                    nickname = Nickname()
                    nickname.data = property.value

                    contact.childModels.append(nickname)

                except:
                    contact.errorList.append(Nickname._meta.verbose_name)

                continue

            if property.name.upper() == "NOTE":
                try:

                    note = Note()
                    note.data = property.value

                    contact.childModels.append(note)

                except:
                    contact.errorList.append(Note._meta.verbose_name)

                continue

            # if property.name.upper() == "PHOTO":

            #    photo = Photo()
            #    photo.data = property.value

            #    contact.childModels.append(photo)

            if property.name.upper() == "ROLE":
                try:

                    role = Role()
                    role.data = property.value

                    contact.childModels.append(role)

                except:
                    contact.errorList.append(Role._meta.verbose_name)

                continue

            if property.name.upper() == "TITLE":
                try:

                    title = Title()
                    title.data = property.value

                    contact.childModels.append(title)

                except:
                    contact.errorList.append(Title._meta.verbose_name)

                continue

            if property.name.upper() == "X-URL":
                try:

                    url = Url()

                    # ':' is replaced with '\:' because ':' must be escaped in vCard files
                    url.data = re.sub(r'\\:', ':',  property.value)

                    contact.childModels.append(url)

                except:
                    contact.errorList.append(Url._meta.verbose_name)

                continue

            if property.name.upper() == "VERSION":
                continue

            contact.errorList.append(property.name.upper())
        if autocommit:
            contact.commit()
        return contact

    def commit(self):
        with tx.atomic():
            self.save()
            for m in self.childModels:
                m.vcard = self
                m.save()
        return self

    @classmethod
    def fromVCard(cls, vCardString, multiple=False, autocommit=False):
        """
        Contact sets its properties as specified by the supplied
        string. The string is in vCard format. Returns a Contact object.
        """
        if multiple:
            return (cls.fromVObject(vObject, autocommit=autocommit)
                    for vObject in vobject.readComponents(vCardString))
        vObject = vobject.readOne(vCardString)

        return cls.fromVObject(vObject, autocommit=autocommit)

    def toVObject(self):
        """
        returns a cast of the Contact to vobject
        """
        v = vobject.vCard()

        n = v.add('n')

        n.value = vobject.vcard.Name(
            given = self.given_name,
            family = self.family_name,
            additional = self.additional_name,
            prefix = self.honorific_prefix,
            suffix = self.honorific_suffix)

        fn = v.add('fn')

        fn.value = self.fn

        for j in self.adr_set.all():

            i = v.add('adr')

            jstreet   = j.street_address if j.street_address else ''
            jbox      = j.post_office_box if j.post_office_box else ''
            jregion   = j.region if  j.region else ''
            jcode     = j.postal_code if j.postal_code else ''
            jcountry  = j.country_name if j.country_name else ''
            jextended = j.extended_address if j.extended_address else ''
            jcity = j.locality if j.locality else ''

            i.type_param = j.type
            i.value = vobject.vcard.Address(
                     box = jbox,
                     extended = jextended,
                     street = jstreet,
                     region = jregion,
                     code = jcode,
                     country = jcountry,
                     city=jcity)

        for j in self.org_set.all():
            i = v.add('org')
            i.value[0]   = j.organization_name
            i.value.append(j.organization_unit)

        for j in self.emails.all():
            i = v.add('email')
            i.value = j.value
            i.type_param = j.type

        for j in self.tel_set.all():
            i = v.add('tel')
            i.value = j.value
            i.type_param = j.type

        if self.classP:
            i = v.add('class')
            i.value = self.classP

        if self.rev:
            i = v.add('rev')
            i.value = str(int(mktime(self.rev.timetuple())))

        if self.sort_string:
            i = v.add('sort-string')
            i.value = self.sort_string

        if self.uid:
            i = v.add('uid')
            i.value = self.uid

        if self.bday:

            i = v.add('bday')

            yearString  = str(self.bday.year)
            monthString = str(self.bday.month)
            dayString   = str(self.bday.day)

            if len(monthString) == 1:
                monthString = '0' + monthString
            if len(dayString) == 1:
                dayString = '0' + dayString
            i.value = yearString + monthString + dayString

        for j in self.geo_set.all():
            i = v.add('geo')
            i.value = j.data

        for j in self.tz_set.all():
            i = v.add('tz')
            i.value = j.data

        for j in self.agent_set.all():
            i = v.add('agent')
            i.value = j.data

        if len(self.category_set.all()) > 0:
            i = v.add('categories')
            i.value = []

            for j in self.category_set.all():
                i.value.append(j.data)

        for j in self.key_set.all():
            i = v.add('key')
            i.value = j.data

        for j in self.label_set.all():
            i = v.add('label')
            i.value = j.data

        #        for j in self.logo_set.all():
        #            i = v.add('logo')
        #            i.value = j.data

        for j in self.mailer_set.all():
            i = v.add('mailer')
            i.value = j.data

        for j in self.nickname_set.all():
            i = v.add('nickname')
            i.value = j.data

        for j in self.note_set.all():
            i = v.add('note')
            i.value = j.data

        #        for j in self.photo_set.all():
        #            i = v.add('photo')
        #            i.value = j.data

        for j in self.role_set.all():
            i = v.add('role')
            i.value = j.data

        #        for j in self.sound_set.all():
        #            i = v.add('sound')
        #            i.value = j.data

        for j in self.title_set.all():
            i = v.add('title')
            i.value = j.data

        for j in self.url_set.all():
            i = v.add('x-url')
            i.value = j.dataf

        return v

    def toVCard(self):
        """
        returns a cast of the Contact to a string in vCard format.
        """
        return self.toVObject().serialize()

    def serialize(self):
        return serialize_objs(self)

    @classmethod
    @transaction.atomic
    def merge_model_objects(cls, primary_object, alias_objects=[], keep_old=True, **kwargs):
        """

        """
        if not isinstance(alias_objects, list):
            alias_objects = [alias_objects]
        
        # check that all aliases are the same class as primary one and that
        # they are subclass of model
        primary_class = primary_object.__class__
        
        if not issubclass(primary_class, Model):
            raise TypeError('Only django.db.models.Model subclasses can be merged')
        
        for alias_object in alias_objects:
            if not isinstance(alias_object, primary_class):
                raise TypeError('Only models of same class can be merged')
        
        # Get a list of all GenericForeignKeys in all models
        # TODO: this is a bit of a hack, since the generics framework should provide a similar
        # method to the ForeignKey field for accessing the generic related fields.
        generic_fields = []
        for model in get_models():
            for field_name, field in filter(lambda x: isinstance(x[1], GenericForeignKey), model.__dict__.iteritems()):
                generic_fields.append(field)
                
        blank_local_fields = set([field.attname for field in primary_object._meta.local_fields if getattr(primary_object, field.attname) in [None, '']])
        
        # Loop through all alias objects and migrate their data to the primary object.
        for alias_object in alias_objects:
            # Migrate all foreign key references from alias object to primary object.
            for related_object in alias_object._meta.get_all_related_objects():
                try:
                    # The variable name on the alias_object model.
                    alias_varname = related_object.get_accessor_name()
                    # The variable name on the related model.
                    obj_varname = related_object.field.name
                    related_objects = getattr(alias_object, alias_varname)
                    for obj in related_objects.all():
                        setattr(obj, obj_varname, primary_object)
                        obj.save()
                except:
                    pass
    
            # Migrate all many to many references from alias object to primary object.
            for related_many_object in alias_object._meta.get_all_related_many_to_many_objects():
                alias_varname = related_many_object.get_accessor_name()
                obj_varname = related_many_object.field.name
                
                if alias_varname is not None:
                    # standard case
                    related_many_objects = getattr(alias_object, alias_varname).all()
                else:
                    # special case, symmetrical relation, no reverse accessor
                    related_many_objects = getattr(alias_object, obj_varname).all()
                for obj in related_many_objects.all():
                    getattr(obj, obj_varname).remove(alias_object)
                    getattr(obj, obj_varname).add(primary_object)
    
            # Migrate all generic foreign key references from alias object to primary object.
            for field in generic_fields:
                filter_kwargs = {}
                filter_kwargs[field.fk_field] = alias_object._get_pk_val()
                filter_kwargs[field.ct_field] = field.get_content_type(alias_object)
                for generic_related_object in field.model.objects.filter(**filter_kwargs):
                    setattr(generic_related_object, field.name, primary_object)
                    generic_related_object.save()
                    
            # Try to fill all missing values in primary object by values of duplicates
            filled_up = set()
            for field_name in blank_local_fields:
                val = getattr(alias_object, field_name) 
                if val not in [None, '']:
                    setattr(primary_object, field_name, val)
                    filled_up.add(field_name)
            blank_local_fields -= filled_up
                
            if not keep_old:
                alias_object.delete()
        if kwargs.get('fn'):
            primary_object.fn = kwargs.get('fn')
        elif kwargs.get('given_name') or kwargs.get('family_name'):
            primary_object.given_name = kwargs.get('given_name', '')
            primary_object.family_name = kwargs.get('family_name', '')
        primary_object.save()
        return primary_object


    @classmethod
    def after_save(cls, sender, instance, **kwargs):
        cache.set(build_key(cls._meta.model_name, instance.pk), json.dumps(serialize_objs(instance), default=date_handler))
        # TODO: each time when contact is updated vcard is recreated. So if it is the case then reinvalidate cache
        if hasattr(instance, 'contact'):
            contact = instance.contact
            contact_id = contact.id
            cached_contact = cache.get(build_key(contact.__class__._meta.model_name, contact_id))
            if cached_contact is None:
                return
            cached_contact = json.loads(cached_contact)
            old_id = cached_contact['vcard_id']
            cached_contact['vcard_id'] = instance.pk
            cache.set(build_key(contact.__class__._meta.model_name, contact_id), json.dumps(cached_contact, default=date_handler))
            cache.delete(build_key(cls._meta.model_name, old_id))

    @classmethod
    def get_by_ids(cls, *ids):
        """Get vcard by ids from cache with fallback to postgres."""
        rv = cache.get_many([build_key(cls._meta.model_name, vcard_id) for vcard_id in ids])
        rv = {extract_id(k, coerce=int): json.loads(v) for k, v in rv.iteritems()}

        not_found_ids = [vcard_id for vcard_id in ids if not vcard_id in rv]
        if not not_found_ids:
            return rv.values()
        vcards_qs = cls.objects.filter(pk__in=not_found_ids).prefetch_related(*vcard_rel_fields())
        more_rv = serialize_objs(vcards_qs)
        cache.set_many({build_key(cls._meta.model_name, vcard_raw['id']): json.dumps(vcard_raw, default=date_handler) for vcard_raw in more_rv})
        return rv.values() + more_rv

    @classmethod
    def cache_all(cls):
        vcard_qs = VCard.objects.all().prefetch_related(*vcard_rel_fields())
        vcards_raw = serialize_objs(vcard_qs)
        cache.set_many({build_key(cls._meta.model_name, vcard_raw['id']): json.dumps(vcard_raw, default=date_handler) for vcard_raw in vcards_raw})


post_save.connect(VCard.after_save, sender=VCard)
post_delete.connect(VCard.after_delete, sender=VCard)


class Tel(SerializableModel):
    """
    A telephone number of a contact
    """
    TYPE_CHOICES = (
        ('HOME', _(u"home")),
        ('VOICE', _(u"INTL")),
        ('MSG',  _(u"message")),
        ('WORK',  _(u"work")),
        ('pref',  _(u"prefered")),
        ('fax',  _(u"fax")),
        ('cell',  _(u"cell phone")),
        ('video',  _(u"video")),
        ('pager',  _(u"pager")),
        ('bbs',  _(u"bbs")),
        ('modem',  _(u"modem")),
        ('car',  _(u"car phone")),
        ('isdn',  _(u"isdn")),
        ('pcs',  _(u"pcs")),
        ('xadditional',  _(u"xadditional")),
    )

    vcard = models.ForeignKey(VCard, related_name='tels')
    # making a choice field of type is incorrect as arbitrary
    # types of phone number are allowed by the vcard specs.
    type  = models.CharField(max_length=30, verbose_name=_("type of phone number"), help_text=_("for instance WORK or HOME"), choices=TYPE_CHOICES)
    value = models.CharField(max_length=100, verbose_name=_("value"))

    class Meta:
        verbose_name = _("telephone number")
        verbose_name_plural = _("telephone numbers")

    class SerializerMeta:
        exclude = ['vcard']
        alias = 'tels'


class Email(SerializableModel):
    """
    An email of a contact
    """
    TYPES = INTERNET, X400, PREF = ('INTERNET', 'x400', 'pref')
    TYPE_CHOICES = (
        (INTERNET, _(u"internet")),
        (X400, _(u"x400")),
        (PREF, _(u"pref")),
    )

    vcard = models.ForeignKey(VCard, related_name='emails')
    type = models.CharField(max_length=30, verbose_name=_("type of email"), choices=TYPE_CHOICES)
    value = models.EmailField(max_length=100, verbose_name=_("value"))

    class Meta:
        verbose_name = _("email")
        verbose_name_plural = _("emails")

    def __unicode__(self):
        return '%s' % self.value

    class SerializerMeta:
        exclude = ['vcard']
        alias = 'emails'


class Geo(models.Model):
    """
    A geographical location associated with the contact
    in geo uri format
    """
    vcard = models.ForeignKey(VCard)
    # because vobject can't properly pass the geo uri for now the
    # field is specified as a normal CharField
    data = models.CharField(max_length=1024, verbose_name=_("geographic uri"))

    class Meta:
        verbose_name = _("geographic uri")
        verbose_name_plural = _("geographic uri's")


# class Org(SerializableModel):
#     """
#     An organization and unit the contact is affiliated with.
#     """
#     vcard = models.ForeignKey(VCard)
#     organization_name = models.CharField(max_length=1024, verbose_name=_("organization name"))
#     organization_unit = models.CharField(max_length=1024, verbose_name=_("organization unit"), blank=True)

#     class Meta:
#         verbose_name = _("organization")
#         verbose_name_plural = _("organizations")

#     def __eq__(self, r):
#         l = self
#         return (
#             l.organization_name == r.organization_name and
#             l.organization_unit == r.organization_unit)

#     @property
#     def name(self):
#         return self.organization_name

#     class SerializerMeta:
#         exclude = ['vcard']
#         alias = 'orgs'


class Adr(SerializableModel):
    """
    An address
    """
    TYPE_CHOICES = (
        ('WORK',  _(u"work")),
        ('INTL', _(u"INTL")),
        ('POSTAL', _(u"postal")),
        ('PARCEL',  _(u"parcel")),
        ('dom',  _(u"dom")),
        ('home',  _(u"home")),
        ('pref',  _(u"pref")),
        ('xlegal',  _(u"xlegal")),
    )

    vcard = models.ForeignKey(VCard, related_name='adrs')
    type = models.CharField(max_length=1024, verbose_name=_("type"), choices=TYPE_CHOICES)
    street_address = models.CharField(max_length=1024, verbose_name=_("street address"), blank=True, null=True)
    locality = models.CharField(max_length=1024, verbose_name=_("locality"), blank=True, null=True)
    region  = models.CharField(max_length=1024, verbose_name=_("region"), blank=True, null=True)
    country_name = models.CharField(max_length=1024, verbose_name=_("country name"), blank=True, null=True)
    post_office_box= models.CharField(max_length=1024, verbose_name=_("post office box"), blank=True, null=True)
    extended_address = models.CharField(max_length=1024, verbose_name=_("extended address"), blank=True, null=True)
    postal_code = models.CharField(max_length=1024, verbose_name=_("postal code"), blank=True, null=True)
    # value = models.CharField(max_lengt =1024, verbose_name=_("Value"))

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")

    def __eq__(self, r):
        l = self
        return (
            l.post_office_box == r.post_office_box and
            l.extended_address == r.extended_address and
            l.street_address == r.street_address and
            l.region == r.region and
            l.postal_code == r.postal_code and
            l.country_name == r.country_name and
            l.type == r.type)

    @classmethod
    def create_from_list(cls, params):
        adr = cls(vcard=params[0], type=params[1])
        try:
            adr.street_address = params[2]
            adr.locality = params[3]
            adr.region = params[4]
            adr.country_name = params[5]
            adr.post_office_box = params[6]
        except:
            pass
        adr.save()
        return adr

    class SerializerMeta:
        exclude = ['vcard']
        alias = 'adrs'


class Agent(models.Model):
    """
    An agent of the contact
    """
    vcard = models.ForeignKey(VCard)
    data = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("agent")
        verbose_name_plural = _("agents")


class Category(SerializableModel):
    """
    Specifies application category information about the
    contact.  Also known as "tags".
    """
    vcard = models.ForeignKey(VCard, related_name='categories')
    data = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __unicode__(self):
        return self.data

    class SerializerMeta:
        exclude = ['vcard']
        alias = 'categories'


class Key(models.Model):
    """
    Specifies a public key or authentication certificate
    associated with the contact information
    """
    vcard = models.ForeignKey(VCard)
    data = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("key")
        verbose_name_plural = _("keys")


class Label(models.Model):
    """
    Formatted text corresponding to a delivery
    address of the object the vCard represents
    """
    vcard = models.ForeignKey(VCard)
    data = models.CharField(max_length=2000)

    class Meta:
        verbose_name = _("label")
        verbose_name_plural = _("labels")


# class Logo(models.Model):
#    """
#    A logo associated with the contact

#    The data could be stored in binary or as a uri
#    as could be indicated by a type field

#    My advice; don't. The vcard specs on communicating
#    files are terrible. I'd even leave the entire field
#    out, and wouldn't bother with it. Otherwise it
#    would take a lot of time!
#    """
#    class Meta:
#        verbose_name = _("logo")
#        verbose_name_plural = _("logos")

#    contact = models.ForeignKey(Contact)

#    data = models.TextField()


class Mailer(models.Model):
    """
    No longer supported in draft vcard specificiation of July 12 2010
    """
    vcard = models.ForeignKey(VCard)
    data = models.CharField(max_length=2000)

    class Meta:
        verbose_name = _("mailer")
        verbose_name_plural = _("mailers")


class Nickname(models.Model):
    """
    The nickname of the
    object the vCard represents.
    """
    vcard = models.ForeignKey(VCard)
    data = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("nickname")
        verbose_name_plural = _("nicknames")


class Note(SerializableModel):
    """
    Supplemental information or a comment that is
    associated with the vCard.
    """
    vcard = models.ForeignKey(VCard, related_name='notes')
    data = models.TextField()

    def __unicode__(self):
        return self.data

    class Meta:
        verbose_name = _("note")
        verbose_name_plural = _("notes")

    class SerializerMeta:
        exclude = ['vcard']
        alias = 'notes'


# class Photo(models.Model):
#    """
#    A photo of some aspect of the contact
#
#    The data could be stored in binary or as a uri
#    as could be indicated by a type field

#    My advice; don't. The vcard specs on communicating
#    files are terrible. I'd even leave the entire field
#    out, and wouldn't bother with it. Otherwise it
#    would take a lot of time!
#    """
#    class Meta:
#        verbose_name = _("photo")
#        verbose_name_plural = _("photos")


#    contact = models.ForeignKey(Contact)

#    data = models.TextField()


class Role(models.Model):
    """
    The function or part played in a particular
    situation by the object the vCard represents.
    """
    vcard = models.ForeignKey(VCard)
    data = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")


# class Sound(models.Model):
#    """
#    A sound about some aspect of the contact

#    The data could be stored in binary or as a uri
#    as could be indicated by a type field

#    My advice; don't. The vcard specs on communicating
#    files are terrible. I'd even leave the entire field
#    out, and wouldn't bother with it. Otherwise it
#    would take a lot of time!
#    """
#    class Meta:
#        verbose_name = _("sound")
#        verbose_name_plural = _("sounds")
#    contact = models.ForeignKey(Contact)

#    data = models.TextField()


class Title(SerializableModel):
    """
    The position or job of the contact
    """
    vcard = models.ForeignKey(VCard, related_name='titles')
    data = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("title")
        verbose_name_plural = _("titles")

    def __eq__(self, r):
        l = self
        return l.data == r.data

    class SerializerMeta:
        exclude = ['vcard']
        alias = 'titles'


class Tz(models.Model):
    """
    A time zone of a contact

    Tz is represented as a CharField and not in a formal structure because
    the vcard specification allows city names as tz parameters
    """
    vcard = models.ForeignKey(VCard)
    data = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("time zone")
        verbose_name_plural = _("time zones")


class Url(SerializableModel):
    """
    A Url associted with a contact.
    """
    TYPE_CHOICES = (
        ('website', _(u"website")),
        ('github', _(u"github")),
    )
    vcard = models.ForeignKey(VCard, related_name='urls')
    type = models.CharField(max_length=40, verbose_name=_("type"), choices=TYPE_CHOICES)
    value = models.URLField()

    class Meta:
        verbose_name = _("url")
        verbose_name_plural = _("url's")

    class SerializerMeta:
        exclude = ['vcard']
        alias = 'urls'
