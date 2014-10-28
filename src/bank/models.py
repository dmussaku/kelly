from django.db import models

class Loan(models.Model):
	contact = models.ForeignKey()
	contract_number = models.IntegerField()
	apr = models.FloatFied() #annual percentage rate
	date_created = models.DateTimeField()
	date_finished = models.DatetimeField()
	loan_type = models.ChoiceField()
	loan_sum = models.IntegerField()
	aerr - models.FloatField() #annual effective rate of return
	payment_dates = models.ListField() #payment Schedule
	upb = models.IntegerField() #unpaid principle ballance
	payment_frequence = models.ChoiceField()
	outstanding_dept = models.IntField() #close with upb
	fine = models.FloatField()
	card = models.ForeignKey('Card')


class Deposit(models.Model):
	contact = models.ForeignKey()
	contract_number = models.IntegerField()
	apr = models.FloatFied() #annual percentage rate
	date_created = models.DateTimeField()
	date_finished = models.DatetimeField()
	deposit_type = models.ChoiceField()
	renewal_conditions = models.ChoiceField()
	compound_interest = models.ListField()
	card = models.ForeignKey('Card')


class Card(models.Model):
	contact = models.ForeignKey()
	contract_number = models.IntegerField()
	date_created = models.DateTimeField()
	date_finished = models.DatetimeField()
	balance = models.IntegerField()
	cashflow = models.ListField()
	services = models.ListField()
	active = models.BooleanField()


class Account(models.Model):
	balance = models.IntegerField()
	cashflow = models.ListField()
	date_created = models.DateTimeField()
	date_finished = models.DatetimeField()
	active = models.BooleanField()


class Transfer(models.Model):
	cashflow = models.ListField()
	transfer_type = models.ForeignKey('TransferType')


class TransferType(models.Model):
	name = models.CharField()
	conditions = models.CharField()
	tariff = models.FloatField()


class SafeOperation(models.Model):
	docs = models.ListField()
	cell_sizes = models.ListField()
	conditions = models.CharField()
	date_created = models.DateTimeField()
	date_finished = models.DateTimeField()
	tariff = models.FloatField()
	payment = models.IntegerField()
