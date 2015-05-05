from __future__ import absolute_import
from celery import shared_task
from almanet.celery import app
import xlrd
import time
from almanet.settings import TEMP_DIR
from .models import Contact

@app.task
def add(x, y):
    time.sleep(10)
    return {'result':x + y}


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)

@app.task
def add_contacts_from_xls(file_structure, filename):
    book = xlrd.open_workbook(filename=filename)
