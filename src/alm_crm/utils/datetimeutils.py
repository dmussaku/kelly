from datetime import datetime, timedelta, time

def get_start_of_today(d):
    return datetime.combine(d, time.min)

def get_end_of_today(d):
    return datetime.combine(d, time.max)

def get_start_of_week(d):
    start = d - timedelta(days=d.weekday())
    return datetime.combine(start, time.min)

def get_end_of_week(d):
    start = d - timedelta(days=d.weekday())
    return datetime.combine(start + timedelta(days=6), time.max)

def get_start_of_month(d):
    start = d.replace(day=1)
    return datetime.combine(start, time.min)

def get_end_of_month(d):
    start = d.replace(day=28) + timedelta(days=4)  # this will never fail
    return datetime.combine(start - timedelta(days=start.day), time.max)
