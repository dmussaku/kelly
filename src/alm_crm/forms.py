from models import Contact, SalesCycle, Mention, Comment, Activity, Value
from alm_user.models import User
from django import forms
from django.forms import ModelForm


class ActivityForm(ModelForm):

    class Meta:
        model = Activity
        exclude = ['feedback']


class ContactForm(ModelForm):

    class Meta:
        model = Contact
        exclude = ['date_created', 'latest_activity']


class SalesCycleForm(ModelForm):

    class Meta:
        model = SalesCycle
        exclude = ['status', 'date_created', 'latest_activity']


def get_user_choices():
    index_list = []
    user_list = []
    for i in User.objects.all():
        index_list.append(str(i.id))
        user_list.append(str(i))
    return tuple(zip(index_list, user_list))


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
