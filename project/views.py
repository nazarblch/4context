# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from myproject.project.forms import Create_Company
from myproject.project.models import Company
from myproject.agency.models import Clients
from myproject.shop.models import ShopInfo


def sort_kw_phr(request):
#kdlsfdkfls
    clid = int(request.session['client'])
    cl = Clients.objects.get(id=clid)
    cllogin = cl.login
    shopname = request.session["shop"].name
    shopid = request.session["shop"].id


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
