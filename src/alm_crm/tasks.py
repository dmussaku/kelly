# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
from almanet.celery import app
import xlrd
import time
import os
import json
import itertools
from django.conf import settings
from alm_crm.models import Contact, ImportTask, ErrorCell, ContactList
from alm_vcard import models as vcard_models
from alm_user.models import User
from celery import group, result, chord, task
import xlsxwriter
from django.core.mail import send_mail, EmailMessage

TEMP_DIR = getattr(settings, 'TEMP_DIR')
EMAIL_SUBJECT_PREFIX = getattr(settings, 'EMAIL_SUBJECT_PREFIX')
SUPPORT_EMAIL = getattr(settings, 'SUPPORT_EMAIL')

'''
celery -A alm_crm.tasks worker --loglevel=info
this is the main task that will be executed from the api.py file
it will first cut the ranges of excel files by 100 and then it will
group the add_contacts_by_chunks task to execute concurently
'''

def check_task_status(uuid):
    response = task.Task.AsyncResult(uuid)
    return response.ready()


class GroupSplitIterator(object):

    def __init__(self, nrows, gsize):
        self.nrows = nrows
        self.gsize = gsize
        self.next_group = 0
        self.__should_stop = False

    def __iter__(self):
        return self

    def next(self):
        if self.__should_stop:
            raise StopIteration

        if self.next_group == self.nrows:
            self.__should_stop = True
        elif self.next_group > self.nrows:
            self.__should_stop = True
            self.next_group -= self.gsize
            self.next_group += (self.nrows - self.next_group)
            return self.next_group

        self.next_group += self.gsize
        return self.next_group - self.gsize


def current_next_iter(nrows, gsize):
    a, b = itertools.tee(GroupSplitIterator(nrows, gsize), 2)
    next(b, None)
    return itertools.izip(a, b)

def grouped_contact_import_task(file_structure, filename, creator, ignore_first_row=False):
    book = xlrd.open_workbook(filename=os.path.join(TEMP_DIR, filename))
    sheet = book.sheets()[0]
    nrows = sheet.nrows
    i = 0
    import_task = ImportTask()
    import_task.save()
    chord_task = chord([
        add_contacts_by_chunks.s(import_task.id, file_structure, filename, creator.id, curg, nextg)
        for curg, nextg in current_next_iter(nrows, 100)
    ])(finish_add_contacts.s(filename, import_task.id, creator.id))
    import_task.uuid = chord_task.id
    import_task.filename = filename 
    import_task.save()
    return chord_task.id


@app.task
def add_contacts_by_chunks(import_task_id, file_structure, filename, creator_id, start_row=0, fin_row=100):
    '''Task that will have file_structure, filename and start_col and finish col inputed
    this task will open the file and only parse selected rows'''
    creator = User.objects.get(id=creator_id)
    book = xlrd.open_workbook(filename=os.path.join(TEMP_DIR, filename))
    import_task = ImportTask.objects.get(id=import_task_id)
    sheet = book.sheets()[0]
    row_num = fin_row - start_row
    error_counter = 0
    for i in xrange(start_row, fin_row - 1):
        data = sheet.row(i)
        response = Contact.create_from_structure(
            data, file_structure, creator, import_task)
        if response['error']:
            error_cell = ErrorCell(
                import_task=import_task,
                row=i,
                data=json.dumps([obj.value for obj in data]),
                col=response['error_col'])
            error_cell.save()
            error_counter += 1
    return {'imported_num':row_num - error_counter, 'not_imported_num': error_counter}


@app.task
def finish_add_contacts(list_of_responses, filename, import_task_id, creator_id):
    '''A task that creates a list of created contacts and sends a file containing rows with errors
    also saves statistics in ImportTask model'''    
    os.remove(os.path.join(TEMP_DIR, filename))
    creator = User.objects.get(id=creator_id)
    try:
        import_task = ImportTask.objects.get(id=import_task_id)
    except ObjectDoesNotExist:
        return False
    # acc result in import_task object
    import_task.imported_num = 0
    import_task.not_imported_num = 0
    for dict_obj in list_of_responses:
        import_task.imported_num += dict_obj['imported_num']
        import_task.not_imported_num += dict_obj['not_imported_num']
    import_task.save()

    # filter bad contacts
    contact_list = ContactList(
                owner = creator.get_crmuser(),
                title = filename)
    contact_list.save()
    for contact in import_task.contacts.all():
        if not contact.vcard:
            contact.delete()
    contact_list.contacts = import_task.contacts.all()
    contact_list.import_task = import_task
    contact_list.save()

    # prepare result either ok or error
    if not import_task.errorcell_set.all():    
        import_task.finished = True
        import_task.save()
        return import_task.id
    else:
        cell_list = import_task.errorcell_set.all()
        filename = os.path.join(TEMP_DIR, filename+'_edited.xlsx')
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        error_format = workbook.add_format()
        error_format.set_bg_color('red')
        for i in range(0,import_task.errorcell_set.count()):
            row = json.loads(cell_list[i].data)
            for j in range(len(row)):
                if j == cell_list[i].col:
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
            to=[creator.email]
            )
        msg.attach_file(filename)
        msg.send()
        import_task.finished = True
        import_task.filename = filename
        import_task.save()
        os.remove(filename)
        return import_task.id
