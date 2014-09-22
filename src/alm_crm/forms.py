from models import Contact, SalesCycle, Mention, Comment, Activity, Value, ActivityFeedback
from alm_user.models import User
from django import forms
from django.forms import ModelForm


class ActivityForm(ModelForm):

    class Meta:
        model = Activity
        exclude = ['feedback']

class ActivityFeedbackForm(ModelForm):

	class Meta:
		model = ActivityFeedback
		exclude = ['date_created', 'date_edited']


class ContactForm(ModelForm):

    class Meta:
        model = Contact
        exclude = ['date_created', 'latest_activity']


class SalesCycleForm(ModelForm):

    class Meta:
        model = SalesCycle
        exclude = ['status', 'date_created', 'latest_activity']


def get_user_choices():
    for u in User.objects.all():
        yield (u.pk, u)


class MentionForm(ModelForm):
    user_id = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                        choices=get_user_choices())

    class Meta:
        model = Mention
        exclude = ['content_type', 'content_id', 'object_id']


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['comment']


class ValueForm(ModelForm):

    class Meta:
        model = Value
        field = ['salary', 'amount', 'currency']
