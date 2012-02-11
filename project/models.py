# -*- coding: utf-8 -*-

from django.db import models
from myproject.shop.models import ShopInfo


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
	client=models.ForeignKey(ShopInfo)
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

