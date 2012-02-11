# -*- coding: utf-8 -*-
import os
from transl import translit, check_lang
from pymorphy import get_morph
morph = get_morph(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'morph'))
i=0
for d in morph.get_graminfo(u'МОБИЛЬНЫХ'):
    print d['info']

    