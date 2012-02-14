

class Kwblock:
    def __init__(self, shop=None,  parent='', sort_params={}, plus_phr_type=set([]),child_sort=set([])):
        self.parent = parent
        self.sort_params = sort_params
        self.plus_phr_type = plus_phr_type
        self.sort_params = sort_params
        self.child_sort = child_sort
        self.childrens = None
        self.shop = shop

    def all_parents_phr_type(self):
        self.phr_type = []
        p = self
        while p.parent != '':
            if p.plus_phr_type != '':
                self.phr_type.extend(p.plus_phr_type)
            p = p.parent

        return self.phr_type

    def childrens(self):
        ch = []

        categories = self.shop.categories.all()
        vendors = self.shop.vendors.all()

        if 'cat' in self.child_sort:
            ch = [{'cat':cat} for cat in categories]

        if 'ven' in self.child_sort:
            if ch != '':
                ch = []
                for cat in categories:
                    cat_vendors = cat.vendors.all()
                    ch.extend([{'cat': cat, 'ven':ven} for ven in cat_vendors])
            else:
                ch = [{'ven':ven} for ven in vendors]


        self.childrens = {}

        for i in ch:
            sort_param = {}
            if 'ven' in i: sort_param['ven'] = i['ven'].id
            if 'cat' in i: sort_param['cat'] = i['cat'].id

            key = ",".join(sort_param.values())
            self.childrens[key] = Kwblock(self, self.shop, sort_param)

        return ch

    def chield(self, plus_phr_type):

        key = "__".join(plus_phr_type)
        self.childrens[key] = Kwblock(parent=self, shop=self.shop, plus_phr_type=plus_phr_type)

        return key
