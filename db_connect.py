import psycopg2
from config import host, user, password, db_name, port


try:
    # connect to exist database
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        db_name=db_name,
        port=port
    )

    # the cursor for perfoming database operations
    with connection.cursor() as cursor:
        pass

    # create table in PostgreSQL
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE users(
            user_id serial PRIMARY KEY,
            username
            tronscan_account
            reg_date
            upd_date)
            """
        )

except Exception as _ex:
    print('[INFO] Error while working with PostgreSQL', _ex)
finally:
    if connection:
        connection.close()
        print('[INFO] PostgreSQL connection closed')
