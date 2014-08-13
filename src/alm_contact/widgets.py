from django import forms
from django.template.loader import render_to_string

class AddressMultiWidget(forms.MultiWidget):

    def __init__(self, attrs=None):
        widgets = (
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
            forms.NumberInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
        )
        super(AddressMultiWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.box, value.extended, value.code, value.street, value.city, value.region, value.country]
        return ['', '', '', '', '', '', '']

    def format_output(self, rendered_widgets):
        widgetContext = {
            'box': rendered_widgets[0],
            'extended': rendered_widgets[1], 
            'code': rendered_widgets[2],
            'street': rendered_widgets[3],
            'city': rendered_widgets[4],
            'region': rendered_widgets[5],
            'country': rendered_widgets[6],
        }
        return render_to_string("contact/_address_widget.html", widgetContext)