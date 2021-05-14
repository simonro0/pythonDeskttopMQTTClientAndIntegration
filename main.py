import subprocess
import time
from win10toast import ToastNotifier
# from configparser import ConfigParser

import paho.mqtt.client as mqtt
from datetime import datetime
import pytz
# now = datetime.now(pytz.timezone('Europe/Amsterdam'))
# current_time = now.strftime("%Y-%m-%d %H:%M:%S ")
# print(current_time)

QOS = {'At most once': 0, 'At least once': 1, 'Exactly once': 2}
windowsUserNotifier = ToastNotifier()

# General data
localMqttBroker = "192.168.0.198"
starttime = time.time()

quit_publish_loop = False
# Own topics to send
general_topic = "computer"
default_topic = general_topic + "/running"
startime_topic = general_topic + "/starttime"
shutdowntime_topic = general_topic + "/shutdowntime"

last_will = general_topic + "/lastwill"

# Topics to subscribe
request_topics = general_topic + "/command"
request_commands = {"/shutdown"}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result: " + mqtt.connack_string(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")  #this might subscribe to every message on the broker
    client.subscribe(request_topics + "/#")
    # subscribe.callback(callback=on_message, topics=request_topics, qos=QOS['Exactly once'], hostname=localMqttBroker) #blocking function


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    now = datetime.now(pytz.timezone('Europe/Amsterdam'))
    current_time = now.strftime("%Y-%m-%d %H:%M:%S ")

    print(current_time + msg.topic + " " + str(msg.payload))
    if msg.topic.startswith(request_topics):
        command = msg.topic[len(request_topics):]
        if command == "/shutdown":
            header = "MQTT-Backggroundscript"
            content = "Shutting down in 10 seconds"
            print(current_time + content)
            windowsUserNotifier.show_toast(header, content)
            # Previous attempt to use the existing script and setting the shutdown time to 1 minute
            # configfilename = "E:/Eigene Dateien/Eigene Programme/AutoHotkey/NoCapslockAndShortkeys/ShutdownAtIn.ini"
            # parser = ConfigParser()
            # parser.read(configfilename)
            # parser.set("General", "RestDurationInMinutes", "1")
            # with open(configfilename, "w") as configfile:
            #     parser.write(configfile)

            global quit_publish_loop
            quit_publish_loop = True
            time.sleep(10)
            subprocess.run("shutdown /s /f")
        if command == "/hint":
            header = "MQTT-Notification"
            content = msg.topic + ": " + str(msg.payload)
            print(current_time + "Got a hint: " + content)
            windowsUserNotifier.show_toast(header, content)


# The callback for having new subscriptions
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscription was called")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe

client.will_set(topic=last_will, payload="unexpected_shutdown", qos=QOS['Exactly once'], retain=False)
client.connect(host=localMqttBroker, port=1883, keepalive=60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()

client.publish(topic=default_topic, payload="True", qos=QOS['Exactly once'])
client.publish(topic=startime_topic, payload=starttime, qos=QOS['Exactly once'])
while not quit_publish_loop:
    time.sleep(30)  # wait some seconds until next publish
    client.publish(topic=default_topic, payload="True", qos=QOS['Exactly once'])

client.publish(topic=shutdowntime_topic, payload=time.time(), qos=QOS['Exactly once'])
client.publish(topic=default_topic, payload="False", qos=QOS['Exactly once'])
client.loop_stop()
