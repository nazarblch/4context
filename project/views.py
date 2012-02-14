# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template
from myproject.project.forms import Create_Company
from myproject.project.models import Company
from myproject.agency.models import Clients
from myproject.shop.models import ShopInfo

def get_default_info(request):
    clid = int(request.session['client'])
    cl = Clients.objects.get(id=clid)
    cllogin = cl.login
    shopname = request.session["shop"].name
    shopid = request.session["shop"].id

    return  {
        "username": request.user.username,
        "cllogin": cllogin,
        "shopname": shopname,
        "shopid": shopid,
        "clid": clid,
            }


def create_progect(request):

    def_templ_data = get_default_info(request)

    templ_dict = {}
    templ_dict.update(def_templ_data)
    return direct_to_template(request, 'project/index.html', templ_dict)




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
