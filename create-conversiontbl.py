# Simple loader file to create sqlite DB from the PATH_ROW_TO_UTM_ZONE.ldr file

import sqlite3
import os


base_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(base_path, 'conversion-table.db')
ldr_path = os.path.join(base_path, 'PATH_ROW_TO_UTM_ZONE.ldr')
ps_path = os.path.join(base_path, 'ps-antarctic.csv')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute(r'CREATE TABLE conversion (path integer, row integer, zone text)')
conn.commit()

# Load database with default values that LPSG uses
with open(ldr_path, 'r') as f:
    for _ in range(11):
        next(f)
    for line in f:
        row = line.strip().split('|')
        cursor.execute('INSERT INTO conversion VALUES (?,?,?)', row)

# Update path/rows for polar stereographic
with open(ps_path, 'r') as f:
    for line in f:
        row = line.strip().split(',')
        cursor.execute('UPDATE conversion SET zone = "3031" WHERE path = ? AND row = ?', row)

conn.commit()
conn.close()
