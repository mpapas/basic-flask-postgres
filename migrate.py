import psycopg2
from psycopg2 import pool

def migrate_db(db: pool.ThreadedConnectionPool) -> None:
    connection = db.getconn()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("CREATE TABLE transactions (date TEXT, amount REAL, account TEXT);")
    #except psycopg2.errors.DuplicateTable: -- Fix This: https://www.psycopg.org/docs/module.html#exceptions
    except psycopg2.errors.DuplicateTable:
        print("Table already exists")
        pass
    except psycopg2.Error as err:  # https://www.psycopg.org/docs/module.html#exceptions
        print(err)
        print(psycopg2.errorcodes.lookup(err.pgcode))
        if err.pgcode == "42P07":
            print("Table already exists")
            pass

    db.putconn(connection)
    