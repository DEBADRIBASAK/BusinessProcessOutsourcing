from django.contrib import admin
from .models import Company,Employee,BPO_Employee,AccountingInfo
# Register your models here.
admin.site.register(Company)
admin.site.register(Employee)
admin.site.register(BPO_Employee)
admin.site.register(AccountingInfo)