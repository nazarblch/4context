#!/usr/bin/python
# -*- coding: utf-8 -*-
from xml.dom.minidom import parse
from django.views.generic.simple import direct_to_template
from myproject.shop.models import ShopInfo, Products, Params, Categories, Vendors
from myproject.agency.models import Clients
from myproject.shop.xl import *
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from myproject.yafunc import get_synonyms, wordstat
from myproject.shop.groupModels import *
from myproject.shop.groups import *
import codecs
from django.utils.encoding import *

from cv_syn.synonyms import *



def index(request):
    if 'client' not in request.session:
        request.session['client'] = 1

    clid = int(request.session['client'])
    cl = Clients.objects.get(id=clid)
    cllogin = cl.login

    if "shop" in request.session and request.session["shop"].client != cl:
        del request.session["shop"]

    if "shop" not in request.session:
        request.session["shop"] = ShopInfo(name = "def", company = "def", url = "def", email = "def", client=cl)
        request.session["shop"].save()

    shopid = request.session["shop"].id
    shopname = request.session["shop"].name

    return direct_to_template(request, 'shop/index.html', {"cllogin": cllogin, "shopid": shopid, "clid": clid, "shopname": shopname, "username": request.user.username })

def addproducts_todb(request):

    if request.is_ajax():

        ymltype = request.POST["ymltype"]
        ymlfile = request.POST["ymlfile"]

        shopobj = request.session["shop"]

        fparams = ["category", "vendor"]
        shop_id = shopobj.id

        if ymltype == "xml":
            shop = YML(ymlfile, shopobj)
            res = shop.setdbdata()

            if res == True:

                print shop.new_products
                print shop.updated_products

                request.session["shop"] = shop.shop_key
                return show_companies("", shop_id, fparams)

            else:
                return HttpResponse(str(res))


        if ymltype == "xl":
            parse_xl(ymlfile, shopobj) # "/home/nazar/django_projects/myproject/media/xml/foo.xls"
            return show_companies("", shop_id, fparams)

def modify_model(request):
    if request.is_ajax():

        if "shop" not in request.session:
            return HttpResponse("Shop isn't defined")

        shopobj = request.session["shop"]

        pr_id = int(request.POST["pr_id"]) or None
        pr_field = str(request.POST["pr_field"]) or None
        pr_new_val = str(request.POST["new_val"]).strip() or None

        PR_FIELDS = ["model", "price", "typePrefix"]

        if not str(pr_id).isdigit() or pr_field not in PR_FIELDS and pr_new_val != None:
            return HttpResponse("Wrong post data")

        try:
            product = Products.objects.get(id=pr_id)
        except:
            return HttpResponse("Product doesn't exist id="+str(pr_id))

        if product.shop != shopobj:
            return HttpResponse("Product isn't yours")

        try:
            product.__setattr__(pr_field, pr_new_val)
            product.save()
        except:
            return HttpResponse("Wrong modified value")


        return HttpResponse("1")



def del_unchecked_products(request):

    if request.is_ajax():

        if "shop" not in request.session:
            return HttpResponse("Shop isn't defined")

        shopobj = request.session["shop"]

        try:

            if len(request.POST["unchecked_ids"]) == 0 : return HttpResponse("1")

            postarr = str(request.POST["unchecked_ids"]).strip().split(',')

            postarr = map(lambda i: int(i), postarr)

            Products.objects.filter(shop = shopobj, id__in = postarr).delete()

        except Exception, e:
            return HttpResponse("Wrong product numbers for deleting "+str(e))


        return HttpResponse("1")


def add_syn_vendor_category(request):
    if 'client' not in request.session:
        return HttpResponse("Client hasn't been defined")

    if 'shop' not in request.session:
        return HttpResponse("Shop hasn't been defined")

    shopobj = request.session["shop"]
    categories = shopobj.categories.all()
    vendors = shopobj.vendors.all()


    if categories.count() == 0:
        return HttpResponse("Shop doesn't have any categories!")
    if vendors.count() == 0:
        return HttpResponse("Shop doesn't have any vendors")


    db_category_syn = categories[0].category_synonyms_set.all()
    '''
    if db_category_syn.count() > 0:
        ya_category_syn = get_synonyms([categories[0].name, db_category_syn[0].name])
    else:
        ya_category_syn = get_synonyms([categories[0].name])

    '''

    ob=Category_synonyms(categories[0].name)
    ob.phr_mod10 += [syn.name for syn in db_category_syn]
    ob.obtained_phr |= set([syn.name for syn in db_category_syn])

    ob.phrase_suggestion_recursive( 10, [])

    request.session["cur_cv_ob"] = ob
    request.session["cv_obs"] = {}


    ya_category_syn = ob.phr_div10

    #print  ya_category_syn
    #print categories[0].name


    if type(ya_category_syn) == type(""):
        return HttpResponse("Direct error: " + str(ya_category_syn))

    db_category_syn = [syn.name for syn in db_category_syn]
    ya_category_syn = set(ya_category_syn) - set(db_category_syn)

    clid = int(request.session['client'])
    cl = Clients.objects.get(id=clid)
    cllogin = cl.login
    shopname = request.session["shop"].name
    shopid = request.session["shop"].id

    first_elem = categories[0]
    request.session["cv_obs"]["cat"+str(first_elem.id)] = ob

    return render_to_response("shop/add_syn_vendor_category.html", {
                                                                    "username": request.user.username,
                                                                    "cllogin": cllogin,
                                                                    "shopname": shopname,
                                                                    "shopid": shopid,
                                                                    "clid": clid,
                                                                    "first_elem": first_elem,
                                                                    "categories":categories,
                                                                    "vendors":vendors,
                                                                    "db_category_syn":db_category_syn,
                                                                    "ya_category_syn":ya_category_syn})



def change_cur_cv_ob(request):
    if request.is_ajax():

        ob = request.session["cur_cv_ob"]
        ob.unchecked_words |= set(str(request.POST["new_unchecked_words"]).strip().split("&_&"))
        obname = request.POST["ob_name"]

        try:
            request.session["cur_cv_ob"] = request.session["cv_obs"][obname]
        except:
            get_syn(request)

        return HttpResponse(obname)


def get_syn(request):

    if request.is_ajax():
        dbtable = request.POST['dbtable']
        id = int(request.POST['id'])

        ob = request.session["cur_cv_ob"]

        if "new_unchecked_words" in request.POST:
            ob.unchecked_words |= set(str(request.POST["new_unchecked_words"]).strip().split("&_&"))

        ya_syn = ""

        if dbtable == 'cat':
            obj = Categories.objects.get(id=id)
            db_syn = obj.synonyms()
            name = obj.name

            ob=Category_synonyms(name)
            ob.phr_mod10 += [syn.name for syn in db_syn]
            ob.obtained_phr |= set([syn.name for syn in db_syn])

            ob.phrase_suggestion_recursive( 10, [])

            request.session["cur_cv_ob"] = ob

            ya_syn = ob.phr_div10

            request.session["cv_obs"]["cat"+str(id)] = ob

        if dbtable == 'ven':
            obj = Vendors.objects.get(id=id)
            db_syn = obj.synonyms()
            name = obj.name


            ob=Vendor_synonyms(name, method='sug')


            ya_syn = ob.synonyms
            ya_syn = set(ya_syn) - set(db_syn)
            request.session["cur_cv_ob"] = ob
            request.session["cv_obs"]["ven"+str(id)] = ob

            '''
            if len(db_syn) > 0:
                ya_syn = get_synonyms([name, db_syn[0]])
            else:
                ya_syn = get_synonyms([name])

            ya_syn = set(ya_syn) - set(db_syn)

            '''




        if type(ya_syn) == type(""):
            return HttpResponse("Direct error: " + str(ya_syn))


        return render_to_response("shop/syn_container.html", {
                                                                    "db_syn":db_syn,
                                                                    "ya_syn":ya_syn})

def get_more_syn(request):

    if request.is_ajax():
        ob = request.session["cur_cv_ob"]

        dbtable = request.POST['dbtable']

        if dbtable == 'cat':

            if "new_unchecked_words" in request.POST:
                ob.unchecked_words |= set(request.POST.getlist("new_unchecked_words"))

            checked_phr = []
            if "checked_phr" in request.POST:
                checked_phr = request.POST.getlist("checked_phr")

            ob.phrase_suggestion_recursive( 10, [], checked_phr)

            ya_syn = ob.phr_div10

        if dbtable == 'ven':

            ya_syn = ob.add_wordstat()



        request.session["cur_cv_ob"] = ob

        return render_to_response("shop/syn_container.html", {
                                                                "db_syn":[],
                                                                "ya_syn":ya_syn})







def set_syn(request):
    if request.is_ajax():

        if 'shop' not in request.session:
            return HttpResponse("Shop hasn't been defined")

        shop = request.session["shop"]

        cat_keys = request.POST.getlist('cat_keys')
        ven_keys = request.POST.getlist('ven_keys')

        res = ""
        if len(cat_keys)>0: shop.category_syns.all().delete()
        for k in cat_keys:
            id = int(k)
            obj = Categories.objects.get(id=id)
            cat_syn_objs = obj.add_synonyms(request.POST.getlist(k))
            for cat_syn in cat_syn_objs:
                shop.category_syns.add(cat_syn)

        if len(ven_keys)>0: shop.vendor_syns.all().delete()
        for k in ven_keys:
            id = int(k)
            obj = Vendors.objects.get(id=id)
            ven_syn_objs = obj.add_synonyms(request.POST.getlist(k))
            for ven_syn in ven_syn_objs:
                shop.vendor_syns.add(ven_syn)


        return  HttpResponse("0")


def kw_phrases(request):

    if 'client' not in request.session:
        return HttpResponse("Client hasn't been defined")

    if 'shop' not in request.session:
        return HttpResponse("Shop hasn't been defined")

    clid = int(request.session['client'])
    cl = Clients.objects.get(id=clid)
    cllogin = cl.login
    shop = request.session["shop"]
    shopname = shop.id

    if 'category' not in request.session or 'vendor' not in request.session:
        request.session['vendor'] = shop.vendors.all()[0]
        request.session['category'] = shop.categories.all()[0]

    vendor = request.session['vendor']
    category = request.session['category']

    VENDOR = vendor.name
    CATEGORY = category.name

    products = shop.products_set.filter(category=category, vendor=vendor)

    list_models=[model(prod.model, prod.id) for prod in products]

    list_gr=make_group(list_models)

    Mg = [ ModelGroup(gr) for gr in list_gr  ]

    Mg = join_groups(Mg)
    Mg = join_groups(Mg)
    Mg = join_groups(Mg)
    Mg = join_groups(Mg)

    return render_to_response("shop/kw_phrases.html", {"cllogin": cllogin,
                                                        "shop": shopname,
                                                        "clid": clid,
                                                        "Mg": Mg,
                                                         })


def fix_groups(request):

    if request.is_ajax():

        vendor = request.session['vendor']
        category = request.session['category']
        shop = request.session["shop"]

        modnumarr = request.POST['modnumarr']

        Mg = makeMg_from_ajax(request.POST, modnumarr)

        request.session["Mg"] = Mg

        return render_to_response("shop/kw_phrases_container.html", {"Mg": Mg})


def synforall(request):
    if request.is_ajax():

        Mg = request.session["Mg"]

        vendor = request.session['vendor']
        category = request.session['category']
        shop = request.session['shop']

        VENDOR = vendor.name
        ven_syn = shop.vendor_syns.filter(vendor=vendor)
        CATEGORY = category.name
        cat_syn = shop.category_syns.filter(category=category)

        req_phrs = make_ven_cat_syn_phrs(VENDOR, CATEGORY, ven_syn, cat_syn)

        firstphrases = wordstat(req_phrs[:10], showsmax=20000, geos = [1,2])[0]

        additional_wd = set()

        for phrasesarr in firstphrases:
            for phr in phrasesarr:
                num,wordsoutset = find_nearest_groups(Mg, phr, 0.2)
                for addwd in wordsoutset:
                    additional_wd.add(addwd)
                    
        request.session["Mg"] = Mg


        return render_to_response("shop/ya_kw_container.html", {"Mg": Mg, "additional_wd": additional_wd})


def synforall_sep(request, border=0.19):
    if request.is_ajax():

        Mg = request.session["Mg"]

        vendor = request.session['vendor']
        category = request.session['category']
        shop = request.session['shop']

        VENDOR = vendor.name
        
        phr_gr_nums = get_popul_gr_phrs(Mg, [VENDOR])
        
        req_phrs = phr_gr_nums.keys()
        
        kwphrases, req_phrases = wordstat(req_phrs[:50], showsmax=10000, geos = [1,2])

        additional_wd = {}

        print phr_gr_nums

        for phrnum, req_phr in enumerate(req_phrases):
            for grnum in phr_gr_nums[req_phr]:
                gr = Mg[grnum]
                
                for phr in kwphrases[phrnum]:
                    friq = int(phr[1])
                    
                    score,patt,wordsout = gr.kwphrase_check(phr[0], friq)
                    
                    if additional_wd.has_key(grnum): additional_wd[grnum] |= (wordsout)
                    else: additional_wd[grnum] = wordsout              
                    
                    if score >  border:
                            
                        pattkey = str(sorted(patt.values()))
                        if gr.kwpatt.has_key(pattkey): gr.kwpatt[pattkey][1] += friq
                        else: gr.kwpatt[pattkey] = [patt, friq]
                
                
                
      
        request.session["Mg"] = Mg


        return render_to_response("shop/ya_kw_container.html", {"Mg": Mg, "additional_wd": additional_wd})


def show_model_syns(request):

    if request.is_ajax():

        Mg = request.session["Mg"]
        
        shop = request.session['shop']
        
        for k,gr in enumerate(Mg):
            kw_patts = request.POST.getlist(k)
            if len(kw_patts) == 0: kw_patts = request.POST.getlist(str(k))
            
            for kw_patt in kw_patts:
                for mod in gr.models:
                    modkwphr = mod.get_subphrathe(gr.kwpatt[kw_patt][0], gr.pattern)
                    if len(modkwphr) > 0:
                        mod.kwphr.add(" ".join(modkwphr))

        request.session["Mg"] = Mg
        
        return render_to_response("shop/gr_kw_final_container.html", {"Mg": Mg})



def push_model_syns_to_db(request):
    
    if request.is_ajax():
        
        shop = request.session['shop']
        
        


def show_companies(request="", shop_id="", fparams=""):

    if request != "":
        shop_id = request.POST.get("shop_id", "")
        fparams = request.POST.getlist("fparam")

    if shop_id and int(shop_id):
        shop = ShopInfo.objects.get(id = shop_id)
        try:
            pr_blocks = shop.make_companies(fparams)
            pr_blocks_dict = {}
            blocks = []
            for block in pr_blocks:
                pr_blocks_dict = {}
                pr_blocks_dict["block"] = block
                if "category" in fparams:
                        pr_blocks_dict["category"] = block[0].category
                if "vendor" in fparams:
                        pr_blocks_dict["vendor"] = block[0].vendor
                if "typePrefix" in fparams:
                        pr_blocks_dict["typePrefix"] = block[0].typePrefix

                blocks.append(pr_blocks_dict)


        except Exception, e:
            return HttpResponse("Failed to make product blocks " + str(e))

        return render_to_response("shop/show_companies.html", {"pr_blocks":blocks,"fparams":fparams})
    else:
        return HttpResponse("Shop id was lost or isn't correct")





def parse_xl(file_path, shopobj):
    '''
    new_sh =  ShopInfo(
                    name = request.POST.get("shname", shname),
                    company = request.POST.get("shcompany", ""),
                    url = request.POST.get("shurl", ""),
                    email = request.POST.get("shemail", ""),
                    agency = request.POST.get("shagency", "")
              )
    new_sh.save()
    '''
    new_sh = shopobj

    shop = XL(file_path)

    categories = shop.colbyname("category")[1:]
    vendors = shop.colbyname("vendor")[1:]
    countries = shop.colbyname("country_of_origin")

    res,new_categories = new_sh.setCategories(categories)
    if res != True:
        return HttpResponse(str(new_categories))

    if countries != False:
        countries = countries[1:]

    res,new_vendors = new_sh.setVendors(vendors, countries)
    if res != True:
        return HttpResponse(str(new_vendors))


    rowmap = shop.colmap()

    try:

        for num in range(1,shop.nrows()):
            new_product =  Products()
            row = shop.row(num)

            new_product.shop = new_sh
            new_product.category = new_categories[num-1]
            new_product.vendor = new_vendors[num-1]
            new_product.model = str(row[rowmap["model"]]).lower().strip()
            new_product.available = bool(row[rowmap["available"]])
            if rowmap.has_key("url"):
                new_product.url = row[rowmap["url"]]
            new_product.price = float(row[rowmap["price"]])
            new_product.currencyId = row[rowmap["currencyId"]]

            if rowmap.has_key("sales_notes"):
                new_product.sales_notes = row[rowmap["sales_notes"]]
            if rowmap.has_key("manufacturer_warranty"):
                new_product.manufacturer_warranty = bool(row[rowmap["manufacturer_warranty"]])
            if rowmap.has_key("barcode"):
                new_product.barcode = row[rowmap["barcode"]]
            if rowmap.has_key("description"):
                new_product.description = row[rowmap["description"]]
            if rowmap.has_key("typePrefix"):
                new_product.typePrefix = row[rowmap["typePrefix"]]
            if rowmap.has_key("local_delivery_cost") and row[rowmap["local_delivery_cost"]]:
                new_product.local_delivery_cost = int(row[rowmap["local_delivery_cost"]])
            if rowmap.has_key("delivery"):
                new_product.delivery = bool(row[rowmap["delivery"]])
            if rowmap.has_key("downloadable"):
                new_product.downloadable = bool(row[rowmap["downloadable"]])


            new_product.save()

    except Exception, e:
        return HttpResponse("XL File isn't correct. Error in set products part: \n " + str(e))


    return HttpResponseRedirect("/shop/choose_division/" + str(new_sh.id)  )



class YML:

    def __init__(self, filearg, shopobj="" ):

        self.path = filearg
        self.shoptag = "shop"
        self.shop_key = shopobj
        self.updated_products = []
        self.new_products = []

    def getshopdata(self):
        return self.shop_key

    def setdbdata(self):
        try:
            self.dom = parse(self.path)
        except Exception, e:
            return "Error in YML file: " + str(e)


        shop = self.dom.getElementsByTagName(self.shoptag)[0]
        self.shop_key = self.setShopInfo(shop)

        res1,new_categories =  self.setCategories(shop.getElementsByTagName("categories")[0], self.shop_key)

        return res1 and self.setOffers(shop, self.shop_key, new_categories)


    def getText(self, node):
        try:
            if node.nodeType==node.TEXT_NODE:
                return node.data
            else:
                if node.nodeType==node.ELEMENT_NODE:
                    return  node.firstChild.data
                else:
                    return -1
        except:
            return -1




    def setShopInfo(self,parent):


        try:
            if self.shop_key != "":
                new_sh = self.shop_key

                if new_sh.name == "def":
                    new_sh.name = self.getText(parent.getElementsByTagName("name")[0])
                if new_sh.company == "def":
                    new_sh.company = self.getText(parent.getElementsByTagName("company")[0])
                if new_sh.url == "def":
                    new_sh.url = self.getText(parent.getElementsByTagName("url")[0])
                if new_sh.email == "def":
                    new_sh.email = self.getText(parent.getElementsByTagName("email")[0])

                agency_var = self.getText(parent.getElementsByTagName("agency")[0])
                if agency_var != -1:
                    new_sh.agency = agency_var

                new_sh.save()

            else:
                return "Shop hasn't been defined \n "


        except Exception, e:
            return "YML File isn't correct. Error in shop info part: \n " + str(e)

        else:
            return new_sh



    def setProduct(self,parent, cat_key, shop_key):
        try:
            new_product =  Products()

            new_product.shop = shop_key
            new_product.category = cat_key
            new_product.model = self.getText(parent.getElementsByTagName("model")[0])
            new_product.model = new_product.model.lower().strip()

            new_vendor = Vendors()
            new_vendor.name = self.getText(parent.getElementsByTagName("vendor")[0])
            new_vendor.name = new_vendor.name.lower().strip()
            if parent.getElementsByTagName("vendorCode"):
                new_vendor.vendorCode = self.getText(parent.getElementsByTagName("vendorCode")[0])
            if parent.getElementsByTagName("country_of_origin"):
                new_vendor.country_of_origin = self.getText(parent.getElementsByTagName("country_of_origin")[0])


            obj = Vendors.objects.filter(
                    name = new_vendor.name,
                    country_of_origin = new_vendor.country_of_origin
            )
            if obj.count() > 0:
                new_product.vendor = obj[0]
                shop_key.vendors.add(obj[0])
            else:
                new_vendor.save()
                new_product.vendor = new_vendor
                shop_key.vendors.add(new_vendor)

            old_product = Products.objects.filter(shop=new_product.shop, vendor=new_product.vendor,
                                                    category=new_product.category, model=new_product.model)
            if old_product.count() > 0:
                new_product = old_product[0]
                self.updated_products.append(new_product)
            else:
                self.new_products.append(new_product)

            new_product.available = bool(parent.getAttribute('available'))
            if parent.getElementsByTagName("url"):
                new_product.url = self.getText(parent.getElementsByTagName("url")[0])
            new_product.price = float(self.getText(parent.getElementsByTagName("price")[0]))
            new_product.currencyId = self.getText(parent.getElementsByTagName("currencyId")[0])

            if parent.getElementsByTagName("sales_notes"):
                new_product.sales_notes = self.getText(parent.getElementsByTagName("sales_notes")[0])
            if parent.getElementsByTagName("manufacturer_warranty"):
                new_product.manufacturer_warranty = bool(self.getText(parent.getElementsByTagName("manufacturer_warranty")[0]))
            if parent.getElementsByTagName("barcode"):
                new_product.barcode = self.getText(parent.getElementsByTagName("barcode")[0])
            if parent.getElementsByTagName("description"):
                new_product.description = self.getText(parent.getElementsByTagName("description")[0])
            if parent.getElementsByTagName("typePrefix"):
                new_product.typePrefix = self.getText(parent.getElementsByTagName("typePrefix")[0])
            if parent.getElementsByTagName("local_delivery_cost"):
                new_product.local_delivery_cost = int(self.getText(parent.getElementsByTagName("local_delivery_cost")[0]))
            if parent.getElementsByTagName("delivery"):
                new_product.delivery = bool(self.getText(parent.getElementsByTagName("delivery")[0]))
            if parent.getElementsByTagName("downloadable"):
                new_product.downloadable = bool(self.getText(parent.getElementsByTagName("downloadable")[0]))

            new_product.save()
            product_key = new_product

            res = self.setParams(parent.getElementsByTagName("param"), product_key)

            if res != True:
                return res

        except Exception, e:
            return "Error in offer:" + parent.getAttribute('id') +" : " +  new_product.model + "\n " + str(e)

        else:
            return True

    def setParams(self, params, product_key):

        try:
            for node in params:
                new_param = Params()
                new_param.product = product_key
                new_param.name = node.getAttribute('name')
                new_param.data = self.getText(node)
                if node.getAttribute('unit'):
                    new_param.unit = node.getAttribute('unit')
                new_param.save()

        except Exception, e:
            return "Error in params:" + product_key.model +" : " +  new_param.name + "\n " + str(e)
        else:
            return True






    def setOffers(self,parent, shop_key, new_categories):

        try:

            for node in parent.getElementsByTagName("offer"):
                cat = new_categories[int(self.getText(node.getElementsByTagName("categoryId")[0]))]

                res = self.setProduct(node, cat, shop_key)
                if res != True:
                    return res



        except Exception, e:
            return "YML File isn't correct. Error in shop offers part: \n " + str(e)

        else:
            return True





    def setCategories(self, parent, key):

        try:

            CatIds = {}

            arr = [ self.getText(node) for node in parent.getElementsByTagName("category") ]

            res, new_categories = key.setCategories(arr)

            if res == False:
                return False, new_categories

            i = 0
            for node in parent.getElementsByTagName("category"):
                CatIds[int(node.getAttribute('id'))] = new_categories[i]
                i = i + 1


        except Exception, e:
            return False, "YML File isn't correct. Error in shop categories part: \n " + str(e)

        else:
            return True, CatIds
