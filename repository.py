# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime
import numpy

db_path = 'orders.db'

class RepositoryException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors


class Orders():
    """Model pojedynczego zamówienia"""
    def __init__(self, id, date= datetime.now(), positions=[]):
        self.id = id
        self.date = date
        self.positions = positions
        self.qty = sum([item.qty for item in self.positions])
        self.qtyc = sum([item.qty*item.costprice for item in self.positions])

    def __repr__(self):
        return "<Orders(id='%s', date='%s', qty='%s', qtyc='%s', items='%s')>" % (
                    self.id, self.date, str(self.qty), str(self.qtyc), str(self.positions)
                )


class Position():

    def __init__(self, name, subclass, qty, costprice):
        self.name = name
        self.subclass = subclass
        self.qty = qty
        self.costprice = costprice

    def __repr__(self):
        return "<Position(name='%s', subclass='%s', qty='%s', costprice='%s')>" % (
                    self.name, self.subclass, str(self.qty), str(self.costprice)
                )



class Repository():
    def __init__(self):
        try:
            self.conn = self.get_connection()
        except Exception as e:
            raise RepositoryException('GET CONNECTION:', *e.args)
        self._complete = False

    # wejście do with ... as ...
    def __enter__(self):
        return self

    # wyjście z with ... as ...
    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def get_connection(self):
        return sqlite3.connect(db_path)

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise RepositoryException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise RepositoryException(*e.args)


class OrdersRepository(Repository):

    def add(self, orders):
        """Metoda dodaje pojedyncze zamówienie do bazy danych,
        wraz ze wszystkimi jej pozycjami."""
        try:
            c = self.conn.cursor()
            # zapisz nagłowek zamówienia
            self.qty = sum([item.qty for item in orders.positions])
            self.qtyc = sum([item.qty*item.costprice for item in orders.positions])            
            c.execute('INSERT INTO Orders (id, order_date, qty, qtyc) VALUES(?, ?, ?, ?)',
                        (orders.id, str(orders.date), self.qty, self.qtyc)
                    )
            # zapisz pozycje zamówienia
            if orders.positions:
                for position in orders.positions:
                    try:
                        c.execute('INSERT INTO Position (name, subclass, qty, costprice, position_id) VALUES(?, ?, ?, ?, ?)',
                                        (position.name, position.subclass, position.qty, position.costprice, orders.id)
                                )
                    except Exception as e:
                        #print "position add error:", e
                        raise RepositoryException('error adding orders item: %s, to orders: %s' %
                                                    (str(position), str(orders.id))
                                                )
        except Exception as e:
            #print "orders add error:", e
            raise RepositoryException('error adding orders %s' % str(orders))

    def delete(self, orders):
        """Metoda usuwa pojedyncze zamówienie z bazy danych,
        wraz ze wszystkimi jej pozycjami."""
        try:
            c = self.conn.cursor()
            # usuń pozycje
            c.execute('DELETE FROM Position WHERE position_id=?', (orders.id,))
            # usuń nagłowek
            c.execute('DELETE FROM Orders WHERE id=?', (orders.id,))

        except Exception as e:
            #print "orders delete error:", e
            raise RepositoryException('error deleting orders %s' % str(orders))

    def getById(self, id):
        """Get orders by id"""
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM Orders WHERE id=?", (id,))
            or_row = c.fetchone()
            orders = Orders(id=id)
            if or_row == None:
                orders=None
            else:
                orders.date = or_row[1]
                orders.qty = or_row[2]
                orders.qtyc = or_row[3]
                c.execute("SELECT * FROM Position WHERE position_id=? order by name", (id,))
                or_items_rows = c.fetchall()
                items_list = []
                for item_row in or_items_rows:
                    item = Position(name=item_row[0], subclass=item_row[1], qty=item_row[2], costprice=item_row[3])
                    items_list.append(item)
                orders.positions=items_list
        except Exception as e:
            #print "orders getById error:", e
            raise RepositoryException('error getting by id orders_id: %s' % str(id))
        return orders

    def update(self, orders):
        """Metoda uaktualnia pojedyncze zamówienie w bazie danych,
        wraz ze wszystkimi jej pozycjami."""
        try:
            # pobierz z bazy zamówienie
            or_oryg = self.getById(orders.id)
            if or_oryg != None:
                # zamówienie jest w bazie: usuń je
                self.delete(orders)
            self.add(orders)
        except Exception as e:
            #print "orders update error:", e
            raise RepositoryException('error updating orders %s' % str(orders))

class PositionRepository(Repository):

    def meanqty(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT qty FROM Position")
            qty_row = c.fetchall()
            qty_list = []
            for row in qty_row:
                    qty_list.append(row[0]),

            if len(qty_list)==0:
                return None
            else:
                return numpy.mean(qty_list)

        except Exception as e:
            raise RepositoryException('error counting average qty of position %s' % e.args)

    def minmeanmax(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT costprice FROM Position")
            costprice_row = c.fetchall()
            costprice_list = []
            for row in costprice_row:
                    costprice_list.append(row[0]),

            if len(costprice_list)==0:
                return None
            else:
                return round(min(costprice_list),2), round(numpy.mean(costprice_list),2), round(max(costprice_list),2)

        except Exception as e:
            raise RepositoryException('error counting average qty of position %s' % e.args)

        
if __name__ == '__main__':

    try:
        with OrdersRepository() as orders_repository:
            orders_repository.update(
                Orders(id = 1, date= '2016-01-19',
                        positions = [
                            Position(name = "KX977", subclass = "t-shirts_s_s", qty = 1000, costprice = 5.50),
                            Position(name = "KY878", subclass = "t-shirts_l_s", qty = 1000, costprice = 10.20),
                        ]
                    )
                )
            orders_repository.complete()
    except RepositoryException as e:
        print(e)

    print OrdersRepository().getById(1)

    try:
        with OrdersRepository() as orders_repository:
            orders_repository.add(
                Orders(id = 2, date = '2016-01-18',
                        positions = [
                            Position(name = "ZA965", subclass = "jackets", qty = 300, costprice = 102.50),
                            Position(name = "KS878", subclass = "trousers", qty = 400, costprice = 63.60),
                        ]
                    )
                )
            orders_repository.complete()
    except RepositoryException as e:
        print(e)

    print OrdersRepository().getById(2)
    
    try:
        with OrdersRepository() as orders_repository:
            orders_repository.add(
                Orders(id = 3, date = '2016-01-18',
                        positions = [
                            Position(name = "ZA965", subclass = "coats", qty = 500, costprice = 150.50),
                            Position(name = "KS878", subclass = "outer_jackets", qty = 500, costprice = 140.60),
                        ]
                    )
                )
            orders_repository.complete()
    except RepositoryException as e:
        print(e)    


    print OrdersRepository().getById(3)
    
    try:
        with OrdersRepository() as orders_repository:
            orders_repository.update(
                Orders(id = 1, date= '2016-01-19',
                        positions = [
                            Position(name = "KX977", subclass = "t-shirts_s_s", qty = 1500, costprice = 5.50),
                            Position(name = "KY878", subclass = "t-shirts_l_s", qty = 1500, costprice = 10.20),
                        ]
                    )
                )
            orders_repository.complete()
    except RepositoryException as e:
        print(e)

    print OrdersRepository().getById(1)

    try:
        with OrdersRepository() as invoice_repository:
            invoice_repository.delete( Orders(id = 3) )
            invoice_repository.complete()
    except RepositoryException as e:
        print(e)

    try:
        print("Average qty of position: %0.0f" % PositionRepository().meanqty())

    except RepositoryException as e:
        print(e)

    try:
        print("MAX, MEAN, MIN costprice of position:")
        print(PositionRepository().minmeanmax())

    except RepositoryException as e:
                print(e)
