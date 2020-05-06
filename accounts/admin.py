from django.contrib import admin

# Register your models here.
from .models import Charges,Accounts,Extractions,Purchases,Transactions,Products

admin.site.site_header = 'Accounts Admin'
admin.site.site_title = 'Accounts Admin Area'
admin.site.index_title = 'Welcome to Accounts Admin Area'


for mod in [Charges,Accounts,Extractions,Purchases,Transactions,Products]:
    admin.site.register(mod)
#
# admin.site.register(Charge,Accounts,Extractions,Purchases)
#
#
# class TransactionsInline(admin.TabularInline):
#     model = Transactions
#     extra = 3
#
#
# class AccountsAdmin(admin.ModelAdmin):
#     fieldsets = [(None, {'fields': ['name']}),
#                  ('Balance', {'fields': ['balance'], 'classes':['collapse']})
#                  ]
#     inlines = [TransactionsInline]
#
#
# admin.site.register(Accounts,AccountsAdmin)
