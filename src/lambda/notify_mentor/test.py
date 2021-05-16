import os
import unittest
import json

import lambda_function


class TestNotification(unittest.TestCase):

    def test_notification(self):
        event = [{'domain': 'fb', 'size': 2000},
                 {'domain': '9gag', 'size': 40000}]
        lambda_function.lambda_handler(event, {})


if __name__ == '__main__':
    unittest.main()
