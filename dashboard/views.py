from django.shortcuts import render
from django.http import HttpResponse
from firstexpense.models import firstExpenses
from firstexpense.views import expense_category_summary
from django.db.models import Sum



# Create your views here.
def index(request):

    expenses=firstExpenses.objects.filter(owner=request.user)

    if expense_category_summary:
        total_sum = expenses.aggregate(Sum('amount'))
        
    else:
        total_sum = 0
       
    
    context = {
        'expenses': expenses,
        'total': total_sum,
        

    }
    return render(request,'dashboard/index.html',context)

