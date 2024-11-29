import pymysql
import pymysql.cursors
import random
import datetime
import dateutil.relativedelta

# root root football
# login
con = pymysql.connect(
    host='localhost',
    port=3306,
    user="root",
    password="root",
    db='Football'
)

cur = con.cursor()
cur.execute("SELECT * FROM Clubs")
rows = cur.fetchall()
for row in rows:
    print(row)



def createRandomDate():
    year = random.randint(1980, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime.date(year, month, day)

def createMatchRandom():
        


