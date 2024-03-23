from django.shortcuts import render,redirect
from . models import Source,UserIncome
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
import json,datetime,csv
from django.http import JsonResponse

import xlwt
import io
from django.template.loader import render_to_string
from weasyprint import HTML

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
        amount_income = 0

        filtered_by_income=incomes.filter(source=source)
        
        for item in filtered_by_income:
            amount_income += item.amount
        return amount_income
    
    for x in incomes:
        for y in source_list:
            final_rep[y]=get_income_source_amount(y)

    return JsonResponse({'income_source_data':final_rep},safe=False)


def income_stats_view(request):
    return render(request,'income/income_stats.html')

# excel
def export_csv(request):

    response= HttpResponse(content_type='text/csv')
    #we set the header is used to suggest a filename for the content being sent in the response.
    response['Content-Disposition']='attachment; filename=Income '+str(datetime.datetime.now())+'.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount','Description','Source','Date'])

    income = UserIncome.objects.filter(owner=request.user)

    for income in income:
        writer.writerow([income.amount,income.description,income.source,income.date])

    return response


# excel 

def export_excel(request):
    response= HttpResponse(content_type='application/ms-excel')

    response['Content-Disposition']='attachment; filename=Income '+ str(datetime.datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Income')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount','Description','Source','Date']

    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)

    font_style = xlwt.XFStyle()

    rows=UserIncome.objects.filter(owner=request.user).values_list('amount','description','source','date')


    for row in rows:
        row_num += 1
        for col_num, value in enumerate(row):
            ws.write(row_num, col_num, str(value), font_style)

    wb.save(response)
    return response



from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import datetime
from django.db.models import Sum

def export_pdf(request):
    # Prepare the response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=Income'+ str(datetime.datetime.now())+'.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    income = UserIncome.objects.filter(owner=request.user)

    if income:
        total_sum_income = income.aggregate(Sum('amount'))
    else:
        total_sum_income = 0

    context = {
        'income': income,
        'total_income': total_sum_income,
    }

    # Generate PDF content from HTML template
    html_string = render_to_string('income/pdf-outlet.html', context)
    print("\n\n\n\nthis is html String\n\n\n\n",html_string)
    html = HTML(string=html_string)
    print("\n\n\n\nthis is html\n\n\n\n",html)
    result = html.write_pdf()

    size_in_bytes = len(result)
    print("Size of PDF content:", size_in_bytes, "bytes")
    #print((result))

    pdf_file = io.BytesIO(result)

    # Set response content
    response.write(pdf_file.getvalue())
    return response