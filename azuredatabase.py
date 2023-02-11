import pyodbc
from datetime import datetime

server = 'logidb.database.windows.net'
database = 'logiDB'
username = 'login'
port ='1433'
password = '{Admin@123}'
driver= '{ODBC Driver 18 for SQL Server}'

with pyodbc.connect('Driver='+driver+';Server=tcp:'+server+','+port+';Database='+ database +';UID='+ username +';Pwd='+password) as conn:
    with conn.cursor() as cursor:
        def create_data():
            with conn:

                cursor.execute("""DROP TABLE IF EXISTS dbo.StudentLogin
                                  CREATE TABLE dbo.StudentLogin([Student_Name] nvarchar(20),[Student_Email] nvarchar(20),[Date_Time] nvarchar(20))""")


        def insert_data(name, dtstring):
            with conn:
                cursor.execute("INSERT INTO dbo.StudentLogin  (Student_Name ,Student_Email, Date_Time)VALUES(?, ?)",  name,dtstring)

        def exist_name(name, d1):
            cursor.execute("SELECT Student_Name FROM dbo.StudentLogin   ")
            row = cursor.fetchall()
            for ro in row:
                if (name == ro[0]):
                    return True
            return False
