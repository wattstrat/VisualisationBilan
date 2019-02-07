from django import forms
from django.utils.translation import ugettext as _

from crispy_forms.layout import Layout, HTML, Field
from crispy_forms.helper import FormHelper

from wattstrat.simulation.models import Simulation
from wattstrat.utils.forms import SimpleCrispyMixin, WattstratSubmit
from django.forms.widgets import HiddenInput


class BaseCreateSimulationForm(SimpleCrispyMixin, forms.ModelForm):
    submit_label = _('Create')

    class Meta:
        model = Simulation
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(BaseCreateSimulationForm, self).__init__(*args, **kwargs)
        self.instance.account = user.account


class TerritoryAssessmentForm(BaseCreateSimulationForm):
    add_submit = False
    #CHOICES = (('average','Année moyenne'),('2016','2016'),('2015', '2015'),('2014', '2014'),('2013','2013'),('2012','2012'),('2011','2011'),('2010','2010'))
    CHOICES = (('2015', '2015'),)
    weather = forms.ChoiceField(choices=CHOICES, label='Météo')

    class Meta:
        model = Simulation
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(TerritoryAssessmentForm, self).__init__(*args, **kwargs)
        self.helper.layout[0].attrs['placeholder'] = _(
            'Ex: Assessment 2015 Paris')
        self.helper.form_tag = False


class RemovalForm(forms.Form):
    simulation = forms.ModelChoiceField(label="Simulation à supprimer",
                                        queryset=Simulation.objects.all(),
                                        widget=forms.HiddenInput(),
                                        initial=0,
                                        required=True,
                                        to_field_name='shortid')
    action = forms.Field(label='action',
                        widget=forms.HiddenInput(),
                        initial="removal")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-1'
        self.helper.field_class = 'col-md-11'

        self.helper.layout = Layout(
            Field('simulation'),
            Field('action'),
            WattstratSubmit('submit', _('Suppression')),
        )
