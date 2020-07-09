import pyodbc
from pprint import pprint
import sys

CEGID_HOST = '192.168.1.45,50887'
CEGID_USER = 'cegidlogin'
CEGID_PASSWORD = 'cegidpassword'
CEGID_DATABASE = 'GEPROGRESSIS'


if __name__ == '__main__':
    conn = pyodbc.connect('DRIVER=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.2.1;SERVER={};DATABASE={};UID={};PWD={}'.format(CEGID_HOST, CEGID_DATABASE, CEGID_USER, CEGID_PASSWORD))
    conn2 = pyodbc.connect('DRIVER=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.2.1;SERVER={};DATABASE={};UID={};PWD={}'.format(CEGID_HOST, CEGID_DATABASE, CEGID_USER, CEGID_PASSWORD))
    cursor = conn.cursor()
    cursor2 = conn2.cursor()
    cursor.execute("SELECT TABLE_NAME FROM GEPROGRESSIS.INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")


    search = sys.argv[1]
    tables = []
    for row in cursor:
        tables.append(row.TABLE_NAME)

    for table in tables:
        cursor.execute("SELECT c.name 'Column Name', t.Name 'Data type', c.max_length 'Max Length', c.precision , c.scale , c.is_nullable, ISNULL(i.is_primary_key, 0) 'Primary Key' FROM sys.columns c INNER JOIN  sys.types t ON c.user_type_id = t.user_type_id LEFT OUTER JOIN  sys.index_columns ic ON ic.object_id = c.object_id AND ic.column_id = c.column_id LEFT OUTER JOIN  sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id WHERE c.object_id = OBJECT_ID('{}')".format(table))
        for row in cursor:
            if row[1] == 'varchar':
                # recherche dans le champ
                sql = "SELECT * FROM {} WHERE {} LIKE '%{}%'".format(table, row[0], search)
                cursor2.execute(sql)
                for row2 in cursor2:
                    print("\033[91mFOUND : {}, {}\033[0m".format(table, row[0]))
                    """
                    for key, val in row2.items():
                        print("\033[1m{}\033[0m: \t{}".format(key, val))
                    """
