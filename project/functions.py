
def max_ctr(product):
    return product["ctr"]/product["price"]

def push_into_pack(products, price_names, budget, goal_func = max_ctr):
    separated_pr = []

    for pr_num,prod in enumerate(products):
        for price_name in price_names:
            prod_part = {"pr_num":pr_num, "price":prod[price_name], "ctr": prod["ctr"], "clicks": prod["clicks"] }
            separated_pr.append(prod_part)

    summa = 0.0

    while summa <= budget and len(separated_pr) > 0:
        max = 0
        max_id = None

        for pr_num,prod in enumerate(separated_pr):
            t = goal_func(prod)
            if t > max:
                max = t
                max_id = pr_num




