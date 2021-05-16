import os
import unittest
import json
from datetime import datetime, timedelta

from leetcode import LeetCode
import utils
import db
import lambda_function


class TestLeetCode(unittest.TestCase):
    # def test_login(self):
    #     leetcode_client = LeetCode(USERNAME, COOKIE)
    #     # leetcode_client.parse_cookie()
    #     leetcode_client.get_problems()
    #     # print(leetcode_client.session.cookies)

    # def test_problems(self):
    #     secret = '/cs498/time/secret'
    #     cookie = utils.get_secrets(secret)
    #     leetcode_client = LeetCode('', cookie)
    #     user, done, remaining = leetcode_client.get_problems(
    #         category_slug='algorithms')
    #     new, old = leetcode_client.get_next_problems(done, remaining)
    #     print(user, new, old)
    #     user['problems'] = [{new[0]:new[1]}, {old[0]:old[1]}]
    #     print(json.dumps(user))

    # def test_parameter_store(self):
    #     secret = '/cs498/time/secret'
    #     utils.get_secrets(secret)
    #     utils.get_secrets(secret)
    #     utils.get_secrets(secret)
    #     utils.get_secrets(secret)
    #     val = utils.get_secrets(secret)

    # def test_db(self):
    #     today = '2020-05-05'
    #     problems = db.get_problems(today)
    #     print(problems)
    #     db.store_problems(today, 'two-sum', 72, 'ac')

    # def test_timezone_conversion(self):
    #     utils.get_today()

    # def test_within_hour(self):
    #     curr_ts = (datetime.utcnow() - timedelta(minutes=30)).timestamp()
    #     assert utils.is_within_hours(curr_ts)
    #     curr_ts = (datetime.utcnow() - timedelta(hours=2)).timestamp()
    #     assert not utils.is_within_hours(curr_ts)

    # def test_ack(self):
    #     secret = '/cs498/time/secret'
    #     cookie = utils.get_secrets(secret)
    #     leetcode_client = LeetCode('', cookie)
    #     event = {'ack': True, 'slug': 'deepest-leaves-sum', 'id': '1254'}
    #     lambda_function.handle_ack(event, leetcode_client)

    def test_entrypoint(self):
        # event = {'ack': True, 'slug': 'subdomain-visit-count', 'id': '829'}
        event = {'ack': True, 'slug': 'Loading...', 'id': 'Loading...'}
        lambda_function.lambda_handler(event, {})

    # def test_count(self):
    #     lambda_function.get_today_count()

    # def test_prob_filter(self):
    #     today_probs = db.get_problems(utils.get_today())
    #     done = [("find-bottom-left-tree-value", 513),
    #             ("binary-tree-maximum-path-sum", 124),
    #             ("two-sum", 72)]
    #     new_done = lambda_function.filter_today_probs(done, today_probs)
    #     assert new_done == done[:2]
    #     print(new_done, today_probs)


if __name__ == '__main__':
    # USERNAME = os.environ['USERNAME']
    # PASSWORD = os.environ['PASSWORD']
    # COOKIE = os.environ['COOKIE']

    unittest.main()
