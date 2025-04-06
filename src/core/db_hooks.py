from django.db.backends.signals import connection_created
from django.db import connection

def set_dynamic_row_format(sender, connection, **kwargs):
    with connection.cursor() as cursor:
        cursor.execute("SET SESSION innodb_strict_mode=ON;")

connection_created.connect(set_dynamic_row_format)
