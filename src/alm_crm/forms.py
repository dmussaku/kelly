from models import Contact, SalesCycle, Mention, Comment, Activity, Value, \
     Share
from alm_user.models import User
from django import forms
from django.forms import ModelForm
import json


class ActivityForm(ModelForm):
    mentioned_user_ids_json = forms.CharField(max_length=300)

    class Meta:
        model = Activity

    def save(self, commit=True):
        activity = super(ActivityForm, self).save(commit=commit)
        if commit:
            try:
                mentioned_user_ids = json.loads(
                    self.cleaned_data['mentioned_user_ids_json'])
            except ValueError, e:
                raise Exception(e)
                mentioned_user_ids = []

            for user_id in mentioned_user_ids:
                m = Mention(user_id=user_id, content_object=activity)
                m.save()
        return activity


class ContactForm(ModelForm):

    class Meta:
        model = Contact
        exclude = ['date_created', 'latest_activity']


class SalesCycleForm(ModelForm):

    class Meta:
        model = SalesCycle
        exclude = ['status', 'date_created', 'latest_activity']


class ShareForm(ModelForm):

    class Meta:
        model = Share
        exclude = ['date_created']


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

        
