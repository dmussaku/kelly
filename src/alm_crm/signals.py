from django.db.models import signals
from django.dispatch import receiver
from alm_crm.models import Activity


@receiver(signals.post_save, sender=Activity)
def set_latest_activity_to_sales_cycle_and_contact(sender, **kwargs):
    if kwargs.get('created', False):
        activity = kwargs.get('instance', None)
        sales_cycle = activity.sales_cycle
        sales_cycle.latest_activity = activity
        sales_cycle.save()

        contact = sales_cycle.contact
        contact.latest_activity = activity
        contact.save()


@receiver(signals.post_delete, sender=Activity)
def reset_latest_activity_to_sales_cycle_and_contact(sender, **kwargs):
    activity = kwargs.get('instance', None)
    sales_cycle = activity.sales_cycle
    sales_cycle.latest_activity = sales_cycle.get_latest_activity()
    sales_cycle.save()

    contact = sales_cycle.contact
    contact.latest_activity = contact.get_latest_activity()
    contact.save()
