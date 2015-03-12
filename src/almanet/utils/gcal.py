import datetime
# import oauth.oauth as oauth
import httplib2
import random
from django.conf import settings
from oauth2client.file import Storage
from apiclient.discovery import build
from oauth2client.tools import run
from oauth2client.client import OAuth2WebServerFlow
import gflags
from django.utils.translation import ugettext_lazy as _
FLAGS = gflags.FLAGS
CALENDAR_ID = '7so4s32gs2mpbrs7ecrqqist3o@group.calendar.google.com'
FLOW = OAuth2WebServerFlow(
    client_id='405002223375-06d8suldprun88p84dgmoed8ir3higa1.apps.googleusercontent.com',
    client_secret='WcbTngSPwGQl_z41EsrS1Agk',
    scope='https://www.googleapis.com/auth/calendar',
    user_agent='chrome/38',
    redirect_uri='http://localhost:8080/')


class GCalConnection(object):
    service = None

    def establish(self):
        if not self.service:
            storage = Storage('calendar.dat')
            credentials = storage.get()
            if not credentials or credentials.invalid:
                credentials = run(FLOW, storage)
            http = httplib2.Http()
            http = credentials.authorize(http)
            self.service = build(
                serviceName='calendar', version='v3',
                http=http, developerKey='AIzaSyCqPeJk-5kcWO3T9uiXV9OIGhIo3gDhe7A')
            return self
        # return self.service

    def build_event_from_activity(self, activity):
        assert self.service is not None, "service should not be known"
        author = activity.author.get_billing_user()
        from_dt = activity.deadline.isoformat()
        rand_minutes = random.randint(1, 24 * 60)
        from_dt = (activity.deadline + datetime.timedelta(
            minutes=rand_minutes)).isoformat()
        to_dt = (activity.deadline + datetime.timedelta(
            minutes=rand_minutes + 60)).isoformat()
        description = _(
            "Activity was created at %(cycle)s for contact %(contact)s.") % {
            'cycle': activity.sales_cycle.title,
            'contact': "{} <{}>".format(activity.sales_cycle.contact.email, activity.sales_cycle.contact.name)
        }

        event = {
            'summary': activity.description,
            'description': description,
            # 'colorId':
            'start': {
                'dateTime': from_dt,
            },
            'end': {
                'dateTime': to_dt
            },
            'attendees': [{
                'email': author.email,
                'displayName': author.get_full_name()
            }],
        }
        self.service.events().insert(
            calendarId=CALENDAR_ID,
            body=event).execute()
