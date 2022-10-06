import psycopg2
import settings
import time


# DSN = 'dbname={} user={} password={}'.format(settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD)
# DSN = 'user={} password={}'.format(settings.DB_USER, settings.DB_PASSWORD)

def migration_1():
    # conn = psycopg2.connect(DSN, )
    # curs = conn.cursor()
    connection = False
    time.sleep(5.0) # waiting until db initializes in a container
    try:
        # DSN = 'user={} password={} host={}'.format(settings.DB_USER, settings.DB_PASSWORD, '127.0.0.1')
        # DSN = 'dbname={} user={} password={} host={}'.format(settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD, 'db')
        DSN = 'user={} password={} host={}'.format(settings.DB_USER, settings.DB_PASSWORD, settings.DB_HOST)
        connection = psycopg2.connect(DSN)
        # connection.autocommit = True
        connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as curs:
            # cursor.execute("CREATE DATABASE foo")
            # with psycopg2.connect(DSN) as conn:
            #     conn.autocommit = False
            #     with conn.cursor() as curs:

            curs.execute("""
            DROP DATABASE IF EXISTS {0};
            """.format(settings.DB_NAME, settings.DB_USER))

            curs.execute("""
            CREATE DATABASE {0}
            WITH 
            OWNER = {1}
            TABLESPACE = pg_default
            CONNECTION LIMIT = -1;
            """.format(settings.DB_NAME, settings.DB_USER))
        connection.close()
 
        time.sleep(3.0)
        DSN = 'dbname={} user={} password={} host={}'.format(settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD, 'db')
        connection = psycopg2.connect(DSN)
        connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as curs:
            curs.execute("""
            CREATE TABLE IF NOT EXISTS {0}.public.accounts
            (
                client_id integer NOT NULL,
                sum real,
                CONSTRAINT accounts_pkey PRIMARY KEY (client_id)
            )

            TABLESPACE pg_default;
             """.format(settings.DB_NAME, settings.DB_USER))

            curs.execute("""
            ALTER TABLE IF EXISTS public.accounts
                OWNER to {1};
             """.format(settings.DB_NAME, settings.DB_USER))

            curs.execute("""
            CREATE TABLE IF NOT EXISTS public.history
            (
                transaction_id text COLLATE pg_catalog."default" NOT NULL,
                client_id integer,
                sum real,
                operation text COLLATE pg_catalog."default",
                status text COLLATE pg_catalog."default",
                n integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
                CONSTRAINT history_pkey PRIMARY KEY (transaction_id)
            )

            TABLESPACE pg_default;
             """.format(settings.DB_NAME, settings.DB_USER))

            curs.execute("""
            ALTER TABLE IF EXISTS public.history
                OWNER to {1};
             """.format(settings.DB_NAME, settings.DB_USER))
    finally:
        if connection:
            connection.close()
        print("migration_1 end")


if __name__ == '__main__':
    migration_1()