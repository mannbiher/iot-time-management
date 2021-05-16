import json
import requests
from random import choice, random, sample
from string import Template

from requests.models import Response

import constants


class LeetCode:
    def __init__(self, username, cookie):
        self.username = username
        self.cookie = cookie.encode('utf-8')
        self.session = requests.session()

    def get_headers(self, referer, is_graphql=False):
        headers = {
            'Referer': referer,
            'Origin': constants.BASE_URL,
            'Cookie': self.cookie,
            'Host': constants.HOST,
            'User-Agent': constants.USER_AGENT
        }
        if is_graphql:
            csrf_token = self.get_cookie_value('csrftoken')
            headers['x-csrftoken'] = csrf_token
        return headers

    def get_cookie_value(self, key):
        for parts in self.cookie.decode('utf-8').split(';'):
            k, v = parts.split('=', 1)
            if k.strip() == key:
                return v.strip().encode('utf-8')
        return None

    def login(self):
        """It is not used, however keeping it for future enhancement."""
        print('sign in to leetcode')
        if not self.session:
            self.session = requests.session()

        response = self.session.get(constants.LOGIN_URL)
        response.raise_for_status()
        csrf_token = response.cookies['csrftoken']
        headers = {
            'Origin': constants.BASE_URL,
            'Referer': constants.LOGIN_URL,
        }
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'login': self.username,
            'password': self.password
        }
        response = self.session.post(constants.LOGIN_URL,
                                     headers=headers, data=form_data)
        print(response.request)
        print(response.text)
        response.raise_for_status()

    def get_problem_submission(self, slug):
        referer = Template(constants.PROBLEM_URL).substitute(slug=slug)
        headers = self.get_headers(referer, is_graphql=True)
        variables = {'lastKey': None, 'limit': 20, 'offset': 0,
                     'questionSlug': slug}

        operation = 'Submissions'
        payload = {
            'operationName': operation,
            'query': constants.GRAPH_QL[operation],
            'variables': variables
        }
        response = self.session.post(constants.GRAPHQL_URL, headers=headers,
                                     json=payload)
        response.raise_for_status()
        return response.json()

    def get_last_status(self, prob_sub):
        """Get laststatus from problem submission.

        Possible status None, 'notac', 'ac'
        """
        status = None
        try:
            status = (prob_sub['data']
                      ['submissionList']
                      ['submissions'][0]['statusDisplay'])
        except (KeyError, IndexError):
            pass
        if status:
            if status == 'Accepted':
                status = 'ac'
            else:
                status = 'notac'
        return status

    def get_last_ts(self, prob_sub):
        """Get lasttimestamp from problem submission."""
        return int(prob_sub['data']
                   ['submissionList']
                   ['submissions'][0]['timestamp'])

    def get_next_problems(self, done, remaining):
        """Give two questions from set.

        One randomly selected from not done set.
        Other the oldest submission from five randomly selected
        completed problems.
        """
        new_prob = choice(remaining)
        old_probs = sample(done, 5)
        old_probs_ts = []
        for slug, id_ in old_probs:
            prob_sub = self.get_problem_submission(slug)
            # print('prob_sub', prob_sub)
            ts = self.get_last_ts(prob_sub)
            old_probs_ts.append((ts, slug, id_))

        # print(old_probs_ts)
        old_prob = tuple(sorted(old_probs_ts, reverse=True)[0][1:])
        return new_prob, old_prob

    def get_problems(self, category_slug='all'):
        """Get metadata for all leetcode problems.

        Category slugs: all, algorithms, database, shell, concurrency
        """
        headers = self.get_headers(constants.PROBLEM_SET_URL)

        url = Template(constants.ALL_URL).substitute(
            category_slug=category_slug)
        response = self.session.get(url, headers=headers)
        # print(response.request.headers)
        response.raise_for_status()
        payload = response.json()
        new_questions = []
        old_questions = []
        for item in payload['stat_status_pairs']:
            comb_id = (item['stat']['question__title_slug'],
                       item['stat']['question_id'])
            if item['status'] is not None:
                old_questions.append(comb_id)
            else:
                new_questions.append(comb_id)

        payload.pop('stat_status_pairs')
        return payload, old_questions, new_questions
