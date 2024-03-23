from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from . models import Category,firstExpenses
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json,datetime,csv
from django.http import FileResponse, JsonResponse,HttpResponse
from userpreferences.models import UserPreference
import xlwt
import io
from expense.settings import GTK_FOLDER
from django.template.loader import render_to_string
from weasyprint import HTML

from tempfile import NamedTemporaryFile
from django.db.models import Sum

# Create your views here.
@login_required(login_url='/auth/login')
def index(request):
    categories=Category.objects.all()
 
    expenses=firstExpenses.objects.filter(owner=request.user)
    paginator=Paginator(expenses,10)
    page_number=request.GET.get('page')
    page_obj=Paginator.get_page(paginator,page_number)
    currency=UserPreference.objects.get(user=request.user).currency
    context={
        'expenses':expenses,
        'page_obj':page_obj,
        'currency':currency,
    }
    return render(request,'expense/index.html',context)

@login_required(login_url='/auth/login')
def addexpense(request):
    categories=Category.objects.all()
    context={
        'categories':categories,
        'values':request.POST
    }
    if request.method=='GET':
        return render(request,'expense/addexpense.html',context)
    
    if request.method=='POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'expense/addexpense.html',context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']


        if not description:
            messages.error(request,'Description is required')
            return render(request,'expense/addexpense.html',context)
        
        firstExpenses.objects.create(owner=request.user,amount=amount,date=date,category=category,description=description)
        messages.success(request,'Expense saved successfully')
        return redirect('expense')
    
@login_required(login_url='/auth/login')
def expense_edit(request,id):
    categories=Category.objects.all()
    expense= firstExpenses.objects.get(pk=id)
    context={
        'expense' : expense,
        'values':expense,
        'categories':categories,
    }
    
    if request.method=='GET':
        return render(request,'expense/edit-expense.html',context)
    
    if request.method=='POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'expense/edit-expense.html',context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']


        if not description:
            messages.error(request,'Description is required')
            return render(request,'expense/edit-expense.html',context)
        
        expense.owner=request.user
        expense.amount=amount
        expense.description=description
        expense.category=category
        expense.date=date

        expense.save()
        messages.success(request,'Expense Updated successfully')
        return redirect('expense')

def delete_expense(request,id):
    expense=firstExpenses.objects.get(pk=id)
    expense.delete()
    messages.success(request,'Expense deleted')
    return redirect('expense')

#Important 
def search_expenses(request):
    if request.method=='POST':
       
        search_str=json.loads(request.body).get('searchText')

        expenes=firstExpenses.objects.filter(
            amount__istartswith=search_str,owner=request.user) | firstExpenses.objects.filter(
            date__istartswith=search_str,owner=request.user) | firstExpenses.objects.filter(
            description__icontains=search_str,owner=request.user) | firstExpenses.objects.filter(
            category__icontains=search_str,owner=request.user)

        data=expenes.values()
        return JsonResponse(list(data),safe=False)
    
def expense_category_summary(request):
    todays_date=datetime.date.today()
    six_months_ago=todays_date-datetime.timedelta(days=30*6)
    expenses=firstExpenses.objects.filter(owner=request.user,date__gte=six_months_ago,date__lte=todays_date)
    final_rep={}


    #helper function
    def get_category(expense):
        return expense.category
    
    category_list=list(set(map(get_category,expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category=expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount



    for x in expenses:
        for y in category_list:
            final_rep[y]=get_expense_category_amount(y)

    return JsonResponse({'expense_category_data':final_rep},safe=False)


def stats_view(request):
    return render(request,'expense/stats.html')


def export_csv(request):

    response= HttpResponse(content_type='text/csv')
    #we set the header is used to suggest a filename for the content being sent in the response.
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount','Description','Category','Date'])

    expenses = firstExpenses.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount,expense.description,expense.category,expense.date])

    return response

def export_excel(request):
    response= HttpResponse(content_type='application/ms-excel')

    response['Content-Disposition']='attachment; filename=Expenses'+ str(datetime.datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount','Description','Category','Date']

    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)

    font_style = xlwt.XFStyle()

    rows=firstExpenses.objects.filter(owner=request.user).values_list('amount','description','category','date')


    for row in rows:
        row_num += 1
        for col_num, value in enumerate(row):
            ws.write(row_num, col_num, str(value), font_style)

    wb.save(response)
    return response

from django.http import HttpResponse, FileResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
import datetime

def export_pdf(request):
    # Prepare the response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=Expenses'+ str(datetime.datetime.now())+'.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    expenses = firstExpenses.objects.filter(owner=request.user)

    if expenses:
        total_sum = expenses.aggregate(Sum('amount'))
    else:
        total_sum = 0

    context = {
        'expenses': expenses,
        'total': total_sum,
    }

    # Generate PDF content from HTML template
    html_string = render_to_string('expense/pdf-outlet.html', context)
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
    #return render(request, 'expense/pdf-outlet.html', context)
    
   
   
    





    