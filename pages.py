from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .forms import PFormset
from .models import Constants, Player, Punishment as PunishmentModel
from otree.constants import timeout_happened



class Introduction(Page):
    """Description of the game: How to play and returns expected"""
    pass

    timeout_seconds = 90

    def is_displayed(self):
        return self.subsession.round_number == 1


class Contribute(Page):
    """Player: Choose how much to contribute"""

    form_model = 'player'
    form_fields = ['contribution']

    def is_displayed(self):
        return self.subsession.round_number <= self.session.config["num_rounds"]


class AfterContribWP(WaitPage):
    after_all_players_arrive = 'set_pd_payoffs'

    def is_displayed(self):
        return self.subsession.round_number <= self.session.config["num_rounds"]

    # body_text = "Waiting for other participants to contribute."


class Punishment(Page):
    def post(self):
        print(self.request.POST)
        return super().post()

    def get_formset(self, data=None):
        return PFormset(instance=self.player,
                        data=data,
                        )

    def get_form(self, data=None, files=None, **kwargs):
        # here if this page was forced by admin to continue we just submit an empty form (with no formset data)
        # if we need this data later on that can create some problems. But that's the price we pay for autosubmission
        if data and data.get('timeout_happened'):
            return super().get_form(data, files, **kwargs)
        if not data:
            return self.get_formset()
        formset = self.get_formset(data=data)
        return formset

    def before_next_page(self):
        if self.timeout_happened:
            self.player.punishments_sent.all().update(amount=0)

    def is_displayed(self):
        if not self.session.config["punishment"]:
            return False
        else:
            return self.subsession.round_number <= self.session.config["num_rounds"]


class AfterPunishmentWP(WaitPage):
    after_all_players_arrive = 'set_punishments'

    def is_displayed(self):
        return self.subsession.round_number <= self.session.config["num_rounds"]


class Results(Page):
    """Players payoff: How much each has earned"""

    timeout_seconds = 20

    def vars_for_template(self):
        return dict(
            total_earnings=self.group.total_contribution * self.session.config["efficiency_factor"]
        )

    def is_displayed(self):
        return self.subsession.round_number <= self.session.config["num_rounds"]


class FinalResults(Page):
    """Final payoff"""

    def is_displayed(self):
        return self.subsession.round_number == self.session.config["num_rounds"]


page_sequence = [
    Introduction,
    Contribute,
    AfterContribWP,
    Punishment,
    AfterPunishmentWP,
    Results,
    FinalResults
]
