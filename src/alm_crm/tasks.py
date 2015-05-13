from __future__ import absolute_import
from celery import shared_task
from almanet.celery import app
import xlrd
import time
from almanet.settings import BASE_DIR
from alm_crm.models import Contact, ImportTask, ErrorCell
from alm_vcard import models as vcard_models
from celery import group, result
import xlsxwriter

'''
celery -A alm_crm.tasks worker --loglevel=info
'''

@app.task
def add(x, y):
    return {'result':x + y}


@app.task
def mul(x, y):
    return x * y

def nested_add(x,y):
    result_array = group(add.s(x,y) for i in range(0,2))
    result_array = result_array()
    return result_array.id

@app.task
def xsum(numbers):
    return sum(numbers)

'''
this is the main task that will be executed from the api.py file
it will first cut the ranges of excel files by 100 and then it will
group the add_contacts_by_chunks task to execute concurently
'''


def grouped_contact_import_task(file_structure, filename, creator):
    book = xlrd.open_workbook(filename=BASE_DIR+'/'+filename)
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
    grouped_task = group(
        [add_contacts_by_chunks.s(import_task.id, file_structure, filename, creator.id, obj[0], obj[1]) for obj in val_list]
        )
    job = grouped_task.apply_async()
    job.save()
    import_task.uuid=job.id
    import_task.save()
    return job.id
'''
Task that will have file_structure, filename and start_col and finish col inputed
this task will open the file and only parse selected rows
'''
@app.task
def add_contacts_by_chunks(import_task_id, file_structure, filename, creator_id, start_row=0, finish_row=100):
    creator = User.objects.get(id=creator_id)
    book = xlrd.open_workbook(filename=filename)
    import_task = ImportTask.objects.get(id=import_task_id)
    sheet = book.sheets()[0]
    for i in range(start_row, finish_row):
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

        
@app.task
def create_failed_contacts_xls(filename, import_task):
    if not import_task.errorcell_set.all():    
        return False
    cell_list = import_task.errorcell_set.all()
    workbook = xlsxwriter.Workbook(BASE_DIR+filename+'_edited.xlsx')
    worksheet = workbook.add_worksheet()
    error_format = workbook.add_format()
    error_format.set_bg_color('red')
    for i in range(0,import_task.errorcell_set.count()):
        for j in range(len(cell_list)):
            if j==cell_list[i].col:
                worksheet.write(i, j, cell_list[j], error_format)
            else:
                worksheet.write(i, j, cell_list[j])
    workbook.close()
    import_task.filename = filename +  '_edited.xlsx'
    import_task.save()
    return import_task
