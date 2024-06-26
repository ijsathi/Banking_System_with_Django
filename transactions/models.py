from django.db import models
from accounts.models import UserBankAccount
from .constants import TRANSACTION_TYPE

class Transaction(models.Model):
    account = models.ForeignKey(UserBankAccount, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits=12)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'Transaction of {self.amount} {self.get_transaction_type_display()}'

    @classmethod
    def create_deposit(cls, account, amount):
        transaction = cls.objects.create(
            account=account,
            amount=amount,
            balance_after_transaction=account.balance + amount,
            transaction_type=TRANSACTION_TYPE.DEPOSIT
        )
        account.balance += amount
        account.save()
        return transaction

    @classmethod
    def create_withdrawal(cls, account, amount):
        if account.balance >= amount:
            transaction = cls.objects.create(
                account=account,
                amount=-amount,
                balance_after_transaction=account.balance - amount,
                transaction_type=TRANSACTION_TYPE.WITHDRAWAL
            )
            account.balance -= amount
            account.save()
            return transaction
        else:
            return None

    @classmethod
    def create_transfer(cls, from_account, to_account, amount):
        if from_account.balance >= amount:
            transaction_from = cls.objects.create(
                account=from_account,
                amount=-amount,
                balance_after_transaction=from_account.balance - amount,
                transaction_type=TRANSACTION_TYPE.TRANSFER_OUT
            )
            transaction_to = cls.objects.create(
                account=to_account,
                amount=amount,
                balance_after_transaction=to_account.balance + amount,
                transaction_type=TRANSACTION_TYPE.TRANSFER_IN
            )
            from_account.balance -= amount
            to_account.balance += amount
            from_account.save()
            to_account.save()
            return transaction_from, transaction_to
        else:
            return None, None
