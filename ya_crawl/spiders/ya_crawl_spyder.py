# -*- coding:utf8 -*-


import re
from ast import literal_eval

from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import MapCompose
from scrapy.contrib.loader.processor import TakeFirst
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http.request.form import FormRequest

import time









def htmlparse_dict(html):
    str = html
    only_phrase = re.match('.*var phrases = new Array \((?P<array_inside>[^\)]*)', str, re.S).group('array_inside')
    arr_diction = ''.join(['[',only_phrase,']'])
    arr_diction = re.sub('(\s+|,{1})(\w+)(:{1})',lambda res: '%s"%s"%s' %(res.group(1),res.group(2),res.group(3)), arr_diction)

    dict = literal_eval(arr_diction)
    return dict


class Ya_crawlLoader(XPathItemLoader):
    default_input_processor = MapCompose(lambda s: re.sub('\s+', ' ', s.strip()))
    default_output_processor = TakeFirst()

class Ya_crawlSpider(CrawlSpider):

    name = "ya_crawl"
    allowed_domains = ["yandex.ru"]

    start_urls = []

    reg_deta = None

    res = []



    def __init__(self, phrases, login, passwd):

        self.login = login
        self.passwd = passwd

        self.phrarr = phrases
        self.cur_phrarr = self.phrarr[:15]
        self.cur_step = 0
        steps = len(self.phrarr)/15
        if len(self.phrarr)%15 != 0: steps += 1

        for i in range(steps):
            self.start_urls.append('http://direct.yandex.ru/registered/main.Fz0_I3aANIVYfWrv.pl?cmd=calcForecast&new_phrases='+"hren")


    def parse(self, response):

        if self.reg_deta != None:
            return self.after_login(response)


        '''
        myformdata = {
        'ChoosedCategories':'',
        'UncheckedCategories':'',
        'cmd':	'calcForecast',
        'geo':'',
        'new_phrases':	'samsung, sams',
        'phrases':'',
        'pseudo_currency_id': 'rub',
        'suggest_add_all_count': '0',
        'suggest_add_one_phrase_count':'1',
        'suggest_added_phrases_count': '1',
        'suggest_clear_count':	'0',
        'suggest_nonempty_answers':	'1',
        'suggest_refine_count':	'0',
        'suggest_request_count': '4',
        'text_rubrics':''
            }
        '''


        myformdata = {
            'display':	'page',
            'from': 'passport',
            'login': self.login,
            'passwd': self.passwd,
            'retpath': self.start_urls[0],
        }

        '''
        res1 = FormRequest("https://passport.yandex.ru/passport?mode=auth",
                            formdata=myformdata,
                            callback=self.parse)
        '''



        print response

        print "here1"
        return [ FormRequest.from_response(response,
                                          formdata=myformdata,
                                          callback=self.after_login)

                ]

    def after_login(self, response):



        if self.reg_deta == None: self.reg_deta = response

        print self.cur_phrarr

        myformdata = {

            'cmd':	'calcForecast',

            'new_phrases': (",".join(self.cur_phrarr)).encode("utf-8"),

        }

        self.cur_step += 1
        self.cur_phrarr = self.phrarr[20*self.cur_step:20*self.cur_step+20]

        return [FormRequest.from_response(self.reg_deta, formdata=myformdata, callback=self.parse_page2 )]

    def parse_page2(self, response):

        # this would log http://www.example.com/some_page.html
        #open('paulsmith1.html', 'wb').write(response.body)
        phrdictarr = htmlparse_dict(response.body)
        print "here"
        self.res += phrdictarr
        '''
        for phrdict in phrdictarr:
            print "==========================================================================="
            print "                              new dict                                     "
            print "==========================================================================="
            for k,v in phrdict.items():
                print k,v
            #print response.body
        '''






def main():
    from scrapy import signals
    from scrapy.xlib.pydispatch import dispatcher

    phrarr = "самсунг мобилки, сотовые телефоны samsung, мобильный самсунг, samsung телефоны все модели, телефоны самсунг каталог, купить телефон самсунг, мобильные телефоны самсунг, самсунг телефоны, мобильные телефоны nokia, samsung телефоны каталог, купить телефон samsung, самсунг телефоны цены, куплю телефон samsung, куплю телефон самсунг".split(", ")


    phrarr += "samsung galaxy, samsung galaxy купить, samsung i9000 galaxy s, сотовые телефоны samsung galaxy, купить samsung galaxy s, samsung galaxy s i9100, samsung galaxy s цена, samsung galaxy s ii i9100, samsung galaxy s ii, купить samsung i9000 galaxy s, samsung galaxy s gt-i9000, galaxy s, samsung i9000, samsung galaxy s, samsung gt-i9000".split(", ")
    phrarr += "samsung galaxy, samsung galaxy купить, samsung i9000 galaxy s, сотовые телефоны samsung galaxy, купить samsung galaxy s, samsung galaxy s i9100, samsung galaxy s цена, samsung galaxy s ii i9100, samsung galaxy s ii, купить samsung i9000 galaxy s, samsung galaxy s gt-i9000, galaxy s, samsung i9000, samsung galaxy s, samsung gt-i9000".split(", ")



    def catch_item(sender, item, **kwargs):
        print "Got:", item

    dispatcher.connect(catch_item, signal=signals.item_passed)

    # shut off log
    from scrapy.conf import settings
    settings.overrides['LOG_ENABLED'] = False

    # set up crawler
    from scrapy.crawler import CrawlerProcess

    crawler = CrawlerProcess(settings)
    #crawler.install()
    crawler.configure()

    # schedule spider
    Ya_crawl = Ya_crawlSpider(phrarr, "genromix", "16208075")
    crawler.crawl(Ya_crawl)

    # start engine scrapy/twisted
    print "STARTING ENGINE"
    crawler.start()
    print "ENGINE STOPPED"
    print Ya_crawl.res

if __name__ == '__main__':
    st  = time.time()
    main()
    t1 = time.time()

    print t1 - st





