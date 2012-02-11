from django.db import models
from myproject.agency.models import Clients
import datetime

class Vendors(models.Model):        
    name = models.CharField(max_length=100)
    vendorCode = models.CharField(max_length=100, blank=True)
    country_of_origin = models.CharField(max_length=100, blank=True)
    
    def __unicode__(self):
        return self.name  
    
    def add_synonyms(self, phrases):
        ids = []
        
        for phr in phrases:
            phr = phr.lower()
            old_obj = Vendor_synonyms.objects.filter(name=phr)
            if old_obj.count() == 0:
                if self.name != phr:
                    new_syn = Vendor_synonyms(vendor=self, name=phr, score=1)
                    new_syn.save()
                    ids.append(new_syn)
            else:
                old_obj[0].score += 1
                old_obj[0].save()
                ids.append(old_obj[0])
        
        return ids
                
    def synonyms(self):
            syns = self.vendor_synonyms_set.all()        
            return [s.name for s in syns]

class Vendor_synonyms(models.Model):
    vendor = models.ForeignKey(Vendors)
    name = models.CharField(max_length=100)
    score = models.IntegerField(default=1)  
    
    def __unicode__(self):
        return self.name 
    
    class Meta:
        ordering = ["-score"]
  
class Categories(models.Model):
    localId = models.IntegerField()  
    name =  models.CharField(max_length=100)
    p = models.ForeignKey("self", null=True, default="self")
    vendors = models.ManyToManyField(Vendors, through="Products")

    def __unicode__(self):
        return self.name
    
    def getChildren(self):
        return Categories.objects.filter(p = self)   
    
    class Meta:
        ordering = ["name"]
        
    def add_synonyms(self, phrases):
        ids = []
        
        for phr in phrases:
            phr = phr.lower()
            old_obj = Category_synonyms.objects.filter(name=phr)
            if old_obj.count() == 0:
                if self.name != phr:
                    new_syn = Category_synonyms(category=self, name=phr, score=1)
                    new_syn.save()
                    ids.append(new_syn)
            else:
                old_obj[0].score += 1
                old_obj[0].save()
                ids.append(old_obj[0])
        
        return ids
    
    def synonyms(self):
        syns = self.category_synonyms_set.all()
        
        return [s.name for s in syns]
        

class Category_synonyms(models.Model):
    category = models.ForeignKey(Categories)
    name = models.CharField(max_length=100)
    score = models.IntegerField(default=1)  
    
    def __unicode__(self):
        return self.name 
    
    class Meta:
        ordering = ["-score"]
        
    

class ShopInfo(models.Model):
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    url = models.URLField()
    agency = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Clients)
    
    categories = models.ManyToManyField(Categories)
    vendors = models.ManyToManyField(Vendors)
    
    category_syns = models.ManyToManyField(Category_synonyms)
    vendor_syns = models.ManyToManyField(Vendor_synonyms)
    
    def __unicode__(self):
        return self.name
    
    def make_companies(self, fparams):
        
        products = Products.objects.filter(shop = self)
        
        prod_arr = [products]
        
        if fparams.__contains__("category"):
            prod_arr1 = []
            for prod_arr_i in prod_arr:
                categories = set(p.category for p in prod_arr_i)
                for cat in categories:
                    prod_arr1.append( prod_arr_i.filter(category = cat) )
            prod_arr = prod_arr1
        
        
        if fparams.__contains__("vendor"):    
            prod_arr1 = []
            for prod_arr_i in prod_arr:
                vendors = set(p.vendor for p in prod_arr_i)
                for ven in vendors:
                    prod_arr1.append( prod_arr_i.filter(vendor = ven) )
            prod_arr = prod_arr1
            
    
        if fparams.__contains__("typePrefix"):    
            prod_arr1 = []
            for prod_arr_i in prod_arr:
                typePrs = set(p.typePrefix for p in prod_arr_i)
                for tP in typePrs:
                    prod_arr1.append( prod_arr_i.filter(typePrefix = tP) )
            prod_arr = prod_arr1

        return prod_arr
    
    

    def setCategories(self, arr):
        
        try:
            i = 0 
            res_arr = {}
            for node in arr:
                node = node.lower().strip()
                
                obj = Categories.objects.filter( name = node )
                if obj.count() > 0:
                    res_arr[i] = obj[0]
                    self.categories.add(obj[0])
                else:
                    new_cat = Categories()
                    new_cat.localId = i
                    new_cat.name = node
                    new_cat.p = new_cat 
                    new_cat.save();
                    
                    res_arr[i] = new_cat 
                    self.categories.add(new_cat)
                i = i + 1           
    
        except Exception, e: 
            return False, "Error in shop categories array: " + str(e)
            
        else:
            return True, res_arr  
        
    def setVendors(self, arr1, arr2):
        
        try:
            i = 0 
            res_arr = {}
            if arr2 == False:
                arr3 = ["" for j in arr1]
            else:
                arr3 = arr2    
            for name in arr1:
                name = name.lower().strip()
                
                obj = Vendors.objects.filter( 
                        name = name, 
                        country_of_origin = arr3[i]
                )
                if obj.count() > 0:
                    res_arr[i] = obj[0]
                    self.vendors.add(obj[0]) 
                else:
                    new_vendor = Vendors() 
                    new_vendor.name = name
                    new_vendor.country_of_origin = arr3[i] 
                    
                    new_vendor.save()
                    res_arr[i] = new_vendor
                    self.vendors.add(new_vendor)                 
                i = i + 1           
    
        except Exception, e: 
            return False, "Error in shop vendors array: " + str(e)
            
        else:
            return True, res_arr  


                      

class Products(models.Model):
    shop = models.ForeignKey(ShopInfo)
    category = models.ForeignKey(Categories)
    model = models.CharField(max_length=255)
    available = models.BooleanField(blank=True)
    url = models.URLField(blank=True)
    price = models.FloatField(blank=True)
    currencyId = models.CharField( max_length=5, blank=True)
    vendor = models.ForeignKey(Vendors, blank=True)
    sales_notes = models.CharField(max_length=100, blank=True)
    manufacturer_warranty = models.BooleanField(max_length=100, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    typePrefix = models.CharField(max_length=255, blank=True)
    local_delivery_cost =models.IntegerField(blank=True, default=-1)  
    delivery = models.BooleanField(blank=True)
    downloadable = models.BooleanField(blank=True)

    date = models.DateTimeField(auto_now_add=True)



    def __unicode__(self):
        res = "" 
        if self.model:
            res += self.typePrefix+": "    
        if self.model:
            res += self.model
        
        return res 

    class Meta:
        ordering = ["category","vendor"]


    
class Params(models.Model):
    product = models.ForeignKey(Products)    
    name = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=50, blank=True) 
    data = models.CharField(max_length=50, blank=True)
    
    def __unicode__(self):
        return self.name    
    
    class Meta:
        ordering = ["product"]
