# Procastination Tracker and Goal Reminder
*Maneesh Kumar Singh (mksingh4@illinois.edu)*

This is source code repository for my final project for UIUC graduate course
CS498 Internet of Things. As part of this project, I built a time management
system which consists of two parts: A social media usage tracker with deterrent
and a live display of current tasks or goals in hand using Raspberry Pi. We are
using AWS to host our IoT infrastructure.

## Project Resources

- [Project Report](doc/CS%20498%20IoT%20Final%20Project%20Report.pdf)
- [Video URL](https://uofi.box.com/s/hw6nnz6az4d38klui68at7gntorrwbnf). Video
  URL is only accessible using UIUC net id.

## Code structure

### tcpdump

#### `tcpdump.sh`

A bash script to run tcpdump with correct parameters to capture network traffic
on wlan0 interface and write them to /var/tmp/pcap location.

#### `mqtt_client.py`

An AWS IoT client written using AWS IoT Python SDK. It has methods implemented
for connect, disconnect, publish and subscribe.

#### `mqtt_publish.py`

This python module parses the `pcap` files created by `tcpdump` utility. It
build a reverse DNS lookup dictionary using DNS records and uses them for
reverse DNS lookup on subsequent network records. It summarizes and sends
message to IoT topic in batches of 500 messages in a JSON array. Reverse DNS
dictionary function is written by Je-Clark at his [GitHub
Repository](https://github.com/je-clark/ScapyDNSDissection).

## lambda

This folder contains the source code for three lambda functions used in this
project.

### flatten_records

This lambda function is used by AWS IoT Analytics pipeline to flatten the JSON
array send by `mqtt_publish.py`. It is based on code provided in [AWS support
forum](https://forums.aws.amazon.com/thread.jspa?threadID=288424).

### leetcode_notification

This lambda function pulls the information from LeetCode and decides the next
problem to publish to IoT topic. It requires access to LeetCode session cookie
which can be stored in parameter store and retrieved by lambda.

### notify_mentor

This lambda function maintains a global dictionary to track network data usage.
It maintains a blacklisted website list and threshold. Once a blacklisted domain
crosses the threshold it publishes a message to AWS SNS which in turns sends SMS
to people subscribed for SMS delivery mode.

## electron-app

This folder contains source code for Electron application used to display
LeetCode status and allows user to request refresh by click.

## How to run

We have developed and tested the code on Ubuntu and Raspberry Pi. Therefore we
would provide instructions for Ubuntu and Pi only.

### Setup

Please setup and activate `virualenv` for python >= 3.7.3. Clone the repository
and then from src folder use pip to install all the necessary packages.

```bash
cd src
pip install -r requirements.txt
```

### AWS IAM setup

Create new IAM roles or modify existing one to provide

- AWS Lambda role needs access to `iot:Publish`, `sns:Publish` and
  `ssm:GetParameter`
- AWS EC2 role for access to IoT Analytics dataset through IoT notebook. I used
  create new role option during creation of notebook instance.

### AWS SSM setup (Optional)

Login to LeetCode using Google Chrome. Copy `crsftoken` cookie value from
Developer tools and store it in AWS SSM parameter store as a secret value. Note
down parameter path.

### AWS SNS setup

Create an AWS SNS topic and note down the ARN. Also subscribe to topic using SMS
delivery mode.

### AWS Lambda function

If you have setup AWS SSM to store LeetCode cookie value, change the SSM path in
leetcode_notification lambda_function.py module. leetcode_notification lambda
requires extra libraries not available in AWS Lambda environment.

- Install dependencies in the leetcode_notification directory.
- zip the package

```bash
# From src/lambda/leetcode_notification
pip install -r requirements.txt -t .
zip -r leetcodenotification.zip
```

Modify notify_mentor lambda code with new SNS ARN generated in previous step.
Other two lambda function do not require any external dependencies so you can
zip them without install step.

```bash
# From src/lambda/
cd flatten_records
zip -r flatten_records.zip .
cd ../notify_mentor
zip -r notify_mentor.zip .
```

Create corresponding empty lambda functions with Python 3.7 runtime and upload
the zip files. In AWS Lambda role, provide access to iot:Publish, sns:Publish
and ssm:GetParameter. Change the Memory to 256 MB and runtime to 1 minute for
all functions using configuration tab in AWS Lambda console.

### AWS IoT Analytics setup

1. Please create an IoT analytics channel, data source, pipeline and query
   dataset. While creating pipeline, add AWS Lambda activity and configure
   FlattenRecords lambda created above.

2. Create an IoT Analytics notebook. It would requires an notebook instance to
   spin-up. You can create new role to provide access to notebook instance or
   you can use existing role if setup with right permissions.

### AWS IoT setup

1. Please create a device in AWS IoT Core and download the certificates and keys
   to folder src/tcpdump/certificates. Find AWS IoT endpoint in Settings Page of
   AWS IoT Core console. Change the corresponding values in `mqtt_publish.py`

    ```python
        client = MQTTClient(
            'xxxxxxxxxxxx-ats.iot.us-east-2.amazonaws.com',
            'certificates/d6ccf7c6bd-certificate.pem.crt',
            'certificates/d6ccf7c6bd-private.pem.key',
            'certificates/AmazonRootCA1.pem')
        client.connect()
    ```

2. Create an IoT rule to trigger AWS IoT analytics channel and AWS Lambda
   `NotifyMentor` for topic `cs498/time/usage`.

3. Create an IoT rule to trigger AWS Lambda `LeetCodeNotification` for topic
   `cs498/time/new`.

### Network capture

Network capture part can be tested on Ubuntu or Pi without setting up Pi as
network router. In this mode, it will capture the instance data flowing through
wlan0 interface.

In order to deploy this system, you need to setup Raspberry Pi as an access
point and network router. Please follow [project
report](doc/CS%20498%20IoT%20Final%20Project%20Report.pdf) for complete
instructions.

Run the `tcpdump.sh` script provided at src/tcpdump/tcpdump.sh. Please change
the interface name or output location if different than as specified in the
script.

```bash
cd src/tcpdump/
./tcpdump.sh
```

This will star capturing network traffic in /var/tmp/pcap folder.

### Python parsing

Run `mqtt_publish.py` python module from src/tcpdump folder.

```bash
# from src/tcpdump
python mqtt_publish.py
```

This module would parse the network packets, summarize them and publish them to
topic `cs498/iot/usage`.

If everything is correctly setup, you should get SMS on subscribed cellphone on
high usage. You can play with threshold in `NotifyMentor` lambda to test value
that suits your use.

### Electron-app

Go to src/electron-app folder. Install npm dependencies and start the
application.

```bash
cd src/electron-app
npm install
npm start
```

Once application starts you can click on `Get New` button to request information
or wait for five minutes to get the message from IoT topic.

## Acknowledgement

- Goal tracker is my personal favorite and was on my agenda to build something
  like for a long. I am thankful for Professor Matt to provide me an opportunity
  to implement this idea while learning about IoT systems and technologies.
- I would also like to acknowledge the support from TA and fellow classmates in
  completing this project and other course labs.
- Je-Clark for his work on ScapyDNSDissection at [GitHub
  Repository](https://github.com/je-clark/ScapyDNSDissection).
