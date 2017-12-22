import os
import seekpath_app
import unittest
import tempfile


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        #self.db_fd, seekpath_app.app.config['DATABASE'] = tempfile.mkstemp()
        seekpath_app.app.config['TESTING'] = True
        self.app = seekpath_app.app.test_client()
        #with seekpath_app.app.app_context():
        #    seekpath_app.init_db()

    def tearDown(self):
        #os.close(self.db_fd)
        #os.unlink(seekpath_app.app.config['DATABASE'])
        pass


class TestBasic(FlaskTestCase):
    """
    I at least check that I can get the basic content without error
    """

    def test_input_structure(self):
        rv = self.app.get('/input_structure/')
        self.assertEqual(rv.status_code, 200)

    def test_get_static_css(self):
        rv = self.app.get('/static/css/visualizer.min.css')
        self.assertEqual(rv.status_code, 200)

    def test_example_cP1_inv(self):
        rv = self.app.post(
            '/process_example_structure/',
            data={'value': 'cP1_inv'},
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        #html_data = rv.get_data()


if __name__ == '__main__':
    unittest.main()
