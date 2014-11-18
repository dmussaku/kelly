from random import randint


#add objects into fixture activities
activity_file = open('activities.json', 'w')

activity_file.write( '[\n')

for i in range(1, 301):
	j=randint(1,10) # generate randomly values for sales_cycles 
	k=randint(1,4) # generate randomly values for owners
	activity_file.write( '	{\n')
	activity_file.write( '		"pk": %i,\n'%i)
	activity_file.write( '		"model": "alm_crm.Activity",\n')
	activity_file.write( '		"fields": {\n')
	activity_file.write( '			"title":"t%i",\n'%i)
	activity_file.write( '			"description":"d%i",\n'%i)
	activity_file.write( '			"date_created":"2014-09-11 00:00:00+00:00",\n')
	activity_file.write( '			"sales_cycle":%i,\n'%j)
	activity_file.write( '			"owner":%i\n'%k)
	activity_file.write( '		}\n')
	if i != 300:
		activity_file.write( '	},\n')
	else:
		activity_file.write( '	}\n')


activity_file.write( ']\n')

activity_file.close()


#add objects into fixture comments
comment_file = open('comments.json', 'w')

comment_file.write( '[\n')

for i in range(1, 1501):
	j=randint(1,300) # generate randomly values for activities
	k=randint(1,4) # generate randomly values for owners
	comment_file.write( '	{\n')
	comment_file.write( '		"pk": %i,\n'%i)
	comment_file.write( '		"model": "alm_crm.Comment",\n')
	comment_file.write( '		"fields": {\n')
	comment_file.write( '			"comment":"Test comment %i",\n'%i)
	comment_file.write( '			"owner":%i,\n'%k)
	comment_file.write( '			"date_created":"2014-09-11 00:00:00+00:00",\n')
	comment_file.write( '			"date_edited":"2014-09-11 00:00:00+00:00",\n')
	comment_file.write( '			"object_id":%i,\n'%j)
	comment_file.write( '			"content_type":34\n')
	comment_file.write( '		}\n')
	if i != 300:
		comment_file.write( '	},\n')
	else:
		comment_file.write( '	}\n')


comment_file.write( ']\n')

comment_file.close()

