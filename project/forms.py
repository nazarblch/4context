# -*- coding: utf-8 -*-
from django.forms import ModelForm
from myproject.project.models import *

class Create_Company(ModelForm):
	class Meta:
		model=Company
		exclude = ('ya_id',)
class Create_Project(ModelForm):
	class Meta:
		model=Project
        exclude = ('shop',)
		
