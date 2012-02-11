# -*- coding: utf-8 -*-
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from myproject.agency.models import Clients
from myproject.yafunc import get_clients, create_client
from django.contrib.auth.models import User




def login(request):
    if 'username' in request.POST and 'password' in request.POST and request.POST['username'] and request.POST['password']:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            # Правильный пароль и пользователь "активен"
            auth.login(request, user)
            # Перенаправление на "правильную" страницу
            return HttpResponseRedirect("/agency/clients/")
        else:
            # Отображение страницы с ошибкой
            return render_to_response("agency/login.html", {'error': True})
        
    else:
        return render_to_response("agency/login.html")
        
        
    


def logout(request):
    auth.logout(request)
    # Перенаправление на страницу.
    return HttpResponseRedirect("/")


def show_clients(request):
    #clients=Clients.objects.filter(agent = request.user)
    agent = request.user.username
    clients = get_clients(agent)
    
    return render_to_response("agency/clients.html", {'clients':clients})
    
def new_client(request):
    
        if request.is_ajax():
            login = request.POST["cllogin"]    
            name = request.POST["clname"]
            sur = request.POST["clsur"]
            
            cl = create_client(login, name, sur)
            #res1 = str(cl)
            #res = '<div><div id="'+str(cl.Login)+'" class="client" >'+str(cl.Login)+': '+str(cl.FIO)+'</div></div>'

            res = '<tr id="'+str(cl.Login)+'" class="client"  height="23px" valign="center" >'
            res +=        '<td><span >'+str(cl.Login)+'</span></td>'
            res +=        '<td><span >'+str(cl.FIO)+'</span></td>'
            res +=        '<td><span class="info_but">info</span></td>'
            res +=        '<td><span class="del_but">del</span></td>'
            res +=        '<td><span class="choose_but">choose</span></td>'
            res += '</tr>'
            
            return HttpResponse(res)
        
def addclient_todb(request):
    if request.is_ajax():
        agent = request.user.username
        clients = get_clients(agent)
        postlogin = request.POST["login"]
        for item in clients:
            if item.Login == postlogin:
                try:
                    dbcl = Clients.objects.get(login=postlogin)
                except:
                    dbcl = Clients()
                    dbcl.login = item.Login
                    dbcl.name = item.FIO
                    dbcl.agent = request.user
                    dbcl.save()
                request.session['client'] = dbcl.id 
                return HttpResponse("1")
            
        return HttpResponse("-1")   
    
    

    
 
    