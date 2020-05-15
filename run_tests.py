"""Run the code tests."""
import unittest

# Import all tests here
from seekpath.test_paths_hpkot import *  # pylint: disable=unused-wildcard-import,unused-import
from seekpath.hpkot.test_get_primitive import *  # pylint: disable=unused-wildcard-import,unused-import
from seekpath.brillouinzone.test_brillouinzone import *  # pylint: disable=unused-wildcard-import,unused-import

if __name__ == "__main__":
    unittest.main()
