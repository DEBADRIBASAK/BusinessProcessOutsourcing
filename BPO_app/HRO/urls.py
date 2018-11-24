from django.urls import path
from . import views

urlpatterns = [
path('register/',views.register,name='register'),
path('home/',views.home,name='home'),
path('log_in/',views.LogIn,name='log_in'),
path('logout/',views.LogOut,name='log_out'),
path('upload/',views.Upload,name='upload'),
path('Info/',views.HR_Information,name='show'),
path('Acc_Info/',views.Acc_Info,name='Acc_Info'),
path('Upload_Acc/',views.Upload_Acc_Info,name='Upload_Acc'),
path('Request_HR/',views.Request_HR,name='Request_HR'),
path('Book/(?P<pk>[0-9A-Z]+)/',views.BookEmployee,name='Book'),
path('Deposit/',views.Deposit,name="Deposit"),
path('HCA_Employee/',views.HCA_Employee,name="HCA_Employee"),
path('RequestHCA/',views.RequestHCA,name="RequestHCA"),
path('HCA_Company/',views.HCA_Company,name="HCA_Company"),
path('ProcessHCA/(?P<pk>[a-zA-Z0-9])/(?P<flag>[0-9]/',views.ProcessHCA,name="ProcessHCA"),
path('Acc_Info1/',views.Acc_Info1,name="Acc_Info1"),
]