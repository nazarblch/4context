from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('myproject.shop',
    (r'^$', 'views.index'),

    (r'^show_companies/$', 'views.show_companies'),
    (r'^xl/$', 'views.parse_xl'),
    (r'^addproducts_todb/$', 'views.addproducts_todb'),
    (r'^modify_model/$', 'views.modify_model'),
    (r'^del_unchecked_products/$', 'views.del_unchecked_products'),
    (r'^synonyms/$', 'views.add_syn_vendor_category'),
    (r'^get_syn/$', 'views.get_syn'),
    (r'^get_more_syn/$', 'views.get_more_syn'),
    (r'^set_syn/$', 'views.set_syn'),
    (r'^change_cur_cv_ob/$', 'views.change_cur_cv_ob'),

    (r'^kw_phrases/$', 'views.kw_phrases'),
    (r'^fix_groups/$', 'views.fix_groups'),
    (r'^synforall/$', 'views.synforall'),
    (r'^synforall_sep/$', 'views.synforall_sep'),
    (r'^show_model_syns/$', 'views.show_model_syns'),
    (r'^push_model_syns_to_db/$', 'views.push_model_syns_to_db'),
)


