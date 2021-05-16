import threading
from uuid import uuid4
import time
import sys

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder


def get_client_bootstrap():
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    return io.ClientBootstrap(event_loop_group, host_resolver)


io.init_logging(getattr(io.LogLevel, io.LogLevel.NoLogs.name), 'stderr')

received_count = 0
received_all_event = threading.Event()

# Callback when connection is accidentally lost.


def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(
        return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    # global received_count
    # received_count += 1
    # if received_count == args.count:
    #     received_all_event.set()


class MQTTClient:
    def __init__(self, endpoint, cert, key, root_ca, client_id=None):
        if not client_id:
            self.client_id = "test-" + str(uuid4())
        else:
            self.client_id = client_id
        self.endpoint = endpoint
        client_bootstrap = get_client_bootstrap()
        self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            cert_filepath=cert,
            pri_key_filepath=key,
            client_bootstrap=client_bootstrap,
            ca_filepath=root_ca,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=self.client_id,
            clean_session=False,
            keep_alive_secs=6)

    def connect(self):
        print("Connecting to {} with client ID '{}'...".format(
            self.endpoint, self.client_id))

        connect_future = self.mqtt_connection.connect()

        # Future.result() waits until a result is available
        connect_future.result()
        print("Connected!")

    def subscribe(self, topic):
        print("Subscribing to topic '{}'...".format(topic))
        subscribe_future, packet_id = self.mqtt_connection.subscribe(
            topic=topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_message_received)

        subscribe_result = subscribe_future.result()
        print("Subscribed with {}".format(
            str(subscribe_result['qos'])))

    def publish(self, topic, message):
        print("Publishing message to topic '{}'".format(topic))
        self.mqtt_connection.publish(
            topic=topic,
            payload=message,
            qos=mqtt.QoS.AT_LEAST_ONCE)
        time.sleep(1)

    def disconnect(self):
        # Disconnect
        print("Disconnecting...")
        disconnect_future = self.mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")
