import psycopg2
import configparser

config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
# далее обращаемся как к обычному словарю
pg_dbname = config['Postgres']['pg_dbname']
pg_user = config['Postgres']['pg_user']
pg_userpass = config['Postgres']['pg_userpass']
pg_host = config['Postgres']['pg_host']
pg_port = config['Postgres']['pg_port']

t_name='users'


try:
    # connect to exist database
    conn = psycopg2.connect(f'postgresql://{pg_user}:{pg_userpass}@{pg_host}:{pg_port}/{pg_dbname}')
    conn.autocommit = True
    
    # the cursor for perfoming database operations
    cur = conn.cursor()
    
    # cur.execute(
    #     "SELECT version();"
    # )
    # print(f"Server version: {cur.fetchone()}")
    
    
    cur.execute(
        f"SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = '{t_name}');"
    )

    if not cur.fetchone():
        # create a table
        # cur.execute(
        #     """CREATE TABLE users(
        #         id serial PRIMARY KEY,
        #         first_name varchar(50) NOT NULL,
        #         nick_name varchar(50) NOT NULL);"""
        # )
        print("[INFO] Table created successfully")
    else:
        print('good')

    cur.execute("""
        INSERT INTO events (date_enent, user_id, ex_id, ex_count)
        VALUES (%s, %s, %s, %s);
        """,
        ('2023-7-3', 1,3,20))

# SELECT events.id, date_enent, users.name AS user, exercises.name AS exercise, ex_count AS count FROM events JOIN exercises ON events.ex_id = exercises.id JOIN users ON events.user_id = users.id;
    cur.execute(
        f"SELECT events.id, date_enent, users.name AS user, exercises.name AS exercise, ex_count AS count "
        f"FROM events JOIN exercises ON events.ex_id = exercises.id JOIN users ON events.user_id = users.id;"
    )
    print(cur.fetchall())





    # insert data into a table
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """INSERT INTO users (first_name, nick_name) VALUES
    #         ('Oleg', 'barracuda');"""
    #     )
        
    #     print("[INFO] Data was succefully inserted")
        
    # get data from a table
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """SELECT nick_name FROM users WHERE first_name = 'Oleg';"""
    #     )
        
    #     print(cursor.fetchone())
        
    # delete a table
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """DROP TABLE users;"""
    #     )
        
    #     print("[INFO] Table was deleted")
    
except Exception as _ex:
    #pass
    print("[ERR] Can`t establish connection to database", _ex)
finally:
    if conn:
        cur.close()
        conn.close()
        print("[INFO] PostgreSQL connection closed")
