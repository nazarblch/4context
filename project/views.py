# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from myproject.project.forms import Create_Company
from myproject.project.models import Company
from myproject.agency.models import Clients
from myproject.shop.models import ShopInfo


def index(request):
    clid = int(request.session['client'])
    cl = Clients.objects.get(id=clid)
    cllogin = cl.login
    
    if "shop" in request.session and request.session["shop"].client != cl:
        del request.session["shop"] 
    
    if "shop" not in request.session:
        shopname = "New shop"
        request.session["shop"] = ShopInfo(name = "def", company = "def", url = "def", email = "def", client=cl)
        request.session["shop"].save()
        
    else:
        shopname = request.session["shop"].name
    
    return render_to_response('project/index.html', {"cllogin": cllogin, "shop": shopname, "clid": clid })


def create_company(request):
    if request.method == 'POST':
        form=Create_Company(request.POST)
        if form.is_valid():
            comp = form.save()
            comp.ya_id = 0
            comp.save() 
            #return HttpResponse(str(comp.id))
            return HttpResponseRedirect('/object')

        else:
            return HttpResponse(str(form.errors))
    else:
        form=Create_Company(request.POST)
    return render_to_response('project/create_company.html', {"form": form})
