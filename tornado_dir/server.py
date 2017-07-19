from datetime import date
import tornado.escape
import tornado.ioloop
import tornado.web
import sqlite3
import logging

logging.basicConfig(filename='loger.log', level=logging.DEBUG)
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')



con = sqlite3.connect('test.db')

curs = con.cursor()

try:
    curs.execute('''CREATE TABLE rooms (
                id INTEGER PRIMARY KEY NOT NULL ,
                room_number VARCHAR (4),
                customer VARCHAR (20),
                free INTEGER NOT NULL)''')
except sqlite3.OperationalError:
    print('Error was detected!!')


class GetRooms(tornado.web.RequestHandler):

    def get(self):
        con = sqlite3.connect('test.db')
        curs = con.cursor()
        c = curs.execute('''SELECT * FROM rooms WHERE free = 0 ''')
        qs = c.fetchall()
        data = []
        if len(qs) > 0:
            [data.append({'id': row[0], 'number': row[1], 'customer': row[2]}) for row in qs]
            self.write({'data': data})
            con.close()
            logging.info('GetRooms OK')
        else:
            con.close()
            logging.error('GetRooms get an error data={0}'.format(data))
            self.write({'error': 'empty queryset!'})


class GetRoomCustomers(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        con = sqlite3.connect('test.db')
        curs = con.cursor()
        c = curs.execute('''SELECT * FROM rooms WHERE room_number = ? ''', (args[0],))
        qs = c.fetchall()
        data = []
        if len(qs) > 0:
            [data.append({'id': row[0], 'number': row[1], 'customer': row[2]}) for row in qs]
            self.write({'data': data})
            con.close()
            logging.info('GetRoomCustomers OK')
        else:
            con.close()
            logging.error('GetRoomCustomers error data ={0} args={1}'.format(data, args))
            self.write({'error': 'empty queryset!'})


class DeleteRoom(tornado.web.RequestHandler):

    def delete(self, *args, **kwargs):
        con = sqlite3.connect('test.db')
        curs = con.cursor()
        try:
            room = self.get_argument('room_number')
            c = curs.execute('''DELETE FROM rooms WHERE room_number = ? ''', (room,))
            con.commit()
            con.close()
            logging.info('DeleteRoom OK')
            self.write({'success': 'delete room successfully'})
        except sqlite3.OperationalError:
            con.close()
            logging.error('DeleteRoom error room = {0}'.format(room))
            self.write({'error': 'Delete error!'})


class AddRoom(tornado.web.RequestHandler):

    def post(self):
        con = sqlite3.connect('test.db')
        curs = con.cursor()
        try:
            cast_decode = self.get_argument('customer').encode('utf8')
            con.text_factory = str
            cast = cast_decode
            room = str(self.get_argument('room_number'))
            c = curs.execute('''INSERT INTO rooms ( room_number, customer, free)VALUES (?, ?, ? )''', (room, cast, 0))
            con.commit()
            con.close()
            logging.info('AddRoom OK')
            self.write({'success': 'Room {0} wqs successfully created customer is {1}'.format(
                self.get_argument('room_number'),
                cast_decode,)}
            )
        except sqlite3.OperationalError:
            cast_decode = self.get_argument('customer').encode('utf8')
            room = str(self.get_argument('room_number'))
            logging.error('AddRoom error customers={0} room={1}'.format(room, cast_decode))
            self.write({'error': 'error was detected'})


class ChangeRoom(tornado.web.RequestHandler):

    def put(self, *args, **kwargs):
        con = sqlite3.connect('test.db')
        curs = con.cursor()
        try:
            room = self.get_argument('ex_room_number')
            change_room = self.get_argument('ch_room_number')
            c = curs.execute('''UPDATE rooms SET room_number = ? WHERE room_number = ?''', (change_room, room,))
            con.commit()
            con.close()
            logging.info('ChangeRoom OK')
            self.write({'success': 'Room {0} was successfully updated room number is {1}'.format(
                room,
                change_room, )}
            )
        except sqlite3.OperationalError:
            room = self.get_argument('ex_room_number')
            change_room = self.get_argument('ch_room_number')
            logging.error('ChangeRoom room={0} change_room={1}'.format(room, change_room))
            self.write({'error': 'error was detected'})


application = tornado.web.Application([
    (r"/get_busy_rooms/", GetRooms),
    (r"/delete_room/", DeleteRoom),
    (r"/add_room/", AddRoom),
    (r"/change_room_num/", ChangeRoom),
    (r"/get_room_customers/([0-9]+)/", GetRoomCustomers),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
