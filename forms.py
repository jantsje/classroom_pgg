from django import forms
from .models import Player, Punishment, Constants
from django.forms import BaseInlineFormSet, ValidationError, inlineformset_factory
from django.core.validators import MaxValueValidator, MinValueValidator


class PunishmentForm(forms.ModelForm):
    amount = forms.IntegerField(min_value=0, required=True, widget=forms.NumberInput(attrs={'required': True}))

    class Meta:
        model = Punishment
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        maxval = self.instance.sender.punishment_endowment
        self.fields['amount'].validators += [MaxValueValidator(maxval)]
        self.fields['amount'].widget.attrs['max'] = maxval


class PunishmentFormset(BaseInlineFormSet):
    non_field_errors = None

    def clean(self):
        super().clean()
        if any(self.errors):
            self.non_field_errors = 'Please check your answers'
            return
        amounts = []
        punishment_endowment = self.instance.punishment_endowment
        for form in self.forms:
            amounts.append(form.cleaned_data['amount'])
        if sum(amounts) > punishment_endowment:
            self.non_field_errors = "In total you can't send more than {endowment} points!".format(
                endowment=punishment_endowment)
            raise ValidationError(self.non_field_errors)


PFormset = inlineformset_factory(Player, Punishment,
                                 formset=PunishmentFormset,
                                 form=PunishmentForm,
                                 extra=0,
                                 can_delete=False,
                                 fk_name='sender',
                                 fields=['amount'])
