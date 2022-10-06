from typing import Dict, Any

from flask import Flask
import psycopg2
import queue
import uuid6
import threading
import enum
import migrate
import my_test

import settings

class Operation(enum.Enum):
    PUT = 1
    WITHDRAW = 2

DSN = 'dbname={} user={} password={} host={}'.format(settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD, settings.DB_HOST)
# Q: dict[int, queue.Queue] = {} # Queues
Q = {} # Queues
app = Flask(__name__)
lock = threading.Lock()

class Command():
    def __init__(self, client_id, sum, transaction_id, operation):
        self.client_id = client_id
        self.sum = sum
        self.transaction_id = transaction_id
        self.operation = operation

    def __str__(self):
        return 'Command: {} Client_ID: {} Summ: {} Operation: {}'.format(self.transaction_id, self.client_id, self.sum, self.operation)

@app.route("/<int:client_id>/<float:sum>/<string:op>")
def server(client_id, sum, op):

    transaction_id = uuid6.uuid6()
    if op == "put":
        operation = Operation.PUT
    elif op == "withdraw":
        operation = Operation.WITHDRAW
    else:
        return "Wrong operation type: {}. Must be: put | withdraw.".format(op)

    try:
        with psycopg2.connect(DSN) as conn:
            with conn.cursor() as curs:
                curs.execute("""
                INSERT INTO history VALUES (%s, %s, %s, %s, %s)
                """, (str(transaction_id), client_id, sum, str(operation), 'pending'))

        add_operation_to_Q(transaction_id, client_id, sum, operation)

        return f'{transaction_id}'
    except:
        return "Error: something goes wrong"


def add_operation_to_Q(transaction_id, client_id, sum, operation):
    if not (client_id in Q):
        with lock:
            Q[client_id] = queue.Queue()

    Q[client_id].put(Command(client_id, sum, transaction_id, operation))

def main_loop():
    while True:
        items = Q.items()
        for i in items:
            (client_id, q) = i

            c = q.get() # command
            with psycopg2.connect(DSN) as conn:
                with conn.cursor() as curs:
                    curs.execute("""
                    SELECT sum FROM accounts
                    WHERE client_id = %s 
                    """, (c.client_id, ))
                    result_set = curs.fetchone()
                    if result_set == None:
                        curs.execute("""
                        INSERT INTO accounts VALUES (%s, %s)
                        """, (c.client_id, 0))
                        sum = 0
                    else:
                        (sum, ) = result_set

                    new_sum = sum + c.sum if c.operation == Operation.PUT else sum - c.sum
                    if new_sum >= 0:
                        curs.execute("""
                        UPDATE accounts SET sum = %s WHERE client_id = %s
                        """, (new_sum, c.client_id))

                        curs.execute("""
                        UPDATE history SET status=%s
                        WHERE transaction_id=%s
                        """, ('done', str(c.transaction_id)))
                    else:
                        curs.execute("""
                        UPDATE history SET status=%s
                        WHERE transaction_id=%s
                        """, ('cancelled', str(c.transaction_id)))

def load_pending_operations():
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as curs:
            curs.execute("""
            SELECT transaction_id, client_id, sum, operation FROM history
            WHERE status = 'pending'
            ORDER BY n
            """)
            for record in curs:
                (transaction_id, client_id, sum, operation) = record
                add_operation_to_Q(transaction_id,
                                   client_id,
                                   sum,
                                   Operation.PUT if operation == 'Operation.PUT' else Operation.WITHDRAW)

if settings.MIGRATE:
    migrate.migration_1()

load_pending_operations()
threading.Thread(target=main_loop,
                 daemon=True).start()

#if settings.TEST:
#    my_test.test()