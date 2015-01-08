from django.dispatch import Signal
subscription_reconn = Signal(providing_args=['service', 'service_user'])
