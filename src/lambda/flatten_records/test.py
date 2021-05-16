import unittest
import json

import lambda_function



class TestFlanttenRecords(unittest.TestCase):
    def test_problems(self):
        with open('sample.json') as f:
            sample = json.load(f)
        response = lambda_function.lambda_handler([sample],{})
        assert sample == response
        

if __name__ == '__main__':
    unittest.main()
