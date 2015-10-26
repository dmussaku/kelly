# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import shared_task
from almanet.celery import app
import xlrd
import time
import datetime
import os
import json
import itertools
from django.conf import settings
from alm_crm.models import (
    Contact, 
    ImportTask, 
    ErrorCell, 
    ContactList, 
    AttachedFile
    )
from almanet.models import (
    Subscription,
    Plan,
    Payment,
    BankStatement
    )
from alm_vcard import models as vcard_models
from alm_user.models import User
from celery import group, result, chord, task
import xlsxwriter
from django.core.mail import send_mail, EmailMessage
import logging

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

    def __init__(self, nrows, gsize, ignore_first_row=False):
        self.nrows = nrows
        self.gsize = gsize
        self.next_group = 0
        self.ignore_first_row = ignore_first_row
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
            return self.next_group+1

        self.next_group += self.gsize
        num = self.next_group - self.gsize
        if num == 0 and self.ignore_first_row:
            return num+1
        return self.next_group - self.gsize


def current_next_iter(nrows, gsize, ignore_first_row=False):
    a, b = itertools.tee(GroupSplitIterator(nrows, gsize, ignore_first_row), 2)
    next(b, None)
    return itertools.izip(a, b)

def grouped_contact_import_task(file_structure, filename, contact_list_name, creator, company_id, creator_email, ignore_first_row=False):
    book = xlrd.open_workbook(filename=os.path.join(TEMP_DIR, filename))
    sheet = book.sheets()[0]
    nrows = sheet.nrows
    import_task = ImportTask()
    import_task.save()
    task_list = [
        add_contacts_by_chunks.s(import_task.id, file_structure, filename, contact_list_name, creator.id, company_id, curg, nextg)
        for curg, nextg in current_next_iter(nrows, 100, ignore_first_row)
    ]
    chord_task = chord(task_list)(finish_add_contacts.s(filename, contact_list_name, import_task.id, creator.id, company_id, creator_email))
    import_task.uuid = chord_task.id
    import_task.filename = filename 
    import_task.save()
    return chord_task.id


@app.task
def add_contacts_by_chunks(import_task_id, file_structure, filename, contact_list_name, creator_id, company_id, start_row=0, fin_row=100):
    '''Task that will have file_structure, filename and start_col and finish col inputed
    this task will open the file and only parse selected rows'''
    creator = User.objects.get(id=creator_id)
    book = xlrd.open_workbook(filename=os.path.join(TEMP_DIR, filename))
    import_task = ImportTask.objects.get(id=import_task_id)
    sheet = book.sheets()[0]
    row_num = fin_row - start_row
    error_counter = 0
    for i in xrange(start_row, fin_row):
        try:
            data = sheet.row(i)
        except:
            continue
        response = Contact.create_from_structure(
            data, file_structure, creator, import_task, company_id)
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
def finish_add_contacts(list_of_responses, filename, contact_list_name, import_task_id, creator_id, company_id, creator_email):
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
                owner = creator,
                title = contact_list_name,
                company_id=company_id)
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
            to=[creator_email]
            )
        msg.attach_file(filename)
        msg.send()
        import_task.finished = True
        import_task.filename = filename
        import_task.save()
        os.remove(filename)
        return import_task.id

@app.task
def cleanup_inactive_files():
    logging.basicConfig(filename='files_cleanup.log', 
                        format='%(asctime)s - %(levelname)s - %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info("Clean up started.")
    inactive_files = filter(lambda file: not file.is_active, AttachedFile.objects.all())
    for _file in inactive_files:
        try:
            filename = _file.file_object.filename
            _file.delete()
        except Exception as e:
            logging.error("Error to delete file '%s': %s" % (filename, e.message))
        else:
            logging.info("File '%s' successfully deleted" % filename)

    logging.info("Clean up finished.")



@app.task
def create_payments():
    today = datetime.datetime.now()
    for company in Company.objects.all():
        payments = company.subscription.payments.all()
        if payments:
            last_payment = payments.last()
            pref_currency = last_payment.pref_currency
            current_plan = last_payment.plan
            if pref_currency == 'KZT':
                amount = plan.price_kzt
            elif pref_currency == 'USD':
                amount = plan.price_usd
            next_year = today.year
            next_month = today.month
            if next_month == 12:
                next_year += 1
                next_month = 1
            next_payment_delta = date(next_year, next_month, today.day) - today.date()
            new_payment = Payment(
                amount=amount,
                currency=pref_currency,
                date_to_pay=today + next_payment_delta,
                plan=last_payment.plan
                )
            new_payment.save()
        else:
            subscription = company.subscription
            if today - subscription.date_created > 31:
                next_year = today.year
                next_month = today.month
                if next_month == 12:
                    next_year += 1
                    next_month = 1
                next_payment_delta = date(next_year, next_month, today.day) - today.date()
                plan = Plan.objects.first()
                new_payment = Payment(
                    amount=plan.price_kzt,
                    currency='KZT',
                    date_to_pay=today + next_payment_delta,
                    plan=plan
                    )
                new_payment.save()    

