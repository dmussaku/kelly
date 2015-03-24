# IPython log file

CRMUser.objects.first()
SalesCycle.objects.all()
for c in Contact.objects.all():
    c.delete()
    
SalesCycle.objects.all()
SalesCycle.objects.all()[0].delete()
SalesCycle.objects.all()[0].delete()
SalesCycle.objects.all()[0].delete()
VCard.objects.all()
from django.db import transaction
c = Contact()
c.save()
c
vcard = VCard(fn='Daniyar')
vcard.save()
c.vcard=vcard
c.save()
vcard.contact
get_ipython().magic(u'recall')
Daniyar user
get_ipython().magic(u'recall')
get_ipython().magic(u'history')
get_ipython().magic(u'logstart')
get_ipython().magic(u'dhist')
get_ipython().magic(u'history -g')
get_ipython().magic(u'history hel')
get_ipython().magic(u'history help')
get_ipython().magic(u'history --help')
get_ipython().magic(u'history -help')
get_ipython().magic(u'history')
VCard._meta.get_all_related_objects()
VCard._meta.get_all_related_objects()
import time
time.time
time.time()
time.time()
from django.db.transaction import atomic
from django.db import transaction
with transaction.commit_on_success():
    for c in Contact.objects.all():
        c.delete()
        
Contact.objects.all()
with transaction.commit_on_success():
    for c in VCard.objects.all():
        c.delete()
        
User.objects.all()
Company.objects.first()
Company.objects.first().name
Service.objects.all()
Subscription
Subscription.objects.all()
s = Subscription()
s.user = User.objects.first()
s.service = Service.objects.first()
s.save()
s.organization = Company.objects.first()
s.save()
User.objects.first()
User.objects.first()
exit()
