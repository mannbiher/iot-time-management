import logging
import sys

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# code sample provided on AWS forum 
# https://forums.aws.amazon.com/thread.jspa?threadID=288424
def lambda_handler(event, context):
    logger.info("events received: {}".format(len(event)))
    result = []
    for message in event:
        if isinstance(message, list):
            for record in message:
                result.append(record)
        else:
            result.append(message)

    return result

    