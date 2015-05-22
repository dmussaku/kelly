# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
from almanet.celery import app
import xlrd
import time
import os
from almanet.settings import TEMP_DIR, EMAIL_SUBJECT_PREFIX, SUPPORT_EMAIL
from alm_crm.models import Contact, ImportTask, ErrorCell, ContactList
from alm_vcard import models as vcard_models
from alm_user.models import User
from celery import group, result, chord, task
import xlsxwriter
from django.core.mail import send_mail, EmailMessage

'''
celery -A alm_crm.tasks worker --loglevel=info
'''

# @app.task
# def add(args=None, x=0, y=0):
#     time.sleep(6)
#     print x+y

# @app.task
# def xsum(args=None, num=0):
#     time.sleep(6)
#     print args=None
#     print num
#     return num


@app.task
def mul(x, y):
    return x * y

@app.task
def nested_add(x,y):
    result_array = group(add.s(x,y) for i in range(0,2))
    result_array = result_array()
    return result_array.id



'''
this is the main task that will be executed from the api.py file
it will first cut the ranges of excel files by 100 and then it will
group the add_contacts_by_chunks task to execute concurently
'''

def check_task_status(uuid):
    response = task.Task.AsyncResult(uuid)
    return response.ready()

def grouped_contact_import_task(file_structure, filename, creator):
    book = xlrd.open_workbook(filename=TEMP_DIR + filename)
    sheet = book.sheets()[0]
    nrows = sheet.nrows
    print file_structure
    i = 0
    val_list = []
    l = range(0, nrows, 100)+[100*divmod(nrows,100)[0]+divmod(nrows,100)[1]+1]
    while i+1!=len(l):
        val_list.append((l[i],l[i+1]))
        i+=1
    print val_list
    import_task = ImportTask()
    import_task.save()
    chord_task = chord(
        [add_contacts_by_chunks.s(import_task.id, file_structure, filename, creator.id, obj[0], obj[1]) for obj in val_list]
        )(finish_add_contacts.s(filename, import_task.id, creator.id))
    import_task.uuid = chord_task.id
    import_task.filename = filename 
    import_task.save()
    return chord_task.id
'''
Task that will have file_structure, filename and start_col and finish col inputed
this task will open the file and only parse selected rows
'''
@app.task
def add_contacts_by_chunks(import_task_id, file_structure, filename, creator_id, start_row=0, finish_row=100):
    creator = User.objects.get(id=creator_id)
    book = xlrd.open_workbook(filename=TEMP_DIR+filename)
    import_task = ImportTask.objects.get(id=import_task_id)
    sheet = book.sheets()[0]
    row_num = finish_row - start_row
    error_counter = 0
    for i in range(start_row, finish_row-1):
        data = sheet.row(i)
        response = Contact.create_from_structure(
            data, file_structure, creator, import_task)
        if response['error']:
            error_cell = ErrorCell(
                import_task=import_task,
                row = i,
                data = str([obj.value for obj in data]),
                col = response['error_col']
                )
            error_cell.save()
            error_counter += 1
    return {'imported_num':row_num - error_counter, 'not_imported_num':error_counter}


'''
A task that creates a list of created contacts and sends a file containing rows with errors
also saves statistics in ImportTask model
'''        
@app.task
def finish_add_contacts(list_of_responses, filename, import_task_id, creator_id):
    os.remove(TEMP_DIR+filename)
    creator = User.objects.get(id=creator_id)
    print list_of_responses
    try:
        import_task = ImportTask.objects.get(id=import_task_id)
    except ObjectDoesNotExist:
        return False
    import_task.imported_num = 0
    import_task.not_imported_num = 0
    for dict_obj in list_of_responses:
        import_task.imported_num += dict_obj['imported_num']
        import_task.not_imported_num += dict_obj['not_imported_num']
    import_task.save()
    contact_list = ContactList(
                owner = creator.get_crmuser(),
                title = filename)
    contact_list.save()
    contact_list.contacts = import_task.contacts.all()
    contact_list.import_task = import_task
    contact_list.save()
    if not import_task.errorcell_set.all():    
        import_task.finished = True
        import_task.save()
        return import_task.id
    else:
        cell_list = import_task.errorcell_set.all()
        filename = TEMP_DIR + filename+'_edited.xlsx'
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        error_format = workbook.add_format()
        error_format.set_bg_color('red')
        for i in range(0,import_task.errorcell_set.count()):
            row = eval(cell_list[i].data)
            for j in range(len(row)):
                if j==cell_list[i].col:
                    worksheet.write(i, j, row[j], error_format)
                else:
                    worksheet.write(i, j, row[j])
        workbook.close()
        '''
        this is where i send a temp url or a file via email
        '''
        msg = EmailMessage(
            subject=EMAIL_SUBJECT_PREFIX+'файл с ошибками , do not reply',
            body='Исправьте файл и загрузите его снова',
            from_email=SUPPORT_EMAIL,
            to=['dmussaku@gmail.com']
            )
        msg.attach_file(filename)
        msg.send()
        import_task.finished = True
        import_task.filename = filename
        import_task.save()
        os.remove(filename)
        return import_task.id
