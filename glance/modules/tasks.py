import glance.app

@glance.app.celery.task
def add(x, y):
    """"""
    return x + y