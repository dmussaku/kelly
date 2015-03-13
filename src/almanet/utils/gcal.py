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
CALENDAR_ID = 'grhc502knl9puo3qcsvnbj2i8o@group.calendar.google.com'
FLOW = OAuth2WebServerFlow(
    client_id='95263978532-16369qcnql6vlfpg557bovit8k36s1dk.apps.googleusercontent.com',
    client_secret='SFWiFZOWqnVfQS5ytqGOvkt9',
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
                http=http, developerKey='AIzaSyAxL4aIOSlW11sgc0qWe8KOlRwkGQ08vNM')
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
        new_event = self.service.events().insert(
            calendarId=CALENDAR_ID,
            body=event).execute()
        return new_event['id']

    def get_event_by_id(self, event_id):
        assert self.service is not None, 'service should not be known'
        return self.service.events().get(
            calendarId=CALENDAR_ID, eventId=event_id).execute()

    def update_event_with_activity(self, activity, event_id):
        assert self.service is not None, "service should not be known"
        event = self.get_event_by_id(event_id)
        from_dt = activity.deadline.isoformat()
        to_dt = (activity.deadline + datetime.timedelta(minutes=60)).isoformat()
        author = activity.author.get_billing_user()
        event.update({
            'summary': activity.description,
            'start': {'dateTime': from_dt},
            'end': {'dateTime': to_dt},})
        event['sequence'] += 1    # incr sequence since google checks it
        self.service.events().update(
            calendarId=CALENDAR_ID,
            eventId=event_id,
            body=event).execute()

    def remove_event(self, event_id):
        assert self.service is not None, 'service should not be known'
        self.service.events().delete(
            calendarId=CALENDAR_ID,
            eventId=event_id).execute()
