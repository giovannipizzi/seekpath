import json
import os
import unittest
import tempfile
import seekpath
from seekpath.hpkot import SymmetryDetectionError

import seekpath_app
import structure_importers

this_folder = os.path.dirname(os.path.realpath(__file__))


class TestConverters(unittest.TestCase):

    def test_correct_file_examples(self):
        """Check if these valid structures are properly parsed"""
        with open(os.path.join(this_folder, 'file_examples', 'list.json')) as f:
            list_files = json.load(f)

        for the_format, examples in list_files.items():
            for example in examples:
                filename = example['file']
                extra_data = example.get('extra_data', None)
                with open(os.path.join(this_folder, 'file_examples',
                                       filename)) as f:
                    structure = structure_importers.get_structure_tuple(
                        f, the_format, extra_data=extra_data)
                seekpath_results = seekpath.get_path(structure)
                # No additional check, just check if it works

    def test_wrong_file_examples(self):
        """Check if these valid structures are properly parsed"""
        with open(
                os.path.join(this_folder, 'file_examples_wrong',
                             'list.json')) as f:
            list_files = json.load(f)

        for the_format, examples in list_files.items():
            for example in examples:
                filename = example['file']
                extra_data = example.get('extra_data', None)
                with open(
                        os.path.join(this_folder, 'file_examples_wrong',
                                     filename)) as f:
                    # The error I get is generic, so for now I just check if it crashes
                    with self.assertRaises(Exception):
                        structure = structure_importers.get_structure_tuple(
                            f, the_format, extra_data=extra_data)
                # No additional check, just check if it works

    def test_failing_file_examples(self):
        """These should be files that are valid in format but invalid when looking for symmetry"""
        with open(
                os.path.join(this_folder, 'file_examples_failing',
                             'list.json')) as f:
            list_files = json.load(f)

        for the_format, examples in list_files.items():
            for example in examples:
                filename = example['file']
                extra_data = example.get('extra_data', None)
                with open(
                        os.path.join(this_folder, 'file_examples_failing',
                                     filename)) as f:
                    structure = structure_importers.get_structure_tuple(
                        f, the_format, extra_data=extra_data)
                # No additional check, just check if it works
                with self.assertRaises(SymmetryDetectionError):
                    seekpath_results = seekpath.get_path(structure)


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
