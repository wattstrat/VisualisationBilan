from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field

from django import forms
from django.utils.translation import ugettext as _


class BootstrapFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_class = 'form-horizontal'
        self.label_class = 'col-md-3'
        self.field_class = 'col-md-9'


class WattstratSubmit(Submit):
    field_classes = 'ws-btn ws-big-btn'
    template = "shared/crispy_layout/submit.html"


class DisplayField(Field):
    template = "shared/crispy_layout/field_display.html"


class SimpleCrispyMixin(forms.ModelForm):
    submit_label = _('Save')
    add_submit = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = BootstrapFormHelper()
        layout_fields = [Field(field_name) for field_name in self.fields.keys()]
        if self.add_submit:
            layout_fields += [self.get_submit()]
        self.helper.layout = Layout(
            *layout_fields
        )

        self.display_helper = BootstrapFormHelper()
        display_fields = [DisplayField(field_name) for field_name in self.fields.keys()]
        self.display_helper.layout = Layout(*display_fields)

    def get_submit(self):
        return WattstratSubmit('submit', self.submit_label)
