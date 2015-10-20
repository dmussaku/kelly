from random import randint

names = ['Sattar', 'Nurlan', 'Yerlan', 'Zhan', 'Kot', 'Yernar', 'Ivan',
         'Rustem', 'Sanzhar', 'Zhan', 'Dos', 'Alisher', 'Usman']
words = ['Fairy', 'Cloud', 'Atlas', 'World', 'Solution', 'Apple', 'Juicy']

comments = (
    'The week also lifts the lid on the thinking of Federal Reserve.',
    'Data on US housing starts for October will also be released.',
    'Monday brings the delayed start of the Shanghai-Hong Kong exchange link, when cross-trading of shares on the two exchanges is due to start in a move that would open up China` $4.2 trillion stock market to foreigners',
    'Also due on Monday are US industrial production statistics for October and the start of the Chicago Fed`s annual agriculture conference.',
    'Tuesday brings the Los Angeles Auto Show, earnings from Home Depot and the expected $2 billion-plus initial public offering (IPO) of real estate investment trust Paramount Group.',
    'Also expected on Thursday are an update on existing home sales and earnings from Gap, BestBuy and Dollar Tree.',
    'Friday brings a US Senate hearing on the New York Federal Reserve, which has been accused of being too cosy with the Wall Street banks it is supposed to regulate.',
    'The Senate Banking panel`s Subcommittee on Financial Institutions and Consumer Protection will host the hearing.',
    )

product_names = ['Microsoft', '1C Enterprise', 'Almasales', 'SalesForce']
product_descs = ('is an American multinational technology company headquartered in Redmond', 
                ' is one of the largest independent Russian software developers ', 
                ' the best software service system in the WORLD ', 
                ' is a global cloud computing company headquartered in San Francisco')


f = {
    'company': '',
    'user': '',
    'subscription': '',
    'contact': '',
    'vcard': '',
    'crmuser': '',
    'sales_cycles': '',
    'activities': '',
    'comments': '',
    'products': '',
    'sc_prod_stat': ''
}

id_subscr = 1
id_company = 1
id_user = 1
id_contact = 1
id_vcard = 1
id_vcard_email = 1
id_crmuser = 1
id_sales_cycles = 1
id_activities = 1
id_comments = 1
id_product = 1
id_stat = 1


limits = [  # limits by subscription ids
    {'user': 20, 'contact': randint(2000, 2500), 'sales_cycle': randint(1, 3), 'activity': randint(1, 3), 'comment': randint(0, 4), 'products': 20},
    {'user': 10, 'contact': randint(700, 1500), 'sales_cycle': randint(1, 3), 'activity': randint(1, 2), 'comment': randint(0, 3), 'products': 1000}
]


def gen_name():
    return names[randint(0, len(names)-1)] + ' ' + names[randint(0, len(names)-1)]+'ov'


_emails = []


def gen_email(user_name):
    while(True):
        email = user_name.replace(' ', '.').lower() + str(randint(0, 2000)) + '@alma.net'
        try:
            _emails.index(email)
        except Exception:
            _emails.append(email)
            return email

def gen_vcard(user_name):
    global id_vcard, id_vcard_email

    vcard = ''
    vcard += '{\n'
    vcard += '    "pk": %i,\n' % (id_vcard)
    vcard += '    "model": "alm_vcard.vcard",\n'
    vcard += '    "fields": {\n'
    vcard += '        "family_name": "%s",\n' % (user_name.split(' ')[1])
    vcard += '        "uid": null,\n'
    vcard += '        "honorific_suffix": "",\n'
    vcard += '        "additional_name": "",\n'
    vcard += '        "rev": null,\n'
    vcard += '        "honorific_prefix": "",\n'
    vcard += '        "bday": null,\n'
    vcard += '        "given_name": "%s",\n' % (user_name.split(' ')[0])
    vcard += '        "sort_string": null,\n'
    vcard += '        "classP": null,\n'
    vcard += '        "fn": "%s"\n' % (user_name)
    vcard += '    }\n'
    vcard += '},\n'
    f['vcard'] += vcard
    id_vcard += 1

    vcard_email = ''
    vcard_email += '{\n'
    vcard_email += '    "pk": %i,\n' % (id_vcard_email)
    vcard_email += '    "model": "alm_vcard.email",\n'
    vcard_email += '    "fields": {\n'
    vcard_email += '        "type": "INTERNET",\n'
    vcard_email += '        "vcard": %i,\n' % (id_vcard - 1)
    vcard_email += '        "value": "%s"\n' % (gen_email(user_name))
    vcard_email += '    }\n'
    vcard_email += '},\n'
    f['vcard'] += vcard_email
    id_vcard_email += 1

def gen_sc_prod_stat(cycle_id, product_id, subscription_id):
    global id_stat
    value = randint(2000, 10000)
    stat = ''
    stat += '{\n'
    stat += '    "pk": %i,\n' % (id_stat)
    stat += '    "model": "alm_crm.salescycleproductstat",\n'
    stat += '    "fields": {\n'
    stat += '        "sales_cycle": %i,\n' % (cycle_id)
    stat += '        "product": %i,\n' % (product_id)
    stat += '        "subscription_id": %i,\n' % (subscription_id)
    stat += '        "value": %i \n' % (value)
    stat += '    }\n'
    stat += '},\n'
    f['sc_prod_stat'] += stat
    id_stat += 1
    return value

for index_subscr in range(0, len(limits)):

    ss = ''
    ss += '{\n'
    ss += '    "pk": %i,\n' % (id_subscr)
    ss += '    "model": "almanet.subscription",\n'
    ss += '    "fields": {\n'
    ss += '        "organization": %i,\n' % (id_company)
    ss += '        "is_active": true,\n'
    ss += '        "user": %i,\n' % (id_user)
    ss += '        "service": 1\n'
    ss += '    }\n'
    ss += '},\n'
    f['subscription'] += ss
    id_subscr += 1
    print "Subscription %i created" % index_subscr

    comp_name = 'ALMACloud' if index_subscr == 0 else words[randint(0, len(words)-1)] + words[randint(0, len(words)-1)]
    comp = ''
    comp += '{\n'
    comp += '    "pk": %i,\n' % (id_company)
    comp += '    "model": "alm_company.company",\n'
    comp += '    "fields": {\n'
    comp += '        "owner": [%i],\n' % (id_user)
    comp += '        "subdomain": "%s",\n' % (comp_name.lower())
    comp += '        "name": "%s"\n' % (comp_name)
    comp += '    }\n'
    comp += '},\n'
    f['company'] += comp
    id_company += 1
    print "Company %s created"%comp_name

    for index_user in range(0, limits[index_subscr]['user']):
        is_first_user = lambda: index_subscr == 0 and index_user == 0
        user_name = 'Bruce Wayne' if is_first_user() else gen_name()
        user = ''
        user += '{\n'
        user += '    "pk": %i,\n' % (id_user)
        user += '    "model": "alm_user.user",\n'
        user += '    "fields": {\n'
        user += '        "first_name": "%s",\n' % (user_name.split(' ')[0])
        user += '        "last_name": "%s",\n' % (user_name.split(' ')[1])
        user += '        "company": [%i],\n' % (id_company - 1)
        user += '        "is_active": true,\n'
        user += '        "last_login": "2014-11-11T07:51:02.253Z",\n'
        user += '        "is_admin": %s,\n' % ('true' if is_first_user() else 'false')
        user += '        "timezone": "Asia/Almaty",\n'
        user += '        "password": "pbkdf2_sha256$12000$RfGiFmGJSeoz$063rfBSPM0AsFi1prglD5BW8qD1ElMYxBpRr5tO1M08=",\n'
        user += '        "email": "%s",\n' % ('b.wayne@batman.bat' if is_first_user() else gen_email(user_name))
        user += '        "vcard": %i\n' % (id_vcard)
        user += '    }\n'
        user += '},\n'
        f['user'] += user
        id_user += 1

        gen_vcard(user_name)

        crmuser = ''
        crmuser += '{\n'
        crmuser += '    "pk": %i,\n' % (id_crmuser)
        crmuser += '    "model": "alm_crm.CRMUser",\n'
        crmuser += '    "fields": {\n'
        crmuser += '        "user_id": %i,\n' % (id_user - 1)
        crmuser += '        "organization_id": %i,\n' % (id_company - 1)
        crmuser += '        "subscription_id": %i\n' % (id_subscr - 1)
        crmuser += '    }\n'
        crmuser += '},\n'
        f['crmuser'] += crmuser
        id_crmuser += 1

        print "User %s created" % user_name

    subscr_prod_indx = []
    for index_product in range(0, limits[index_subscr]['products']):
        def gen_user_id():
            ids = range(id_user - limits[index_subscr]['user'], id_user)
            return ids[randint(0, len(ids)-1)]
        product_name = product_names[randint(0, 3)]
        product = ''
        product += '{\n'
        product += '    "pk": %i,\n' % (id_product)
        product += '    "model": "alm_crm.product",\n'
        product += '    "fields": {\n'
        product += '        "name": "Product %s",\n' % (product_name)
        product += '        "description": " Product %s - %s",\n' % (product_name, product_descs[randint(0,3)])
        product += '        "price": %i,\n' % (randint(2000, 80000))
        product += '        "currency": "KZT",\n'
        product += '        "date_created":"2014-10-%02i 00:00:00+00:00",\n' % \
                (index_product%28 + 1)
        product += '        "owner": %i,\n' % (gen_user_id())
        product += '        "subscription_id": %i \n' % (id_subscr - 1)
        product += '    }\n'
        product += '},\n'
        f['products'] += product
        subscr_prod_indx.append(id_product)
        id_product += 1

    for index_contact in range(0, limits[index_subscr]['contact']):

        def gen_user_id():
            ids = range(id_user - limits[index_subscr]['user'], id_user)
            return ids[randint(0, len(ids)-1)]

        cont_name = gen_name()
        cont = ''
        cont += '{\n'
        cont += '    "pk": %i,\n' % (id_contact)
        cont += '    "model": "alm_crm.contact",\n'
        cont += '    "fields": {\n'
        cont += '        "status": 1,\n'
        cont += '        "latest_activity": null,\n'
        cont += '        "tp": "user",\n'
        cont += '        "parent": null,\n'
        cont += '        "owner": %i,\n' % (gen_user_id())
        cont += '        "date_created": "2014-09-10T00:00:00Z",\n'
        cont += '        "subscription_id": %i,\n' % (id_subscr - 1)
        cont += '        "vcard": %i\n' % (id_vcard)
        cont += '    }\n'
        cont += '},\n'
        f['contact'] += cont
        id_contact += 1

        gen_vcard(cont_name)

        for index_s in range(0, randint(1, 4)):
            s_status = ('N', 'P', 'C')[randint(0, 2 if index_s != 0 else 1)]
            s = ''
            s += '{\n'
            s += '    "pk": %i,\n' % (id_sales_cycles)
            s += '    "model": "alm_crm.SalesCycle",\n'
            s += '    "fields": {\n'
            s += '        "is_global":%s,\n' % ('true' if index_s == 0 else 'false')
            s += '        "title":"SalesCycle #%i",\n' % (id_sales_cycles)
            # s += '        "products":[%i],\n' % (product_id)
            s += '        "owner":%i,\n' % (gen_user_id())
            s += '        "followers":[],\n'
            s += '        "contact":%i,\n' % (id_contact - 1)
            s += '        "latest_activity":%s,\n' % 'null'  #('null' if s_status=='N' else str(id_activities+1))
            # s += '        "projected_value":%i,\n' % (id_values)
            # s += '        "real_value":%i,\n' % (id_values + 1)
            s += '        "status":"%s",\n' % (s_status)
            s += '        "date_created":"2014-10-%02i 00:00:00+00:00",\n' % \
                (index_s%28 + 1)
            s += '        "from_date":"2014-10-%02i 00:00:00+00:00",\n' % \
                (index_s%28 + 1)
            s += '        "to_date":"2014-10-%02i 00:00:00+00:00",\n' % \
                (index_s%28 + 1)
            s += '        "subscription_id": %i\n' % (id_subscr - 1)
            s += '    }\n'
            s += '},\n'
            f['sales_cycles'] += s
            id_sales_cycles += 1

            value = 0
            if s_status == 'C':
                value = gen_sc_prod_stat(id_sales_cycles, subscr_prod_indx[randint(0, len(subscr_prod_indx)-1)], id_subscr - 1)

            for index_a in range(0, randint(1, 4)):
                # skip if SalesCycle is NEW, mean without Activities
                if s_status == 'N':
                    continue

                a = ''
                a += '{\n'
                a += '    "pk": %i,\n' % (id_activities)
                a += '    "model": "alm_crm.Activity",\n'
                a += '    "fields": {\n'
                a += '        "title":"activity #%i of SalesCycle #%i",\n' % \
                    (index_a + 1, id_sales_cycles - 1)
                a += '        "description":"activity #%i of SalesCycle #%i",\n' %\
                    (index_a + 1, id_sales_cycles - 1)
                a += '        "date_created":"2014-%02i-%02i 00:00:00+00:00",\n' %\
                    (index_s%12 + 1, (index_a*2)%28 + 1)
                a += '        "sales_cycle": %i,\n' % (id_sales_cycles - 1)
                a += '        "owner":%i,\n' % (gen_user_id())
                a += '        "subscription_id": %i\n' % (id_subscr - 1)
                a += '    }\n'
                a += '},\n'
                f['activities'] += a
                id_activities += 1

                if s_status == 'C':
                    a = ''
                    a += '{\n'
                    a += '    "pk": %i,\n' % (id_activities)
                    a += '    "model": "alm_crm.Activity",\n'
                    a += '    "fields": {\n'
                    a += '        "title":"activity #%i of SalesCycle #%i",\n' % \
                        (index_a + 1, id_sales_cycles - 1)
                    a += '        "description":"Closed. Amount Value is #%i",\n' %\
                        value
                    a += '        "date_created":"2014-%02i-%02i 00:00:00+00:00",\n' %\
                        (index_s%12 + 1, (index_a*2)%28 + 1)
                    a += '        "sales_cycle": %i,\n' % (id_sales_cycles - 1)
                    a += '        "owner":%i,\n' % (gen_user_id())
                    a += '        "subscription_id": %i\n' % (id_subscr - 1)
                    a += '    }\n'
                    a += '},\n'
                    f['activities'] += a
                    id_activities += 1

                for index_c in range(0, randint(0, 3)):
                    c_owner = gen_user_id()
                    c_date = '2014-%02i-%02iT%02i:%02i:00.827Z' % (
                        index_s%12 + 1, (index_a*2)%28 + 1, index_c%23 + 1, randint(0, 59))

                    c = ''
                    c += '{\n'
                    c += '    "pk": %i,\n' % (id_comments)
                    c += '    "model": "alm_crm.Comment",\n'
                    c += '    "fields": {\n'
                    c += '        "comment":"%s - (by cmruser #%i, on activity #%i of sales_cycle #%i)",\n' % \
                        (comments[randint(0, 7)],
                         c_owner,
                         id_activities - 1,
                         id_sales_cycles - 1)
                    c += '        "owner":%i,\n' % (c_owner)
                    c += '        "date_created":"%s",\n' % (c_date)
                    c += '        "date_edited":"%s",\n' % (c_date)
                    c += '        "object_id":%i,\n' % (id_activities - 1)
                    c += '        "content_type":["alm_crm", "activity"],\n'
                    c += '        "subscription_id": %i\n' % (id_subscr - 1)
                    c += '    }\n'
                    c += '},\n'
                    f['comments'] += c
                    id_comments += 1
    
print 'created %i subscriptions'%(id_subscr-1)
print 'created %i companies'%(id_company-1)
print 'created %i users'%(id_user-1)
print 'created %i contacts'%(id_contact-1)
print 'created %i vcard'%(id_vcard-1)
print 'created %i emails'%(id_vcard_email-1)
print 'created %i crmusers'%(id_crmuser-1)
print 'created %i sales_cycles'%(id_sales_cycles-1)
print 'created %i activities'%(id_activities-1)
print 'created %i comments'%(id_comments-1)
print 'created %i products'%(id_product-1)
print 'created %i product stats'%(id_stat-1)


print "start writing to file"
for fname in f:
    f[fname] = '[\n' + f[fname][:-2] + '\n]'

    fixture_file = open('%s.json' % (fname), 'w+')
    fixture_file.write(f[fname])
    fixture_file.close()
print "finished writing"
print "GENERATED"