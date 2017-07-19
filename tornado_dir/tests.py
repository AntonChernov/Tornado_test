from tornado.testing import AsyncTestCase


class TestAPI(AsyncTestCase):

    def get_all_rooms(self):
        response = self.fetch('/get_busy_rooms/')
        self.assertEqual(response.code, 200)
