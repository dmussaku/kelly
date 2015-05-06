from __future__ import absolute_import
from celery import shared_task
from almanet.celery import app
import xlrd
import time
from almanet.settings import TEMP_DIR
from .models import Contact, ImportTask, ErrorCell
from alm_vcard import models as vcard_models
from celery import group

@app.task
def add(x, y):
    return {'result':x + y}


@app.task
def mul(x, y):
    return x * y

def nested_add(x,y):
    result_array = group(add.s(x,y) for i in range(0,2))
    result_array = result_array()
    return result_array

@app.task
def xsum(numbers):
    return sum(numbers)

'''
this is the main task that will be executed from the api.py file
it will first cut the ranges of excel files by 100 and then it will
group the add_contacts_by_chunks task to execute concurently
'''

@app.task
def grouped_contact_import_task(file_structure, filename, creator):
    book = xlrd.open_workbook(filename=filename)
    sheet = book.sheets()[0]
    nrows = sheet.nrows
    i = 0
    val_list = []
    l = range(0, nrows, 100)+[100*divmod(nrows,100)[0]+divmod(nrows,100)[1]+1]
    while i+1!=len(l):
        val_list.append((l[i],l[i+1]))
        i+=1
    import_task = ImportTask()
    import_task.save()
    grouped_task = group(
        [add_contacts_by_chunks.s(import_task, file_structure, filename, creator, obj[0], obj[1]) for obj in val_list]
        )()
    import_task.uuid = grouped_task.id
    import_task.save()
    return grouped_task.id
'''
Task that will have file_structure, filename and start_col and finish col inputed
this task will open the file and only parse selected rows
'''
@app.task
def add_contacts_by_chunks(import_task, file_structure, filename, creator, start_col=0, finish_col=100):
    book = xlrd.open_workbook(filename=filename)
    sheet = book.sheets()[0]
    for i in range(start_col, finish_col):
        data = sheet.row(i)
        response = Contact.create_from_structure(
            data, file_structure, creator, import_task)
        if response['error']:
            error_cell = ErrorCell(
                import_task=import_task,
                row = i,
                col = response['error_col']
                )
            error_cell.save()

        

