import unittest
from namesc import names
import pandas as pd


class TestNamesC(unittest.TestCase):
    def test_valid_names(self):
        self.assertEqual(names('tikhon', 'Ivan')[0], 'M', "Should be 'M'")

    def test_numbers(self):
        self.assertListEqual(names(123, 321), [None], "Should be None")

    def test_numbers_strings(self):
        self.assertListEqual(names("123", "321"), [None], "Should be None")

    def test_valid_names_with_SS(self):
        self.assertEqual(names("__tikhon__", " Ivan")[0], 'M', "Should be 'M'") 
        
    def test_check_with_data(self):
        d = pd.read_csv("test.csv")
        prev = ""
        for i, row in d.iterrows():
            if prev == "":
                prev = row['usernames']
            else:
                self.assertIsInstance(names(row["usernames"], prev), list, "Should be list")
                prev = ""



if __name__ == '__main__':
    unittest.main()
