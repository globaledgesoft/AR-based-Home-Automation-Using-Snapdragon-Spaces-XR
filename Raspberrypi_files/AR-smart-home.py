from awscrt import mqtt
import sys
import threading
import time
from uuid import uuid4
import json
import RPi.GPIO as GPIO
import json

import command_line_utils;
cmdUtils = command_line_utils.CommandLineUtils("PubSub - Send and recieve messages through an MQTT connection.")
cmdUtils.add_common_mqtt_commands()
cmdUtils.add_common_topic_message_commands()
cmdUtils.add_common_proxy_commands()
cmdUtils.add_common_logging_commands()
cmdUtils.register_command("key", "<path>", "Path to your key in PEM format.", True, str)
cmdUtils.register_command("cert", "<path>", "Path to your client certificate in PEM format.", True, str)
cmdUtils.register_command("port", "<int>", "Connection port. AWS IoT supports 443 and 8883 (optional, default=auto).", type=int)
cmdUtils.register_command("client_id", "<str>", "Client ID to use for MQTT connection (optional, default='test-*').", default="test-" + str(uuid4()))
cmdUtils.register_command("count", "<int>", "The number of messages to send (optional, default='10').", default=10, type=int)
cmdUtils.register_command("is_ci", "<str>", "If present the sample will run in CI mode (optional, default='None')")
cmdUtils.get_args()

received_count = 0
received_all_event = threading.Event()
is_ci = cmdUtils.get_command("is_ci", None) != None
LED = 38
FAN = 40
GPIO.setwarnings(False) 	#disable warnings
GPIO.setmode(GPIO.BOARD)	#set pin numbering format
GPIO.setup(LED, GPIO.OUT)	#set GPIO as output
GPIO.setup(FAN, GPIO.OUT)	#set GPIO as output
#--------- Global variables -----------------
IOT_Device_Name = "BT-Beacon_room1"
get_config_topic = 'sdk/Falcon/AR/getconfig'
set_config_topic = 'sdk/Falcon/AR/setconfig'
db_data = ''
db_file_name = 'Falcon_db'
#--------------------------------------------

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))

def Publish_msg(Topic, Pub_payload):
    print("Publishing message to topic '{}': {}".format(Topic, Pub_payload))
    message_json = json.dumps(Pub_payload)
    mqtt_connection.publish(
        topic=Topic,
        payload=message_json,
        qos=mqtt.QoS.AT_LEAST_ONCE)
    time.sleep(1)


def reply_config(topic, payload, dup, qos, retain, **kwargs):
    print("received message on topic '{}': {}".format(topic, payload))
    Ack_topic = get_config_topic+"_ack"
    payload = get_data_from_file()
    # payload={ "location" : IOT_Device_Name, "devices" : {"light" : "on/off" , "fan" :"on/off" }}
    Publish_msg(Topic=Ack_topic, Pub_payload=payload)
    return True

def get_data_from_file():
    # Using a JSON string
    with open(db_file_name, 'r') as file_object:  
        db_data = json.load(file_object)
    return db_data

def save_data_from_file(save_data):
    # Directly from dictionary
    with open(db_file_name, 'w') as outfile:
        json.dump(save_data, outfile)


# Callback when the subscribed topic receives a message
def set_config_callback(topic, payload, dup, qos, retain, **kwargs):
    # print("Received message from topic '{}': {}".format(topic, payload))
    msg = payload.decode()
    # print(msg)
    msg = json.loads(payload)
    db_data = get_data_from_file()
    #-- trun of the LED..
    if msg["location"] == IOT_Device_Name:
        try:
            if "devices" in msg.keys():
                if "light" in msg["devices"].keys():
                    if msg["devices"]["light"]['status'] == 'on' :
                        print("Light - ON")
                        GPIO.output(LED,GPIO.HIGH)
                        db_data["devices"]["light"]["status"] = 'on'
                        db_data["devices"]["light"]["ack"] = 'true'
                        db_data["devices"]["light"]["err_msg"] = ''
                    elif msg["devices"]["light"]["status"] == 'off' :
                        print("Light - OFF")
                        GPIO.output(LED,GPIO.LOW)
                        db_data["devices"]["light"]["status"] = 'off'
                        db_data["devices"]["light"]["ack"] = 'true'
                        db_data["devices"]["light"]["err_msg"] = ''
                    else:
                        print("Got invalid value for Light - Status not changed("+db_data["devices"]["light"]["status"]+")")
                        # GPIO.output(LED,GPIO.LOW)
                        # db_data["devices"]["light"]["status"] = 'off'
                        db_data["devices"]["light"]["ack"] = 'false'
                        db_data["devices"]["light"]["err_msg"] = 'got invalid value in status -' + msg["devices"]["light"]["status"]

                    
                if "fan" in msg["devices"].keys():
                    if msg["devices"]["fan"]['status'] == 'on' :
                        print("Fan - ON")
                        GPIO.output(LED,GPIO.HIGH)
                        db_data["devices"]["fan"]["status"] = 'on'
                        db_data["devices"]["fan"]["ack"] = 'true'
                        db_data["devices"]["fan"]["err_msg"] = ''
                    elif msg["devices"]["fan"]['status'] == 'off' :
                        print("Fan - OFF")
                        GPIO.output(LED,GPIO.LOW)
                        db_data["devices"]["fan"]["status"] = 'off'
                        db_data["devices"]["fan"]["ack"] = 'true'
                        db_data["devices"]["fan"]["err_msg"] = ''
                    else:
                        print("Got invalid value for Fan - Status not changed("+db_data["devices"]["fan"]["status"]+")")
                        # print("Got invalid value for Fan - OFF")
                        # GPIO.output(LED,GPIO.LOW)
                        db_data["devices"]["fan"]["ack"] = 'false'
                        db_data["devices"]["fan"]["err_msg"] = 'got invalid value in status -' + msg["devices"]["fan"]["status"]

        except Exception as e :
            print("Exception : ", e)
    else:
        print("User at other then "+msg["location"])
        print("Led and Fan OFF..")
        GPIO.output(LED,GPIO.LOW)
        GPIO.output(FAN,GPIO.LOW)
        db_data["devices"]["light"]["status"] = 'off'
        db_data["devices"]["fan"]["status"] = 'off'
    # print(db_data)
    Ack_topic = set_config_topic+"_ack"
    save_data_from_file(db_data)
    Publish_msg(Topic=Ack_topic, Pub_payload=db_data)


if __name__ == '__main__':
    mqtt_connection = cmdUtils.build_mqtt_connection(on_connection_interrupted, on_connection_resumed)

    if is_ci == False:
        print("Connecting to {} with client ID '{}'...".format(
            cmdUtils.get_command(cmdUtils.m_cmd_endpoint), cmdUtils.get_command("client_id")))
    else:
        print("Connecting to endpoint with client ID")
    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    message_count = cmdUtils.get_command("count")
    message_topic = cmdUtils.get_command(cmdUtils.m_cmd_topic)
    # message_string = cmdUtils.get_command(cmdUtils.m_cmd_message)

    #----------- Subscribe for get config.. -----------#
    # print("Subscribing to topic '{}'...".format(message_topic))
    print("Subscribing to topic '{}'...".format(get_config_topic))
    subscribe_get_config_future, get_config_packet_id = mqtt_connection.subscribe(
        # topic=message_topic,
        topic=get_config_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=reply_config)

    subscribe_get_config = subscribe_get_config_future.result()
    print("Subscribed with {}".format(str(subscribe_get_config['qos'])))

    #----------- Subscribe for set config.. -----------#
    # print("Subscribing to topic '{}'...".format(message_topic))
    print("Subscribing to topic '{}'...".format(set_config_topic))
    subscribe_set_config_future, set_config_packet_id = mqtt_connection.subscribe(
        # topic=message_topic,
        topic=set_config_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=set_config_callback)

    subscribe_set_config = subscribe_set_config_future.result()
    print("Subscribed with {}".format(str(subscribe_set_config['qos'])))

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if message_count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...")

    received_all_event.wait()
    print("{} message(s) received.".format(received_count))

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")
