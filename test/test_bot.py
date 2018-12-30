import unittest
from mock import MagicMock
from pprint import pprint
# from collections import OrderedDict

class TestMatching(unittest.TestCase):

    def setUp(self):
        """
        Tests setup
        """
        pass

    def test_basic_csv_translation(self):
        """
        Basic check
        """
        raw_data = """\
start,end,case_id,activity
1,2,case_1,start
2,3,case_1,in progress
3,5,case_1,in progress again
6,12,case1,done
2,4,case_2,start
5,20,case_2,canceled
"""
        # print(data)
        expected = """some xml stuff"""



if __name__ == '__main__':
    unittest.main()
