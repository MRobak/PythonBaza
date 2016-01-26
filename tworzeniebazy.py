# -*- coding: utf-8 -*-

import sqlite3


db_path = 'orders.db'
conn = sqlite3.connect(db_path)

c = conn.cursor()

c.execute('''
            DROP TABLE Position
            ''')
    
c.execute('''
            DROP TABLE Orders
            ''')


c.execute('''
            CREATE TABLE Orders
            ( id INTEGER PRIMARY KEY,
            order_date DATE NOT NULL,
            qty NUMERIC NOT NULL,
            qtyc NUMERIC NOT NULL
            )
            ''')

c.execute('''
            CREATE TABLE Position
            ( name VARCHAR(5),
            subclass VARCHAR(50),
            qty INTEGER NOT NULL,
            costprice NUMERIC NOT NULL,
            position_id INTEGER,
            FOREIGN KEY(position_id) REFERENCES Orders(id),
            PRIMARY KEY (name, position_id))
            ''')
