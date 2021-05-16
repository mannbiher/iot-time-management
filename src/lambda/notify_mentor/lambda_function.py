import json
from constants import BLACKLISTED, USAGE_LIMIT

import boto3

DOMAIN_USAGE = {}
SNS_TOPIC = 'arn:aws:sns:us-east-2:057733667042:cs498_iot_time_notification'

sns_client = boto3.client('sns')


def lambda_handler(event, context):
    # print('event received', event)
    for item in event:
        domain = item['domain']
        size = item['size']
        if domain in BLACKLISTED:
            # store usage in a global dict. This global dict is not gauranteed to
            # be maintained before different invocations
            DOMAIN_USAGE[domain] = DOMAIN_USAGE.get(domain, 0) + size

    # do not send notification for each usage overuse
    domains_by_usage = [(v, k)
                        for k, v in DOMAIN_USAGE.items()
                        if v >= USAGE_LIMIT]

    if not domains_by_usage:
        return

    # return only top-5 websites
    messages = ['Social media usage exceeded.']
    top_five = sorted(domains_by_usage, reverse=True)[:5]
    for usage, domain in top_five:
        usage = usage/1000
        messages.append(f'{domain} used for {usage} KB.')
    message = ' '.join(messages)
    print(message)
    sns_client.publish(TopicArn=SNS_TOPIC,
                       Message=message,
                       Subject='Usage exceeded')
    
    for _, domain in top_five:
        # remove from global dict to avoid repeated messages
        DOMAIN_USAGE.pop(domain)

