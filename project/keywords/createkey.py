# -*- coding: utf-8 -*-

from itertools import combinations
from myproject.project.models import Keyword
from myproject.shop.models import Products, Product_synonyms


def combinations_for_mainkey(product):
    prodsyn = list(Product_synonyms.objects.filter(product=product))
    category = product.category
    vendor = product.vendor

    prodsyn.append(product)

    sets_the_key = []

    for psyn in prodsyn:
        sets_the_key.extend(map(lambda x: set(combinations([psyn,category,vendor],x)), [1,2,3]))
    sets_the_key = reduce(lambda x,y: x.union(y), sets_the_key)

    result = sets_the_key.copy()

    for tup in sets_the_key:
        result.add(tup + (u'купить',) )

    return result


def mainkey(product1):
    result_kw = []
    for kw_words in combinations_for_mainkey(product1):
        obj = Keyword()
        obj.afterinit({'product': product1, 'words':kw_words})
        obj.save()

        if obj.keyword1 == "": continue

        result_kw.append({'key':obj.keyword1, 'words': kw_words})

    return result_kw
