import os
from functools import lru_cache
from datetime import datetime, timedelta, timezone
import pytz

import boto3
import constants

client = boto3.client('ssm')


@lru_cache
def get_secrets(parameter_name):
    print('retrieving secret')
    response = client.get_parameter(
        Name=parameter_name,
        WithDecryption=True)
    return response['Parameter']['Value']


def get_today():
    est = pytz.timezone(constants.USER_TZ)
    utc_ts = datetime.utcnow()
    current_datetime = est.fromutc(utc_ts)
    today = current_datetime.date().isoformat()
    print(current_datetime, utc_ts, today)
    return today


def is_within_hours(epoch, hours=1):
    hour_before = datetime.utcnow() - timedelta(hours=hours)
    hour_before_epoch = int(hour_before.replace(
        tzinfo=timezone.utc).timestamp())
    print('hour before epoch', hour_before_epoch)
    return epoch > hour_before_epoch
