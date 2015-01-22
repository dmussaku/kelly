from random import randint

comments = ('The week also lifts the lid on the thinking of Federal Reserve.',
            'Data on US housing starts for October will also be released.',
            'Monday brings the delayed start of the Shanghai-Hong Kong exchange link, when cross-trading of shares on the two exchanges is due to start in a move that would open up China` $4.2 trillion stock market to foreigners',
            'Also due on Monday are US industrial production statistics for October and the start of the Chicago Fed`s annual agriculture conference.',
            'Tuesday brings the Los Angeles Auto Show, earnings from Home Depot and the expected $2 billion-plus initial public offering (IPO) of real estate investment trust Paramount Group.',
            'Also expected on Thursday are an update on existing home sales and earnings from Gap, BestBuy and Dollar Tree.',
            'Friday brings a US Senate hearing on the New York Federal Reserve, which has been accused of being too cosy with the Wall Street banks it is supposed to regulate.',
            'The Senate Banking panel`s Subcommittee on Financial Institutions and Consumer Protection will host the hearing.',
            )


fixture_sales_cycles = ''
fixture_values = ''
fixture_activities = ''
fixture_comments = ''

id_sales_cycles = 1
id_values = 1
id_activities = 1
id_comments = 1

for contact_id in range(1, 11):

    # 3 sales_cycle for ever contact
    for index_s in range(0, 3):

        s_status = ('N', 'P', 'C')[randint(0, 2)]

        s = ''
        s += '{\n'
        s += '    "pk": %i,\n' % (id_sales_cycles)
        s += '    "model": "alm_crm.SalesCycle",\n'
        s += '    "fields": {\n'
        s += '        "is_global":%s,\n' % ('true' if id_sales_cycles==1 else 'false')
        s += '        "title":"SalesCycle #%i",\n' % (id_sales_cycles)
        # s += '        "products":[%i],\n' % (randint(1, 4))
        s += '        "owner":%i,\n' % (randint(1, 3))
        s += '        "followers":[],\n'
        s += '        "contact":%i,\n' % (contact_id)
        s += '        "latest_activity":%s,\n' % 'null'  #('null' if s_status=='N' else str(id_activities+1))
        s += '        "projected_value":%i,\n' % (id_values)
        s += '        "real_value":%i,\n' % (id_values + 1)
        s += '        "status":"%s",\n' % (s_status)
        s += '        "date_created":"2014-%02i-10 00:00:00+00:00",\n' % \
            (index_s + 1)
        s += '        "from_date":"2014-%02i-10 00:00:00+00:00",\n' % \
            (index_s + 1)
        s += '        "to_date":"2014-%02i-10 00:00:00+00:00",\n' % \
            (index_s + 3)
        s += '        "subscription_id":1\n'
        s += '    }\n'
        s += '},\n'
        id_sales_cycles += 1
        fixture_sales_cycles += s

        # 2 values: real and projected
        for index_v in range(0, 2):
            v = ''
            v += '{\n'
            v += '    "pk": %i, \n' % (id_values)
            v += '    "model": "alm_crm.Value", \n'
            v += '    "fields": {\n'
            v += '        "salary":"monthly",\n'
            v += '        "amount":%i,\n' % (5000*randint(1, 10))
            v += '        "currency":"KZT",\n'
            v += '        "subscription_id":1\n'
            v += '    }\n'
            v += '},\n'
            id_values += 1
            fixture_values += v

        # 10 activities
        for index_a in range(0, 10):
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
                (index_s + 1, index_a*2 + 1)
            a += '        "sales_cycle":%i,\n' % (id_sales_cycles - 1)
            a += '        "owner":%i,\n' % (randint(1, 4))
            a += '        "subscription_id":1\n'
            a += '    }\n'
            a += '},\n'
            id_activities += 1
            fixture_activities += a

            # 3-10 comments on activity
            for index_c in range(1, randint(3, 10)):
                c_owner = randint(1, 3)
                c_date = '2014-%02i-%02iT%02i:%02i:00.827Z' % (
                    index_s + 1, index_a*2 + 1, index_c + 1, randint(0, 59))

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
                c += '        "subscription_id":1\n'
                c += '    }\n'
                c += '},\n'
                id_comments += 1
                fixture_comments += c


# for Second Company with another Subcription
for contact_id in range(11, 15):
    # 2 sales_cycle for ever contact
    for index_s in range(0, 2):

        s_status = ('N', 'P', 'C')[randint(0, 2)]

        s = ''
        s += '{\n'
        s += '    "pk": %i,\n' % (id_sales_cycles)
        s += '    "model": "alm_crm.SalesCycle",\n'
        s += '    "fields": {\n'
        s += '        "is_global":%s,\n' % ('true' if contact_id==12 else 'false')
        s += '        "title":"SalesCycle #%i",\n' % (id_sales_cycles)
        # s += '        "products":[%i],\n' % (randint(1, 4))
        s += '        "owner":5,\n'
        s += '        "followers":[],\n'
        s += '        "contact":%i,\n' % (contact_id)
        s += '        "latest_activity":%s,\n' % 'null'  #  ('null' if s_status=='N' else str(id_activities+1))
        s += '        "projected_value":%i,\n' % (id_values)
        s += '        "real_value":%i,\n' % (id_values + 1)
        s += '        "status":"%s",\n' % (s_status)
        s += '        "date_created":"2014-%02i-10 00:00:00+00:00",\n' % \
            (index_s + 1)
        s += '        "from_date":"2014-%02i-10 00:00:00+00:00",\n' % \
            (index_s + 1)
        s += '        "to_date":"2014-%02i-10 00:00:00+00:00",\n' % \
            (index_s + 3)
        s += '        "subscription_id":2\n'
        s += '    }\n'
        s += '},\n'
        id_sales_cycles += 1
        fixture_sales_cycles += s

        # 2 values: real and projected
        for index_v in range(0, 2):
            v = ''
            v += '{\n'
            v += '    "pk": %i, \n' % (id_values)
            v += '    "model": "alm_crm.Value", \n'
            v += '    "fields": {\n'
            v += '        "salary":"monthly",\n'
            v += '        "amount":%i,\n' % (5000*randint(1, 10))
            v += '        "currency":"KZT",\n'
            v += '        "subscription_id":2\n'
            v += '    }\n'
            v += '},\n'
            id_values += 1
            fixture_values += v

        # 7 activities
        for index_a in range(1, 7):
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
                (index_s + 1, index_a*2 + 1)
            a += '        "sales_cycle":%i,\n' % (id_sales_cycles - 1)
            a += '        "owner":5,\n'
            a += '        "subscription_id":2\n'
            a += '    }\n'
            a += '},\n'
            id_activities += 1
            fixture_activities += a

            # 2-5 comments on activity
            for index_c in range(0, randint(2, 5)):
                c_date = '2014-%02i-%02iT%02i:%02i:00.827Z' % (
                    index_s + 1, index_a*2 + 1, index_c + 1, randint(0, 59))

                c = ''
                c += '{\n'
                c += '    "pk": %i,\n' % (id_comments)
                c += '    "model": "alm_crm.Comment",\n'
                c += '    "fields": {\n'
                c += '        "comment":"%s - (by cmruser #%i, on activity #%i of sales_cycle #%i)",\n' % \
                    (comments[randint(0, 7)],
                     5,
                     id_activities - 1,
                     id_sales_cycles - 1)
                c += '        "owner":5,\n'
                c += '        "date_created":"%s",\n' % (c_date)
                c += '        "date_edited":"%s",\n' % (c_date)
                c += '        "object_id":%i,\n' % (id_activities - 1)
                c += '        "content_type":["alm_crm", "activity"],\n'
                c += '        "subscription_id":2\n'
                c += '    }\n'
                c += '},\n'
                id_comments += 1
                fixture_comments += c


fixture_sales_cycles = '[\n' + fixture_sales_cycles[:-2] + '\n]'
fixture_activities = '[\n' + fixture_activities[:-2] + '\n]'
fixture_values = '[\n' + fixture_values[:-2] + '\n]'
fixture_comments = '[\n' + fixture_comments[:-2] + '\n]'


#add objects into fixture activities
file_activities = open('activities.json', 'w')
file_activities.write(fixture_activities)
file_activities.close()

file_sales_cycles = open('sales_cycles.json', 'w')
file_sales_cycles.write(fixture_sales_cycles)
file_sales_cycles.close()

file_values = open('values.json', 'w')
file_values.write(fixture_values)
file_values.close()

file_comments = open('comments.json', 'w')
file_comments.write(fixture_comments)
file_comments.close()


# for i in range(1, 301):
#     j=randint(1,10) # generate randomly values for sales_cycles
#     k=randint(1,4)  # generate randomly values for owners
#     activity_file.write(' {\n')
#     activity_file.write('   "pk": %i,\n'%i)
#     activity_file.write('   "model": "alm_crm.Activity",\n')
#     activity_file.write('   "fields": {\n')
#     activity_file.write('     "title":"t%i",\n'%i)
#     activity_file.write('     "description":"d%i",\n'%i)
#     activity_file.write('     "date_created":"2014-09-11 00:00:00+00:00",\n')
#     activity_file.write('     "sales_cycle":%i,\n'%j)
#     activity_file.write('     "owner":%i\n'%k)
#     activity_file.write('   }\n')
#     if i != 300:
#         activity_file.write(' },\n')
#     else:
#         activity_file.write(' }\n')


# activity_file.write( ']\n')

# activity_file.close()


# #add objects into fixture comments
# comment_file = open('comments.json', 'w')

# comment_file.write( '[\n')

# for i in range(1, 1501):
#     j=randint(1,300) # generate randomly values for activities
#     k=randint(1,4) # generate randomly values for owners
#     comment_file.write( ' {\n')
#     comment_file.write( '   "pk": %i,\n'%i)
#     comment_file.write( '   "model": "alm_crm.Comment",\n')
#     comment_file.write( '   "fields": {\n')
#     comment_file.write( '     "comment":"Test comment %i",\n'%i)
#     comment_file.write( '     "owner":%i,\n'%k)
#     comment_file.write( '     "date_created":"2014-09-11 00:00:00+00:00",\n')
#     comment_file.write( '     "date_edited":"2014-09-11 00:00:00+00:00",\n')
#     comment_file.write( '     "object_id":%i,\n'%j)
#     comment_file.write( '     "content_type":34\n')
#     comment_file.write( '   }\n')
#     if i != 300:
#         comment_file.write( ' },\n')
#     else:
#         comment_file.write( ' }\n')


# comment_file.write( ']\n')

# comment_file.close()
