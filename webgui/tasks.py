from celery import Celery

app = Celery('tasks', broker='sqlite3://guest@localhost//')


BROKER_URL = 'sqla+sqlite:///celerydb.sqlite'





