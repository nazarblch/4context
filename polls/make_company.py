#!/usr/bin/python
# -*- coding: UTF-8 -*-
from django.shortcuts import render_to_response, get_object_or_404

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from django.core.context_processors import csrf

import cgi
import sys
from datetime import date

from suds.client import Client
from suds.cache import DocumentCache
from suds.sax.element import Element
from suds import WebFault

import logging
logging.basicConfig(level=logging.INFO)

logging.getLogger('suds.client').setLevel(logging.DEBUG)

#logging.getLogger('suds.client').setLevel(logging.CRITICAL)
    

#2. Плагин для коррекции ответов
#=========================================================
from suds.plugin import *
class NamespaceCorrectionPlugin(MessagePlugin):
    def received(self, context):
        context.reply = context.reply.replace('"http://namespaces.soaplite.com/perl"','"API"')


#3. Экземпляр класса suds.Client
#=========================================================
#api = Client('http://soap.direct.yandex.ru/wsdl/v4/', plugins = [NamespaceCorrectionPlugin()])
'''песочница'''
api = Client('https://localhost/send.wdsl', plugins = [NamespaceCorrectionPlugin()])


api.set_options(cache=DocumentCache())


#4. Метаданные в заголовках SOAP-пакетов
#=========================================================
locale = Element('locale').setText('en')
api.set_options(soapheaders=(locale))


#5. Авторизация по SSL-сертификатам Яндекс.Директа
#=========================================================
'''
KEYFILE = '/home/nazar/ya_cert/private.key'
CERTFILE = '/home/nazar/ya_cert/cert.crt' 

import httplib, urllib2

class YandexCertConnection(httplib.HTTPSConnection):
    def __init__(self, host, port=None, key_file=KEYFILE, cert_file=CERTFILE, timeout=30):
        httplib.HTTPSConnection.__init__(self, host, port, key_file, cert_file)

class YandexCertHandler(urllib2.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(YandexCertConnection, req) 
    https_request = urllib2.AbstractHTTPHandler.do_request_

api.options.transport.urlopener = urllib2.build_opener(*[YandexCertHandler()])
'''

login = Element('login').setText('genromix')
token = Element('token').setText('895750b6f51d494e91e6a59e06a11e51')
appId = Element('application_id').setText('1ba17deb0ba44efe9edf9b329269ca75')
locale = Element('locale').setText('en')
api.set_options(soapheaders=(login, token, appId, locale))


#6. Функция для вызова методов API
#=========================================================
def directRequest(methodName, params):
    '''
    Вызов метода API Яндекс.Директа:
       api - экземпляр класса suds.Client
       methodName - имя метода
       params - входные параметры
    В случае ошибки программа завершается,
    иначе возвращается результат вызова метода
    '''
    try:
        result = api.service['APIPort'][methodName](params)
        return result
    except WebFault, err:
        return unicode(err)
    except:
        err = sys.exc_info()[1]
        return 'Other error: ' + str(err)
    exit(-1)
    

#company
#=========================================================

def create_company(request):
        try:

                strategy = { "StrategyName": request.POST['strategy'], }

                if request.POST['mxprice'] != "" and request.POST['mxprice'] != None:      
	        	strategy.update({"MaxPrice": float(request.POST['mxprice']) })     
                if request.POST['avprice'] != "" and request.POST['avprice'] != None:      
	        	strategy.update({"AveragePrice": float(request.POST['avprice'])})         
                if request.POST['weeklimit'] != "" and request.POST['weeklimit'] != None:      
	        	strategy.update({"WeeklySumLimit": float(request.POST['weeklimit'])})         
                if request.POST['weekclicks'] != "" and request.POST['weekclicks'] != None:      
	        	strategy.update({"ClicksPerWeek": int(request.POST['weekclicks'])}) 

                MinusKw = request.POST.getlist('MinusKw')
                

		params = {
		   "Login": unicode(request.POST['login']),
		   "CampaignID": 0,
		   "Name": unicode(request.POST['name']),
		   "FIO": unicode(request.POST['fio']),
		   "Strategy":strategy,
		   "EmailNotification":{
		      "MoneyWarningValue":10,
		      "WarnPlaceInterval":60,
		      "SendWarn":"Yes",
		      "Email":unicode(request.POST['email'])
		   },
                   "StatusBehavior": "Yes",
                   "StatusContextStop": "No",
                   "ContextLimit": "Limited",
		   "ContextLimitSum": int(request.POST['contextlimitsum']),
                   "ContextPricePercent": int(request.POST['contextpricepercent']),
                   "AutoOptimization":  "No",
		   "StatusMetricaControl": "Yes",
		   "StatusOpenStat": "No",
                   "ConsiderTimeTarget": "Yes", 
		   "AddRelevantPhrases": "Yes",
		   "RelevantPhrasesBudgetLimit": int(request.POST['RelevantPhrasesBudgetLimit']),
                   "MinusKeywords": MinusKw,  

		}


                if int(request.POST['TimeTarget']) == 1:
                        timetarget = {
				"ShowOnHolidays": request.POST['holidays'],
				"HolidayShowFrom": int(request.POST['hol_from']),
				"HolidayShowTo": int(request.POST['hol_to']),
				"TimeZone": "Europe/Moscow",
			}
 
                        dayshours = []
		        days = request.POST.getlist('days')

		        for d in days:
                        	dh = {"Hours": (d.split('_')[1]).split(','), "Days": (d.split('_')[0]).split(',') }
				dayshours.append(dh) 
			
			timetarget.update({"DaysHours":dayshours})
                        params.update({"TimeTarget":timetarget})
		
		if len(request.POST['DisabledDomains']) > 0:
                        params.update({"DisabledDomains": unicode(request.POST['DisabledDomains']) })
              		       

		campaignId = directRequest('CreateOrUpdateCampaign', params)
		return HttpResponse( str(campaignId) )
	        
	except Exception, e:
		return HttpResponse('Create Company SOAP Fault: '+str(e))



def company_params(id):

    params = {'CampaignIDS': [int(id)]}
    campaignsParams = directRequest('GetCampaignsParams', params)
    params = campaignsParams[0]
        
    return params 

def user_companies_info(request):

        param = {
		"Logins": request.POST.getlist('logins'),
    
		"Filter": {
			"StatusModerate": request.POST.getlist('fmoderate'),
			"IsActive": request.POST.getlist('fisactive'),
			"StatusArchive": request.POST.getlist('farchive'),
			"StatusActivating": request.POST.getlist('factivating'),
			"StatusShow": request.POST.getlist('fshow')
		}
                 }
    
        if int(request.POST['filter']) == 1:
        
            filt = {}
            if len(request.POST.getlist('fmoderate')) > 0 :      
                        filt.update({"StatusModerate": request.POST.getlist('fmoderate') }) 
            if len(request.POST.getlist('fisactive')) > 0 :      
                        filt.update({"IsActive": request.POST.getlist('fisactive') }) 
            if len(request.POST.getlist('farchive')) > 0 :      
                        filt.update({"StatusArchive": request.POST.getlist('farchive') }) 
            if len(request.POST.getlist('factivating')) > 0 :      
                        filt.update({"StatusActivating": request.POST.getlist('factivating') }) 
            if len(request.POST.getlist('fshow')) > 0 :      
                        filt.update({"StatusShow": request.POST.getlist('fshow') }) 

            param.update({"Filter": filt})
            
        
        result = directRequest('GetCampaignsListFilter', param)
        return result  

  
def update_company(request): 

   try:      
        params = {'CampaignIDS': [int(request.POST['Id'])]}
        campaignsParams = directRequest('GetCampaignsParams', params)
        
        #изменить параметры
        params = campaignsParams[0]
        
        #стратегия
        if request.POST['strategy'] != "" and request.POST['strategy'] != None:
        	params.Strategy.StrategyName = request.POST['strategy']

                if request.POST['mxprice'] != "" and request.POST['mxprice'] != None:      
	        	params.Strategy.MaxPrice = float(request.POST['mxprice'])     
                if request.POST['avprice'] != "" and request.POST['avprice'] != None:      
	        	params.Strategy.AveragePrice = float(request.POST['avprice'])         
                if request.POST['weeklimit'] != "" and request.POST['weeklimit'] != None:      
	        	params.Strategy.WeeklySumLimit = float(request.POST['weeklimit'])         
                if request.POST['weekclicks'] != "" and request.POST['weekclicks'] != None:      
	        	params.Strategy.ClicksPerWeek = int(request.POST['weekclicks'])  

        #минус слова
        params.MinusKeywords = [] 
        MinusKw = request.POST.getlist('MinusKw')
        for word in MinusKw:
            params.MinusKeywords.append(unicode(word))

        #время            
        if int(request.POST['TimeTarget']) == 1:
                #выходные
                if request.POST['holidays'] != "" and request.POST['holidays'] != None:        
			params.TimeTarget.ShowOnHolidays = request.POST['holidays']
			if request.POST['hol_from'] != "" and request.POST['hol_from'] != None:
				params.TimeTarget.HolidayShowFrom = int(request.POST['hol_from'])
                        if request.POST['hol_to'] != "" and request.POST['hol_to'] != None:
				params.TimeTarget.HolidayShowTo = int(request.POST['hol_to'])

                #все дни
                if request.POST['days'] != "" and request.POST['days'] != None:        
						
                        days = request.POST.getlist('days')
                        params.TimeTarget.DaysHours = [] 

			i = 0
		        for d in days:
                                params.TimeTarget.DaysHours[i].Days = (d.split('_')[0]).split(',')
				params.TimeTarget.DaysHours[i].Hours = (d.split('_')[1]).split(',')
                        	i = i + 1

	#email
	if request.POST['email'] != "" and request.POST['email'] != None:
		params.EmailNotification.Email = request.POST['email']

	# % расхода и % цены клика в рекламной сети яндех :::10
        if request.POST['contextlimitsum'] != "" and request.POST['contextlimitsum'] != None:
		params.ContextLimitSum = int(request.POST['contextlimitsum'])
	if request.POST['contextpricepercent'] != "" and request.POST['contextpricepercent'] != None:
        	params.ContextPricePercent = int(request.POST['contextpricepercent'])
        
        #релевантные фразы
	if len(request.POST['RelevantPhrases']) > 0:
		params.AddRelevantPhrases = request.POST['RelevantPhrases']
		params.RelevantPhrasesBudgetLimit = int(request.POST['RelevantPhrasesBudgetLimit'])
	
        #враждебные домены
        if len(request.POST['DisabledDomains']) > 0:
                params.DisabledDomains = unicode(request.POST['DisabledDomains'])
              


        #сохранить параметры в API
        result = directRequest('CreateOrUpdateCampaign', params)
        return HttpResponse(str(result))

   except Exception, e:
	return HttpResponse('Update company Id: ' + request.POST['Id'] + ' SOAP Fault: '+str(e))

       
def company_balance(request):

    nums = request.POST.getlist("num")

    i = 0
    for n in nums:
        nums[i] = int(n)
        i = i + 1

    params = nums

    res = directRequest('GetBalance', params) 
    return HttpResponse(str(res))  


def company_archive(Id):

    cid = int(Id)
    
    params = {
              'CampaignID': cid
    }

    res = directRequest('ArchiveCampaign', params) 
    return res  

def company_unarchive(Id):

    cid = int(Id)
    
    params = {
              'CampaignID': cid
    }

    res = directRequest('UnArchiveCampaign', params) 
    return res  


def company_del(Id):

    cid = int(Id)
    
    params = {
              'CampaignID': cid
    }
    res = directRequest('DeleteCampaign', params) 
    return res

def company_resume(Id):

    cid = int(Id)
    
    params = {
              'CampaignID': cid
    }

    res = directRequest('ResumeCampaign', params) 
    return res  

def company_stop(Id):

    cid = int(Id)
    
    params = {
              'CampaignID': cid
    }

    res = directRequest('StopCampaign', params) 
    return res  

 
def company_stat(Ids, startp, endp):
    
    params = {
              "CampaignIDS": [int(Id) for Id in Ids],
              "StartDate": startp,   #'2011-05-14'
              "EndDate": endp
    }

    res = directRequest('GetSummaryStat', params) 
    return res  
 
def company_metr_goals(Id):

    cid = int(Id)
    
    params = {
              'CampaignID': cid
    }

    res = directRequest('GetStatGoals', params) 
    return res  

 
def set_company_rate(request):
      
        params = {
          'CampaignID': int(request.POST['Id']),
          'Mode': unicode(request.POST['mode']),
          'PriceBase': unicode(request.POST['pricebase']),
          'ProcBase': unicode(request.POST['procbase']),
          'Proc': int(request.POST['proc']),
          'MaxPrice': float(request.POST['maxprace']),
        }    
        
        res = directRequest('SetAutoPrice', params)
        response = ''
        for s in res:
           response += s.encode('utf-8')
  
        return HttpResponse(response)    
 
 
  
#banner
#=========================================================
            
        
def create_banner(request):
      
    try:
        
        banner = api.factory.create('BannerInfo')
        banner.CampaignID = int(request.POST['Id'])
        banner.BannerID = 0
        banner.Title = unicode(request.POST['title'])
        banner.Text = unicode(request.POST['text'])
        banner.Href = unicode(request.POST['url'])
        banner.Geo = request.POST['geo']
        
        banner.Sitelinks = []
        
        Sitelinks = request.POST.getlist('Sitelinks')
        i = 0
        for title_hr in Sitelinks:
            banner.Sitelinks[i].Title = unicode(title_hr.split("&_&")[0]);  
            banner.Sitelinks[i].Href = unicode(title_hr.split("&_&")[1]);
            i = i + 1
        
        if int(request.POST["ContactInfo"]) == 1:

            banner.ContactInfo.Country = unicode(request.POST['country'])
            banner.ContactInfo.CountryCode = request.POST['countrycode']
            banner.ContactInfo.City = unicode(request.POST['city'])
            banner.ContactInfo.CityCode = request.POST['citycode']
            banner.ContactInfo.Phone = request.POST['phone']
            banner.ContactInfo.CompanyName = unicode(request.POST['companyname'])
            banner.ContactInfo.WorkTime = unicode(request.POST['worktime'])
            if len(request.POST['phoneext']) > 0:
                banner.ContactInfo.PhoneExt = request.POST['phoneext']
            if len(request.POST['extramessage']) > 0:
                banner.ContactInfo.ExtraMessage = unicode(request.POST['extramessage'])
            if len(request.POST['contactemail']) > 0:    
                banner.ContactInfo.ContactEmail = unicode(request.POST['contactemail'])

        else:
            del(banner.ContactInfo)

        
        banner.MinusKeywords = []
        MinusKw = request.POST.getlist('MinusKw')
        for word in MinusKw:
            banner.MinusKeywords.append(unicode(word))
        
        #поисковая фраза
        phrase = make_phrase(request) 
        banner.Phrases = [phrase]
        
        #сохранить данные в API
        params = [banner]
        bannerID = directRequest('CreateOrUpdateBanners', params)
        return HttpResponse(str(bannerID)) 
    
    except Exception, e:
        return HttpResponse('Create banner SOAP Fault: '+str(e))

#phrase
#=========================================================


def make_phrase(request):

        phrase = api.factory.create('BannerPhraseInfo')
        phrase.PhraseID = 0
        phrase.Phrase = unicode(request.POST['phrase'])
        phrase.AutoBroker = "Yes"
        if len(request.POST['price']) > 0:
            phrase.Price = float(request.POST['price'])
        if len(request.POST['contextprice']) > 0:
            phrase.ContextPrice = float(request.POST['contextprice'])
        if len(request.POST['isrubric']) > 0:
            phrase.IsRubric = request.POST['isrubric']
        if len(request.POST['autobudgetpriority']) > 0:
            phrase.AutoBudgetPriority = request.POST['autobudgetpriority']

            
        #переменные, подставляемые в ссылку на сайт
        userParams = api.factory.create('PhraseUserParams')
        if len(request.POST['param1']) > 0:
            userParams.Param1 = unicode(request.POST['param1'])
        if len(request.POST['param2']) > 0:    
            userParams.Param2 = unicode(request.POST['param2'])
       
    
        phrase.UserParams = userParams
        
        return phrase 
        

def add_phrase(request):
        params = {'BannerIDS': [int(request.POST['Id'])]}
        bannerParams = directRequest('GetBanners', params)[0]
        
        phrase = make_phrase(request)
        bannerParams.Phrases.append(phrase)
        
        params = [bannerParams]
        bannerIDS = directRequest('CreateOrUpdateBanners', params)
        return HttpResponse(str(bannerIDS[0]))


def set_rate(request):
      
        params = [
           {
              'PhraseID': int(request.POST['Id']),
              'BannerID': int(request.POST['bannerId']),
              'CampaignID': int(request.POST['companyId']),
              'Price': float(request.POST['price']),
              'AutoBudgetPriority': str(request.POST['priority']),
              'AutoBroker': 'Yes', 
              #'ContextPrice': float(request.POST['contextprice'])
           }
        ]
        
        res = directRequest('UpdatePrices', params)
        return HttpResponse(str(res))   



def phrases_info(request):

    banners = request.POST.getlist("banner")
        
    params = banners
      
    res = directRequest('GetBannerPhrases', params) 
    response = ''
    for s in res:
        response += str(s)+"<br>"
  
    return HttpResponse(response)  



#keywords
#=========================================================       
            
def get_synonyms(request): 
      
        synonyms = request.POST.getlist("synonym")
        u_synonyms = []
        
        for word in synonyms:
            if word != '':
                u_synonyms.append(unicode(word))
      
        params = {
             'Keywords': u_synonyms
        }  
        
        res = directRequest('GetKeywordsSuggestion', params)
        
        response = ''
        for s in res:
            response += s.encode('utf-8')+"<br>"
        return HttpResponse(response)     
            
      



def wordstat_report(phrases, geos = ""):

        i = 0 
        for phr in phrases:
            phrases[i] = unicode(phr)        

        params = {
    		'Phrases': phrases,
    	}
        
        if geos != "" :
            params['GeoID'] = geos 

        res = directRequest('CreateNewWordstatReport', params) 
        return res  


def del_wordstat_report(num):
        params = int(num)

        res = directRequest('DeleteWordstatReport', params) 
        return res  

def check_wordstat_report():

        res = directRequest('GetWordstatReportList') 
        
        response = ''
        for s in res:
            response += str(s)+"<br>"
  
        return response  

def get_wordstat_report(num):
        params = int(num)

        res = directRequest('GetWordstatReport', params) 
        
        response = ''
        for s in res:
            response += str(s)+"<br>"
  
        return response  
        
#forecast
#=========================================================

def budget_forecast(request):

        phrases = request.POST.getlist("phrase")
        geos = request.POST.getlist("geo") 
        categories = request.POST.getlist("category")

        i = 0 
        for phr in phrases:
            phrases[i] = unicode(phr)        

        params = {
    		'Phrases': phrases,
    		'Categories': categories,
    		'GeoID': geos
    
    	}

        res = directRequest('CreateNewForecast', params) 
        return HttpResponse(str(res))  


def del_budget_forecast(request):

        num = request.POST["num"]
        
        params = int(num)

        res = directRequest('DeleteForecastReport', params) 
        return HttpResponse(str(res)) 


def check_budget_forecast():

        res = directRequest('GetForecastList') 
        
        response = ''
        for s in res:
            response += str(s)+"<br>"
  
        return HttpResponse(response)


def get_budget_forecast(request):

        num = request.POST["num"]
        params = int(num)

        res = directRequest('GetForecast', params) 
        
        response = ''
        for s in res:
            response += str(s)+"<br>"
  
        return HttpResponse(response)     




def userunits(names=["genromix"]):
    params = names
    return directRequest('GetClientsUnits', params) 

def get_clients(agent):
    
    params = {     
       'Login': agent,
       'Filter': {
          'StatusArch':'No'
        },
    }
    
    return directRequest('GetSubClients', params) 
   
def create_client(Login, Name, Surname):
    
    params = {
       'Login': unicode(Login),
       'Name': unicode(Name),
       'Surname': unicode(Surname)
    }
    
    return directRequest('CreateNewSubclient', params) 

       
#post
#========================================================= 

def post(request):
        
        
        get_meth = int(request.POST['meth'])

     

        if   get_meth == 1:  # create company
            return create_company(request) 
           
        elif get_meth == 2:  # update company 
            return update_company(request)  

        elif get_meth == 3:  # create banner
            return create_banner(request)
          
        elif get_meth == 4:  # get synonyms
            return get_synonyms(request)
            
        elif get_meth == 5:  # set rate
            return set_rate(request)
            
        elif get_meth == 6:  # set company rate
            return set_company_rate(request)
            
        elif get_meth == 7:  # add phrase
            return add_phrase(request)
       
        elif get_meth == 8:  # add phrase
            return phrases_info(request)
        
            
        else:
            return HttpResponse('unknown method')
        
        #if request.POST['redirect'] != None:
            #return HttpResponseRedirect(request.POST['redirect'])
           

 

