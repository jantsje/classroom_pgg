from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

from django.db import models as djmodels

doc = """
This is a one-period public goods game with 3 players.
"""


class Constants(BaseConstants):
    name_in_url = 'classroom_pgg'
    players_per_group = 3
    num_others_per_group = players_per_group - 1
    num_rounds = 100
    instructions_template = 'classroom_pgg/instructions.html'

    # """Amount allocated to each player"""
    endowment = c(100)
    punishment_endowment = c(10)
    punishment_factor = 3


from django.db.models import Q, F


class Subsession(BaseSubsession):
    def vars_for_admin_report(self):
        contributions = [p.contribution for p in self.get_players() if p.contribution != None]
        if contributions:
            return dict(
                avg_contribution=sum(contributions) / len(contributions),
                min_contribution=min(contributions),
                max_contribution=max(contributions)
            )
        else:
            return dict(
                avg_contribution='(no data)',
                min_contribution='(no data)',
                max_contribution='(no data)'
            )

    def creating_session(self):
        ps = []
        for p in self.get_players():
            for o in p.get_others_in_group():
                ps.append(Punishment(sender=p, receiver=o, ))
        Punishment.objects.bulk_create(ps)


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    average_contribution = models.CurrencyField()
    reached_threshold = models.CurrencyField()
    total_share = models.CurrencyField()
    individual_share = models.CurrencyField()

    def set_pd_payoffs(self):
        self.total_contribution = sum([p.contribution for p in self.get_players()])
        self.average_contribution = self.total_contribution / self.session.config["players_per_group"]
        self.reached_threshold = self.total_contribution >= self.session.config["threshold"]
        if self.reached_threshold:
            self.total_share = self.total_contribution * self.session.config["efficiency_factor"]
        else:
            self.total_share = 0
        self.individual_share = self.total_share / self.session.config["players_per_group"]
        for p in self.get_players():
            p.pd_payoff = sum([+ Constants.endowment,
                               - p.contribution,
                               + self.individual_share,
                               ])
            p.set_punishment_endowment()

    def set_punishments(self):
        if self.session.config["punishment"]:
            for p in self.get_players():
                p.set_punishment()
        for p in self.get_players():
            p.set_payoff()


class Player(BasePlayer):
    contribution = models.CurrencyField(
        min=0, max=Constants.endowment,
        doc="""The amount contributed by the player""",
        label="How much will you contribute to the project (from 0 to {})?".format(Constants.endowment)
    )
    punishment_sent = models.CurrencyField()
    punishment_received = models.CurrencyField()
    pd_payoff = models.CurrencyField(doc='to store payoff from contribution stage')
    punishment_endowment = models.CurrencyField(initial=0, doc='punishment endowment')

    def set_payoff(self):
        if not self.session.config["punishment"]:
            self.punishment_received = 0
            self.punishment_sent = 0
        self.payoff = self.pd_payoff - self.punishment_sent - self.punishment_received

    def set_punishment_endowment(self):
        assert self.pd_payoff is not None, 'You have to set pd_payoff before setting punishment endowment'
        self.punishment_endowment = min(self.pd_payoff, Constants.punishment_endowment)

    def set_punishment(self):
        self.punishment_sent = sum([i.amount for i in self.punishments_sent.all()])
        self.punishment_received = sum(
            [i.amount for i in self.punishments_received.all()]) * self.session.config["punishment_factor"]


class Punishment(djmodels.Model):
    sender = djmodels.ForeignKey(to=Player, related_name='punishments_sent', on_delete=djmodels.CASCADE)
    receiver = djmodels.ForeignKey(to=Player, related_name='punishments_received', on_delete=djmodels.CASCADE)
    amount = models.IntegerField(min=0)