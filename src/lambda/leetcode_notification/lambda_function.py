import json
import os

import boto3

import utils
import db
from leetcode import LeetCode

CATEGORY_SLUG = 'algorithms'
SSM_PARAMETER = '/cs498/time/secret'
IOT_TOPIC = 'cs498/time/leetcode'

client = boto3.client('iot-data')
COOKIE = utils.get_secrets(SSM_PARAMETER)


def handle_ack(event, leetcode_client, today, hours=1):
    """Handle acknolwegement from device."""
    if not event.get('ack') or event.get('slug')=='Loading...':
        return

    slug = event['slug']
    id_ = event['id']
    prob_sub = leetcode_client.get_problem_submission(slug)
    print('ack prob', prob_sub)
    status = leetcode_client.get_last_status(prob_sub)
    if status == 'ac':
        ts = leetcode_client.get_last_ts(prob_sub)
        print('ts', ts, type(ts))
        if utils.is_within_hours(ts, hours=hours):
            db.store_problems(today, slug, id_, status)
        else:
            print(slug, 'not within hour.')


def filter_today_probs(done, today_probs):
    """Filter today's problems from done."""
    today_prob_id = set(x[0] for x in today_probs)
    done = list(filter(lambda x: x[0] not in today_prob_id,
                       done))
    return done


def lambda_handler(event, context):
    print('event received', event)
    # handle confirmation
    today = utils.get_today()
    leetcode_client = LeetCode('', COOKIE)
    handle_ack(event, leetcode_client, today)

    user, done, remaining = leetcode_client.get_problems(
        category_slug=CATEGORY_SLUG)

    # filter today's problems from done
    today_probs = db.get_problems(today)
    done = filter_today_probs(done, today_probs)

    new, old = leetcode_client.get_next_problems(done, remaining)
    user['problems'] = [{new[0]:new[1]}, {old[0]:old[1]}]
    # print(user)

    user['todayCount'] = len(today_probs)
    payload = json.dumps(user)
    print(payload)
    client.publish(topic=IOT_TOPIC, payload=payload)
