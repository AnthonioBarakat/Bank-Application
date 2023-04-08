from django.contrib import admin
from .models import User, Admin, Loan, Service, Ask, Transactions, DebitCard, Address, Country

# anthonio
# 1234anthonio

# Register your models here.
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Loan)
admin.site.register(Service)
admin.site.register(Ask)
admin.site.register(Transactions)
admin.site.register(DebitCard)
admin.site.register(Address)
admin.site.register(Country)

