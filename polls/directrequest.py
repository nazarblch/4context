#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse

from django.core.context_processors import csrf
import sys

def request(request):

        templ_num = int(request.GET['templ'])
        
        if   templ_num == 1:  # create company
            templ = "create_company.html"
           
        elif templ_num == 2:  # update company 
            templ = "update_company.html"

        elif templ_num == 3:  # create banner
            templ = "create_banner.html"
          
        elif templ_num == 4:  # get synonyms
            templ = "get_synonyms.html"
            
        elif templ_num == 5:  # set rate
            templ = "set_rate.html"
        
        elif templ_num == 6:  # set company rate
            templ = "set_company_rate.html"
            
        elif templ_num == 7:  # add phrase
            templ = "add_phrase.html"
        
        return render_to_response('polls/'+templ)
      


