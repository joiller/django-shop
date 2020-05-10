# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from polymorphic.models import PolymorphicModel
from django.db.models import CASCADE

'''Products,Charges,Accounts,Extractions,Purchases,Transactions'''


class Accounts(models.Model):
    name = models.CharField(max_length=45, unique=True, null=False)
    password = models.CharField(max_length=16, null=False)
    balance = models.FloatField(blank=True, null=True,default=0)

    def __str__(self):
        return self.name

    class Meta:
        # managed = False
        db_table = 'accounts'
        verbose_name_plural = 'Accounts'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Charges(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE, db_column='account_id')
    amount = models.FloatField()
    from_card = models.CharField(max_length=20)

    class Meta:
        # managed = False
        db_table = 'charges'
        verbose_name_plural = 'Charges'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Extractions(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE, db_column='account_id')
    amount = models.FloatField()
    to_card = models.CharField(max_length=20)

    class Meta:
        # managed = False
        db_table = 'extractions'
        verbose_name_plural = 'Extractions'


class Products(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, null=False, unique=True)
    volume = models.IntegerField(default=0, null=False)
    price = models.FloatField(default=10, null=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products'
        verbose_name_plural = 'Products'


class Purchases(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE, db_column='account_id')
    amount = models.FloatField()
    product = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    volume = models.IntegerField()
    status = models.IntegerField(default=0)

    class Meta:
        # managed = False
        db_table = 'purchases'
        verbose_name_plural = 'Purchases'


def increment_transaction():
    last_transaction = Transactions.objects.filter() \
        .order_by('id').last()
    if not last_transaction:
        return 'TRAN' + '1'
    return 'TRAN' + str(last_transaction.id + 1)


class Transactions(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE, db_column='account_id')
    category = models.IntegerField(blank=True, null=True)
    category_id = models.IntegerField(blank=True, null=True)
    transaction_number = models.CharField(max_length=40,null=False)
    trans_id = models.CharField(
        max_length=20,
        default='no',
        # default=1,
        # editable=False
    )

    # pad = models.CharField(max_length=20)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        last_transaction = Transactions.objects \
            .filter(category=self.category) \
            .count()
        trans_types = ['C', 'P', 'E']
        self.trans_id = trans_types[self.category-1] \
                        + str(last_transaction)
        super().save()

    class Meta:
        # managed = False
        db_table = 'transactions'
        verbose_name_plural = 'Transactions'


class TransactionsPoly(PolymorphicModel):
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        db_table = 'transactions_poly'


class PurchasesPoly(TransactionsPoly):
    amount = models.FloatField(null=False)
    product = models.ForeignKey(Products,on_delete=CASCADE)
    volume = models.PositiveIntegerField(null=False,default=1)
    status = models.IntegerField(null=False,default=0)

    class Meta:
        db_table = 'purchases_poly'


class RefundsPoly(TransactionsPoly):
    amount = models.FloatField(null=False)
    product = models.ForeignKey(Products, on_delete=CASCADE)
    volume = models.PositiveIntegerField(null=False, default=1)
    status = models.IntegerField(null=False, default=0)

    class Meta:
        db_table = 'refunds_poly'


class ChargesPoly(TransactionsPoly):
    amount = models.FloatField(null=False)
    from_card = models.CharField(max_length=20)
    status = models.IntegerField(null=False, default=0)

    class Meta:
        db_table = 'charges_poly'


class ExtractionsPoly(TransactionsPoly):
    amount = models.FloatField()
    to_card = models.CharField(max_length=20)
    status = models.IntegerField(null=False, default=0)

    class Meta:
        db_table = 'extractions_poly'
