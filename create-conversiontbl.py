# Simple loader file to create sqlite DB from the PATH_ROW_TO_UTM_ZONE.ldr file

import sqlite3
import os


base_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(base_path, 'conversion-table.db')
ldr_path = os.path.join(base_path, 'PATH_ROW_TO_UTM_ZONE.ldr')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute(r'CREATE TABLE conversion (path int, row int, zone int)')
conn.commit()

with open(ldr_path, 'r') as f:
    for _ in range(11):
        next(f)
    for line in f:
        row = line.strip().split('|')
        cursor.execute('INSERT INTO conversion VALUES (?,?,?)', row)

conn.commit()
conn.close()
