# -*- coding: utf-8 -*-

import repository
import sqlite3
import unittest

db_path = 'orders.db'

class RepositoryTest(unittest.TestCase):

    def setUp(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM Position')
        c.execute('DELETE FROM Orders')
        c.execute('''INSERT INTO Orders (id, order_date, qty, qtyc) VALUES(1, '2016-01-18', 3000, 30000)''')
        c.execute('''INSERT INTO Position (name, subclass, qty, costprice, position_id) VALUES('KX888','t-shirts_l_s',1500,10,1)''')
        c.execute('''INSERT INTO Position (name, subclass, qty, costprice, position_id) VALUES('KZ999','shorts',1500,10,1)''')
        c.execute('''INSERT INTO Orders (id, order_date, qty, qtyc) VALUES(2, '2016-01-18', 2000, 10000)''')
        c.execute('''INSERT INTO Position (name, subclass, qty, costprice, position_id) VALUES('KY985','t-shirts_s_s',1000,5,2)''')
        c.execute('''INSERT INTO Position (name, subclass, qty, costprice, position_id) VALUES('KY988','t-shirts_s_s',1000,5,2)''')
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM Position')
        c.execute('DELETE FROM Orders')
        conn.commit()
        conn.close()

    def testGetByIsInstance(self):
        orders = repository.OrdersRepository().getById(1)
        self.assertIsInstance(orders, repository.Orders, "Objekt nie jest klasy Orders")

    def testGetByIdNotFound(self):
        self.assertEqual(repository.OrdersRepository().getById(3), None,
                         "Powinno wyjsc None")

    def testGetByIdInvitemsLen(self):
        self.assertEqual(len(repository.OrdersRepository().getById(1).positions), 2,
                         "Powinno wyjsc 2")

    def testMeanqty(self):
        self.assertEqual(repository.PositionRepository().meanqty(), 1250,
                         "Powinno wyjsc 1250, a wyszlo " + str(repository.PositionRepository().meanqty()))

    def testMinmeanmaxqty(self):
        self.assertEqual(repository.PositionRepository().minmeanmax(), (5,7.5,10),
                         "Powinno wyjsc (5,7.5,10), a wyszlo " + str(repository.PositionRepository().minmeanmax()))



if __name__ == "__main__":
    unittest.main()
