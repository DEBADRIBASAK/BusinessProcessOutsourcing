from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .models import Company,Employee,BPO_Employee,AccountingInfo
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import Http404,HttpResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import pandas as pd
import numpy as np
import os
import datetime
# Create your views here.
def register(request):
	if request.method=='POST':
		if User.objects.filter(username=request.POST['Username']).exists():
			return render(request,'signup1.html',{'exists':True})
		obj = User()
		obj.username = request.POST['Username']
		password = request.POST['Password']
		password2 = request.POST['Confirm Password']
		if(password!=password2):
			return render(request,'signup1.html',{'is_wrong':True})
		obj.set_password(request.POST['Password'])
		

		obj.save()
		obj1 = None
		com = None
		if 'Organization' in request.POST:
			obj1 = Company()
			obj1.company_code = request.POST['Company Code']
		else:
			obj1 = Employee()
			com = Company.objects.get(company_code=request.POST['Company Code'])
			obj1.company = com
		obj1.username = obj
		obj1.Name = request.POST['Name']
		obj1.PhoneNo = request.POST['Phone']
		obj1.EmailID = request.POST['EmailID']
		obj1.save()
		return redirect('/HRO/log_in/')#request,'login1.html',{})
	return render(request,'signup1.html',{'is_wrong': False})

def LogIn(request):
	a = request.user.is_authenticated
	if a and request.user.is_staff:
		logout(request)
		return render(request,'home.html',{})
	elif a:
		usr = request.user
		isit = False
		obj = Company.objects.filter(username=usr)
		if obj.exists():
			obj = Company.objects.get(username=usr)
			return render(request,'profile1.html',{'Company':obj,'isit':True})
		else:
			#print('hello!')
			obj = Employee.objects.get(username=usr)
			return render(request,'EmpProfile1.html',{'Company':obj,'isit':False,'CompName': obj.company.Name})
	elif request.method=='POST':
		#print('hello')
		name = request.POST['username']
		passwrd = request.POST['password']
		try:
			obj1 = authenticate(username=name,password=passwrd)
			if obj1 is None:
				raise User.DoesNotExist
		except User.DoesNotExist:
			return HttpResponse('<h1>User does not exist!</h1>')
		login(request,obj1)
		#obj2 = Company.objects.get(username=obj1)
		isit = False
		if 'Org' in request.POST:
			obj2 = Company.objects.get(username=obj1)
			return render(request,'profile1.html',{'Company': obj2,'isit':True})
		else:
			#print("I am Here")
			obj2 = Employee.objects.get(username=obj1)
			return render(request,'EmpProfile1.html',{'Company': obj2,'isit':False,'CompName': obj2.company.Name})
	return render(request,'login1.html',{})

def home(request):
	return render(request,'home.html',{})


def LogOut(request):
	logout(request)
	return redirect('/HRO/home')
@login_required()
def Upload(request):
	#print("\n\n\nI am in upload")
	obj = request.user
	obj1 = Company.objects.get(username=obj)
	if request.method=='POST' and request.FILES:
		file = request.FILES.get('HR_Info')
		print("file = ",str(file))
		if file:
			if(not str(file).endswith('.csv')):
				return HttpResponse("<h1>Format must be .csv</h1>")
			fs = FileSystemStorage()
			path = 'docs/'+request.POST['csrfmiddlewaretoken']+file.name
			if obj1.HR_Info:
				path1 = settings.MEDIA_ROOT+'/'+str(obj1.HR_Info)
				os.remove(path1)
			obj1.HR_Info = path
			fs.save(path,file)
		obj1.save()
		return render(request,'profile.html',{'Company':obj1})
	return render(request,'upload.html',{})

@login_required()
def HR_Information(request):
	obj = request.user
	obj1 = Company.objects.get(username=obj)
	if request.method=='GET':
		if obj1.HR_Info:
			path = settings.MEDIA_ROOT+'/'+str(obj1.HR_Info)
			dateparse = lambda dates: [pd.datetime.strptime(d, '%d/%m/%Y') for d in dates]
			data = pd.read_csv(path, parse_dates=['JoiningDate'],date_parser=dateparse)
			data = np.array(data)
			data = np.array(data)
			salaries = np.sort(data[:,4])#,dtype=np.float64)
			#salaries = np.sort(salaries)
			salaries = np.array_split(salaries,3)
			l = []
			for i in range(len(salaries)):
				l.append(np.mean(salaries[i]))#(dtype=np.float64))
			#print("\n\nl = ",l)
			return render(request,'info.html',{'l':l,'data':data})
		else:
			return HttpResponse('<h1>You Have not uploaded HR Info yet</h1>')
	elif request.method=='POST':
		if obj1.HR_Info:
			path = settings.MEDIA_ROOT+'/'+str(obj1.HR_Info)
			dateparse = lambda dates: [pd.datetime.strptime(d, '%d/%m/%Y') for d in dates]
			data = pd.read_csv(path, parse_dates=['JoiningDate'],date_parser=dateparse)
			#print("data = ",data)
			EmployeeID = False
			Name = False
			JoiningDate = False
			Age = False
			Salary = False
			if 'EmployeeID' in request.POST:
				EmployeeID = True
				data = data.sort_values(['EmployeeID'],ascending=[1])
			elif 'Name' in request.POST:
				Name = True
				data = data.sort_values(['Name'],ascending=[1])
			elif 'JoiningDate' in request.POST:
				JoiningDate = True
				data = data.sort_values(['JoiningDate'],ascending=[1])
			elif 'Age' in request.POST:
				Age = True
				data = data.sort_values(['Age'],ascending=[1])
			elif 'Salary' in request.POST:
				Salary = True
				data = data.sort_values(['Salary'],ascending=[1])
			data = np.array(data)
			salaries = np.sort(data[:,4])
			salaries = np.array_split(salaries,3)
			l = []
			for i in range(len(salaries)):
				l.append(np.mean(salaries[i]))
			print("\n\nl = ",l)
			return render(request,'info.html',{'l':l,'data':data,'E':EmployeeID,'N':Name,'J':JoiningDate,'A':Age,'S':Salary})
		else:
			return HttpResponse('<h1>You Have not uploaded HR Info yet</h1>')
	return render(request,'profile.html',{'Company':obj1})


@login_required
def Upload_Acc_Info(request):
	obj = request.user
	if (request.method=='POST'):
		obj1 = Company.objects.get(username=obj)
		flname = request.FILES.get('Acc')
		if flname:
			if(not str(flname).endswith('.csv')):
				return HttpResponse("<h1>Format must be .csv</h1>")
			obj2 = None
			if AccountingInfo.objects.filter(company_code=obj1,date=(datetime.date.today().year)).exists():
				obj2 = AccountingInfo.objects.get(company_code=obj1,date=(datetime.date.today().year))
				path1 = settings.MEDIA_ROOT+'/'+str(obj2.info)
				print("\n\n\nPath = ",path1)
				obj2.delete()
				os.remove(path1)
			fs = FileSystemStorage()
			path = 'ecmdocs/'+request.POST['csrfmiddlewaretoken']+str(flname)
			obj3 = AccountingInfo()
			obj3.company_code = obj1
			obj3.info = path
			obj3.date = request.POST['year']
			fs.save(path,flname)
			obj3.save()
			return redirect('/HRO/log_in')
		else:
			return HttpResponse('<h1>File not there!</h1>')
	return render(request,'upload_account.html',{})

def preprocess(a):
	label1 = []
	label2 = []
	arr1 = []
	arr2 = []
	for i in range(len(a)):
		if int(a[i,1])!=0:
			label1.append(a[i,0])
			arr1.append(int(a[i,1]))
		else:
			label2.append(a[i,0])
			arr2.append(int(a[i,2]))
	return label1,label2,list(arr1),list(arr2)

@login_required
def Acc_Info(request):
	obj = request.user
	if(request.method=='GET'):
		obj1 = Company.objects.get(username=obj)
		dt = int(datetime.date.today().year)
		obj2 = AccountingInfo.objects.filter(company_code=obj1,date=dt)
		if obj2.exists():
			obj2 = AccountingInfo.objects.get(company_code=obj1,date=dt)
			path = settings.MEDIA_ROOT+'/'+str(obj2.info)
			# names = ['Name of Account','Credit','Debit']
			data = pd.read_csv(path)
			data = np.array(data)
			# dr = list(data[:,1])
			# cr = list(data[:,2])
			label1,label2,dr,cr = preprocess(data)
			# print("\n\ncr = ",cr)
			# print("\n\ndr = ",dr)
			Debit_sum = data[:,1].sum(dtype=np.float64)
			Credit_sum = data[:,2].sum(dtype=np.float64)
			return render(request,'Acc_Info.html',{'f':True,'lc':len(cr),'lr':len(dr),'label1':label1,'label2':label2,'cr':cr,'dr':dr,'year':datetime.date.today().year,'data':data,'Suspense':Credit_sum-Debit_sum,'Credit_sum':Credit_sum,'Debit_sum':Debit_sum})
		else:
			return render(request,'Acc_Info.html',{'f':False,'year':dt})
	else:
		obj1 = Company.objects.get(username=obj)
		dt = request.POST['year']
		obj2 = AccountingInfo.objects.filter(company_code=obj1,date=dt)
		if obj2.exists():
			obj2 = AccountingInfo.objects.get(company_code=obj1,date=dt)
			path = settings.MEDIA_ROOT+'/'+str(obj2.info)
			data = pd.read_csv(path)
			data = np.array(data)
			label1,label2,dr,cr = preprocess(data)
			# print("\n\ncr = ",cr)
			# print("\n\ndr = ",dr)
			Credit_sum = data[:,2].sum(dtype=np.float64)
			Debit_sum = data[:,1].sum(dtype=np.float64)
			return render(request,'Acc_Info.html',{'f':True,'lc':len(cr),'lr':len(dr),'label1':label1,'label2':label2,'cr':cr,'dr':dr,'year':dt,'data':data,'Suspense':Credit_sum-Debit_sum,'Credit_sum':Credit_sum,'Debit_sum':Debit_sum})
		else:
			return render(request,'Acc_Info.html',{'f':False,'year':dt})
	return redirect('/HRO/log_in/')

@login_required()
def Request_HR(request):
	if (request.method=='POST'):
		dt = int(request.POST.get('service'))
		obj = None
		print("dt = ",dt)
		if(dt==0):
			obj = BPO_Employee.objects.filter(EmpType='INST',isAvail=True)
		elif(dt==1):
			obj = BPO_Employee.objects.filter(EmpType='MAIN',isAvail=True)
		else:
		 	obj = BPO_Employee.objects.filter(EmpType='SURV',isAvail=True)
		return render(request,'Available.html',{'data':obj})
		print("\n\n\n",obj)
	return render(request,'upload.html',{})

@login_required()
def BookEmployee(request,pk):
		obj = BPO_Employee.objects.get(EmployeeCode=pk)
		obj.isAvail = False
		obj.save()
		return render(request,'Available.html',{})

@login_required()
def HCA_Employee(request):
	usr = request.user
	obj = Employee.objects.get(username=usr)
	return render(request,'HCA_Employee.html',{'E':obj})

@login_required()
def Deposit(request):
	if(request.method=="POST"):
		usr = request.user
		obj = Employee.objects.get(username=usr)
		obj.Deposit+=int(request.POST['Amount'])
		obj.save()
	return redirect('/HRO/HCA_Employee/')

@login_required()
def RequestHCA(request):
	if(request.method=='POST'):
		usr = request.user
		obj = Employee.objects.get(username=usr)
		obj.HCARequest = 2
		obj.RequestAmount = int(request.POST['Amount'])
		obj.save()
	return redirect('/HRO/HCA_Employee')

@login_required()
def HCA_Company(request):
	usr = request.user
	obj = Company.objects.get(username=usr)
	obj2 = Employee.objects.filter(company=obj,HCARequest=2)
	return render(request,'HCA.html',{'data':obj2})

@login_required()
def ProcessHCA(request,pk,flag):
	usr = pk
	obj = User.objects.get(username=usr)
	obj1 = Employee.objects.get(username=obj)
	print('flag = ',flag)
	if(int(flag)==1):
		obj1.HCARequest = 4
		obj1.Deposit-=obj1.RequestAmount
		obj1.RequestAmount = 0
	else:
		obj1.HCARequest = 3
	obj1.save()
	return redirect('/HRO/HCA_Company/')

def Acc_Info1(request):
	obj = request.user
	if(request.method=='GET'):
		obj1 = Employee.objects.get(username=obj)
		dt = int(datetime.date.today().year)
		obj2 = AccountingInfo.objects.filter(company_code=obj1.company,date=dt)
		if obj2.exists():
			obj2 = AccountingInfo.objects.get(company_code=obj1.company,date=dt)
			path = settings.MEDIA_ROOT+'/'+str(obj2.info)
			# names = ['Name of Account','Credit','Debit']
			data = pd.read_csv(path)
			data = np.array(data)
			# dr = list(data[:,1])
			# cr = list(data[:,2])
			label1,label2,dr,cr = preprocess(data)
			print("\n\ncr = ",cr)
			print("\n\ndr = ",dr)
			Debit_sum = data[:,1].sum(dtype=np.float64)
			Credit_sum = data[:,2].sum(dtype=np.float64)
			return render(request,'Acc_Info1.html',{'f':True,'lc':len(cr),'lr':len(dr),'label1':label1,'label2':label2,'cr':cr,'dr':dr,'year':datetime.date.today().year,'data':data,'Suspense':Credit_sum-Debit_sum,'Credit_sum':Credit_sum,'Debit_sum':Debit_sum})
		else:
			return render(request,'Acc_Info1.html',{'f':False,'year':dt})
	else:
		obj1 = Employee.objects.get(username=obj)
		dt = request.POST['year']
		obj2 = AccountingInfo.objects.filter(company_code=obj1.company,date=dt)
		if obj2.exists():
			obj2 = AccountingInfo.objects.get(company_code=obj1.company,date=dt)
			path = settings.MEDIA_ROOT+'/'+str(obj2.info)
			data = pd.read_csv(path)
			data = np.array(data)
			label1,label2,dr,cr = preprocess(data)
			print("\n\ncr = ",cr)
			print("\n\ndr = ",dr)
			Credit_sum = data[:,2].sum(dtype=np.float64)
			Debit_sum = data[:,1].sum(dtype=np.float64)
			return render(request,'Acc_Info1.html',{'f':True,'lc':len(cr),'lr':len(dr),'label1':label1,'label2':label2,'cr':cr,'dr':dr,'year':dt,'data':data,'Suspense':Credit_sum-Debit_sum,'Credit_sum':Credit_sum,'Debit_sum':Debit_sum})
		else:
			return render(request,'Acc_Info1.html',{'f':False,'year':dt})
	return redirect('/HRO/log_in/')
