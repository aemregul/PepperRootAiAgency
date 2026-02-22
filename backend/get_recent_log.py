import json
import sqlite3
# Let's check recent database messages to see if there is a background message indicating video status
import uuid
import datetime

import psycopg2
conn = psycopg2.connect("dbname=pepperroot user=pepperroot password=postgres host=localhost")
cur = conn.cursor()
cur.execute("SELECT content FROM messages ORDER BY created_at DESC LIMIT 5")
rows = cur.fetchall()
for r in rows:
    print(r[0])
