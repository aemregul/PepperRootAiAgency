import sys
import psycopg2

try:
    conn = psycopg2.connect("dbname=pepperroot user=postgres host=localhost password=postgres")
    cur = conn.cursor()
    cur.execute("SELECT content FROM messages WHERE role='assistant' ORDER BY created_at DESC LIMIT 3")
    rows = cur.fetchall()
    for row in rows:
        print(row[0])
except Exception as e:
    print(e)
