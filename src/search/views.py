from django.shortcuts import render
from products.models import Products

# Create your views here.
def SearchProductListView(request):
    query=request.GET.get('q')
    if query is not None:
        queryset=Products.objects.search(query)
        context={'object_list':queryset}
        return render(request,"search-view.html",context)
    else:
        return render(request,"search-view.html")
