from django.shortcuts import render,redirect
from . models import Source,UserIncome
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
import json,datetime
from django.http import JsonResponse

# Create your views here.
@login_required(login_url='/auth/login')
def index(request):
    sources=Source.objects.all()
    income=UserIncome.objects.filter(owner=request.user)
    paginator=Paginator(income,2)
    page_number=request.GET.get('page')
    page_obj=Paginator.get_page(paginator,page_number)
    currency=UserPreference.objects.get(user=request.user).currency
    context={
        'income':income,
        'page_obj':page_obj,
        'currency':currency,
    }
    return render(request,'income/index.html',context)

@login_required(login_url='/auth/login')
def add_income(request):
    sources=Source.objects.all()
    context={
        'sources':sources,
        'values':request.POST
    }
    if request.method=='GET':
        return render(request,'income/add_income.html',context)
    
    if request.method=='POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'income/add_income.html',context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']


        if not description:
            messages.error(request,'Description is required')
            return render(request,'income/add_income.html',context)
        
        UserIncome.objects.create(owner=request.user,amount=amount,date=date,source=source,description=description)
        messages.success(request,'Income saved successfully')
        return redirect('income')
    

@login_required(login_url='/auth/login')
def income_edit(request,id):
    sources=Source.objects.all()
    income= UserIncome.objects.get(pk=id)
    context={
        'income' : income,
        'values':income,
        'sources':sources,
    }
    
    if request.method=='GET':
        return render(request,'income/edit_income.html',context)
    
    if request.method=='POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'income/edit_income.html',context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']


        if not description:
            messages.error(request,'Description is required')
            return render(request,'income/edit_income.html',context)
        
        income.amount=amount
        income.description=description
        income.source=source
        income.date=date

        income.save()
        messages.success(request, 'Income Updated successfully')
        return redirect('income')

def delete_income(request,id):
    income=UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request,'Income deleted')
    return redirect('income')

#Important 
def search_income(request):
    if request.method=='POST':
       
        search_str=json.loads(request.body).get('searchText')

        income=UserIncome.objects.filter(
            amount__istartswith=search_str,owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str,owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str,owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str,owner=request.user)

        data=income.values()
        return JsonResponse(list(data),safe=False)
    
def income_source_summary(request):
    todays_date=datetime.date.today()
    six_months_ago=todays_date-datetime.timedelta(days=30*6)
    incomes=UserIncome.objects.filter(owner=request.user,date__gte=six_months_ago,date__lte=todays_date)
    final_rep={}

    def get_income(income):
        return income.source
    source_list=list(set(map(get_income,incomes)))

    def get_income_source_amount(source):
        amount = 0

        filtered_by_income=incomes.filter(source=source)
        
        for item in filtered_by_income:
            amount += item.amount
        return amount
    
    for x in incomes:
        for y in source_list:
            final_rep[y]=get_income_source_amount(y)

    return JsonResponse({'income_source_data':final_rep},safe=False)


def income_stats_view(request):
    return render(request,'income/income_stats.html')