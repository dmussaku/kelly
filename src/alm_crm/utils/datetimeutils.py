from datetime import timedelta, time

def get_start_of_today(d):
    return d.replace(hour=time.min.hour, minute=time.min.minute, second=time.min.second)

def get_end_of_today(d):
    return d.replace(hour=time.max.hour, minute=time.max.minute, second=time.max.second)

def get_start_of_week(d):
    start = d - timedelta(days=d.weekday())
    return start.replace(hour=time.min.hour, minute=time.min.minute, second=time.min.second)

def get_end_of_week(d):
    start = d - timedelta(days=d.weekday()) + timedelta(days=6)
    return start.replace(hour=time.max.hour, minute=time.max.minute, second=time.max.second)

def get_start_of_month(d):
    start = d.replace(day=1)
    return start.replace(hour=time.min.hour, minute=time.min.minute, second=time.min.second)

def get_end_of_month(d):
    start = d.replace(day=28) + timedelta(days=4)  # this will never fail
    return (start - timedelta(days=start.day)).replace(hour=time.max.hour, minute=time.max.minute, second=time.max.second)
