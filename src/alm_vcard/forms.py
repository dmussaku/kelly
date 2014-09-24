from django import forms
from models import *

'''
"VCard", "Tel", "Email", "Geo", "Org", "Adr", "Agent", "Category", "Key", "Label", "Mailer", "Nickname", "Note", "Role", "Title", "Tz", "Url"
'''
class VCardUploadForm(forms.Form):
    myfile = forms.FileField(label='Select a file')

class VCardForm(forms.ModelForm):

    class Meta():
        model = VCard


class TelForm(forms.ModelForm):

    class Meta():
        model = Tel



class EmailForm(forms.ModelForm):

    class Meta():
        model = Email


class GeoForm(forms.ModelForm):

    class Meta():
        model = Geo


class OrgForm(forms.ModelForm):

    class Meta():
        model = Org


class AdrForm(forms.ModelForm):

    class Meta():
        model = Adr


class AgentForm(forms.ModelForm):

    class Meta():
        model = Agent


class CategoryForm(forms.ModelForm):

    class Meta():
        model = Category


class KeyForm(forms.ModelForm):

    class Meta():
        model = Key


class LabelForm(forms.ModelForm):

    class Meta():
        model = Label


class MailerForm(forms.ModelForm):

    class Meta():
        model = Mailer


class NicknameForm(forms.ModelForm):

    class Meta():
        model = Nickname


class NoteForm(forms.ModelForm):

    class Meta():
        model = Note


class RoleForm(forms.ModelForm):

    class Meta():
        model = Role


class TitleForm(forms.ModelForm):

    class Meta():
        model = Title


class TzForm(forms.ModelForm):

    class Meta():
        model = Tz


class UrlForm(forms.ModelForm):

    class Meta():
        model = Url
