# -*- coding: utf-8 -*-

from django.db import models
from myproject.shop.models import ShopInfo, Products, Product_synonyms, Vendors, Vendor_synonyms, Categories, Category_synonyms
#from typecheck import *

STRATEGY_CHOICES=(
(u'HighestPosition', u'Наивысшая доступная позиция'),
(u'LowestCost', u'Показ в блоке по минимальной цене'),
(u'LowestCostPremium', u'Показ в блоке по мин. цене. Только Спецразмещение'),
(u'WeeklyBudget', u'Недельный бюджет'),
(u'WeeklyPacketOfClicks', u'Недельный пакет кликов'),
(u'AverageClickPrice', u'Средняя цена клика'),
    )

BOOL_CHOICES=(
(u'Yes', u'Да'),
(u'No', u'Нет'),
    )
MOD10_CHOICES=tuple([(i*10, u'%s' % (i*10)+'%') for i in range(11)])

class Project(models.Model):
    shop=models.ForeignKey(ShopInfo)
    name=models.CharField(max_length=30)
    email=models.EmailField(max_length=100)
    geo=models.CharField(max_length=50)    #coma separated
    Days=models.CharField(max_length=100)
    holidays=models.CharField(max_length=3, choices=BOOL_CHOICES)
    hol_from=models.IntegerField(null=True, blank=True)
    hol_to=models.IntegerField(null=True, blank=True)
    contextlimitsum=models.IntegerField(null=True, blank=True, choices=MOD10_CHOICES)
    contextpricepercent=models.IntegerField(null=True, blank=True, choices=MOD10_CHOICES)




class Company(models.Model):
    name=models.CharField(max_length=30)
    ya_id=models.IntegerField(blank=True, null=True)
    project=models.ForeignKey(Project)
    strategy=models.CharField(max_length=30, choices=STRATEGY_CHOICES)
    url=models.URLField()


class Banner(models.Model):
    company=models.ForeignKey(Company)
    ya_id=models.IntegerField()


class Keyword(models.Model):
    pattern = models.CharField(max_length=4,  blank=True)
    keyword1 = models.CharField(max_length=4096,  blank=True)
    product = models.ManyToManyField(Products)
    sellword = models.CharField(max_length=10,  blank=True)

    #@takes(Products, (Products,Product_synonyms), (Categories,Category_synonyms), (Vendors,Vendor_synonyms), str)

    def afterinit(self, dict1):
        self.adding_product = dict1['product']

        self.keyword1 = ""

        def sortbyclass(obj):
            if isinstance(obj, Categories) or isinstance(obj, Category_synonyms): return 1
            if isinstance(obj, Vendors) or isinstance(obj, Vendor_synonyms): return 2
            if isinstance(obj, Products) or isinstance(obj, Product_synonyms): return 3
            if isinstance(obj, unicode): return 4

        objects_for_keyword = list(dict1['words'])

        objects_for_keyword.sort(key=sortbyclass)

        for arg in objects_for_keyword:
            if isinstance(arg,Categories):
                self.pattern+='c'
                self.keyword1 = ' '.join([self.keyword1,arg.name])
            elif isinstance(arg, Category_synonyms):
                self.pattern+='c'
                self.keyword1 = ' '.join([self.keyword1,arg.name])
            elif isinstance(arg,Vendors):
                self.pattern+='v'
                self.keyword1 = ' '.join([self.keyword1,arg.name])
            elif isinstance(arg, Vendor_synonyms):
                self.pattern+='v'
                self.keyword1 = ' '.join([self.keyword1,arg.name])
            elif isinstance(arg,Products):
                self.pattern+='m'
                self.keyword1 = ' '.join([self.keyword1,arg.model])
            elif isinstance(arg, Product_synonyms):
                self.pattern+='m'
                self.keyword1 = ' '.join([self.keyword1,arg.name])
            if isinstance(arg, unicode):
                self.pattern+='s'
                self.keyword1 = ' '.join([self.keyword1,arg])

            self.keyword1.strip()
            self.keyword2 = self.keyword1


    def save(self):
        objs = Keyword.objects.filter(keyword1 = self.keyword1)

        if objs.count() > 0 :
            objs[0].product.add(self.adding_product)
        else:
            if self.keyword2 != "":
                super(Keyword,self).save()
                self.product.add(self.adding_product)
