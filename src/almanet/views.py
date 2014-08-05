from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy

def fork_index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse_lazy('user_profile_url'))
    else:
        return HttpResponseRedirect(reverse_lazy('user_login'))