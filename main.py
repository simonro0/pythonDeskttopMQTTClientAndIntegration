import math
import numbers
import subprocess
import threading
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
default_header = "MQTT-Backggroundscript"

# General data
localMqttBroker = "192.168.0.198"
start_time = time.time()
mqtt_client = mqtt.Client()

quit_publish_loop = False
# Own topics to send
general_topic = "computer"
default_topic = general_topic + "/running"
start_time_topic = general_topic + "/starttime"
shutdown_time_topic = general_topic + "/shutdowntime"

publishNotifications = "nodered/notify"
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
            content = "Shutting down in 10 seconds"
            print(current_time + content)
            notify_timer1 = threading.Timer(3, shut_down_hint, [3])
            notify_timer2 = threading.Timer(6, shut_down_hint, [6])
            notify_timer3 = threading.Timer(9, shut_down_hint, [9])
            do_timer = threading.Timer(11, shut_down_computer)

            client.publish(topic=publishNotifications, payload="Computer is shutting down!", qos=QOS['Exactly once'])
            global default_header
            windowsUserNotifier.show_toast(default_header, content)
            notify_timer1.start()
            notify_timer2.start()
            notify_timer3.start()
            do_timer.start()

            # Previous attempt to use the existing script and setting the shutdown time to 1 minute
            # configfilename = "E:/Eigene Dateien/Eigene Programme/AutoHotkey/NoCapslockAndShortkeys/ShutdownAtIn.ini"
            # parser = ConfigParser()
            # parser.read(configfilename)
            # parser.set("General", "RestDurationInMinutes", "1")
            # with open(configfilename, "w") as configfile:
            #     parser.write(configfile)
        if command == "/hint":
            header = "MQTT-Remote-Notification"
            content = msg.topic + ": " + str(msg.payload)
            print(current_time + "Got a hint: " + content)
            windowsUserNotifier.show_toast(header, content)
        if command == "/volume_up":
            volume_up()
        if command == "/volume_down":
            volume_down()
        if command == "/volume_set":
            volume_set(msg.payload)


# The callback for having new subscriptions
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscription was called")


def shut_down_hint(time_waited):
    global default_header
    content = "Shutting down in {remaining:n} seconds".format(remaining=math.floor(10-time_waited))
    windowsUserNotifier.show_toast(title=default_header, msg=content, duration=2, threaded=True)


def shut_down_computer():
    global default_header
    global quit_publish_loop
    quit_publish_loop = True
    content = "Shutting down!"
    windowsUserNotifier.show_toast(title=default_header, msg=content, duration=2, threaded=True)
    subprocess.run("shutdown /s /f")


def volume_up():
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    import math
    # Get default audio device using PyCAW
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # Get current volume
    current_volume_db = volume.GetMasterVolumeLevel()
    percent_value = convert_db_to_percent(current_volume_db)
    print("current master volume is: %sdb %sperc" % (current_volume_db, percent_value))
    print("new master volume is: %sdb %sperc" % (convert_percent_to_db(percent_value + 10), percent_value + 10))
    volume.SetMasterVolumeLevel(convert_percent_to_db(percent_value + 10), None)  # NOTE: -6.0 dB = half volume !


def volume_down():
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    import math
    # Get default audio device using PyCAW
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # Get current volume
    current_volume_db = volume.GetMasterVolumeLevel()
    percent_value = convert_db_to_percent(current_volume_db)
    new_db_value = convert_percent_to_db(percent_value - 10)
    print("current master volume is: %sdb %sperc" % (current_volume_db, percent_value))
    print("new master volume is: %sdb %sperc" % (new_db_value, percent_value - 10))
    volume.SetMasterVolumeLevel(new_db_value, None)  # NOTE: -6.0 dB = half volume !


def volume_set(value_to_set):
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    import math
    # Get default audio device using PyCAW
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # Get current volume
    current_volume_db = volume.GetMasterVolumeLevel()
    new_db_value = convert_percent_to_db(value_to_set)
    print("current master volume is: %sdb %sperc" % (current_volume_db, convert_db_to_percent(current_volume_db)))
    print("new master volume is: %sdb %sperc" % (new_db_value, value_to_set))
    volume.SetMasterVolumeLevel(new_db_value, None)


def convert_db_to_percent(db):
    # print("dbgot value %s" % db)
    db += 62.0
    db = max(0.0, db)
    db = min(db, 64.0)
    # print("dbgot value %s after min max" % (db-62))
    result = pow(10, (db/35.0))*1.5 - 1.0
    result = max(0.0, result)
    result = min(result, 100.0)
    # print("dbgot result %s afterwards" % result)
    return result


def convert_percent_to_db(percent):
    # print("got value %s" % percent)
    percent = min(percent, 100.0)
    percent = max(0.0, percent)
    # print("got value %s after min max" % percent)
    result = math.log((percent+1)/1.5, 10) * 35.0 - 62
    result = max(-62.0, result)
    result = min(result, 2.0)
    # print("got result %s afterwards" % result)
    return result


mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_subscribe = on_subscribe

mqtt_client.will_set(topic=last_will, payload="unexpected_shutdown", qos=QOS['Exactly once'], retain=False)
mqtt_client.connect(host=localMqttBroker, port=1883, keepalive=60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqtt_client.loop_start()

mqtt_client.publish(topic=default_topic, payload="True", qos=QOS['Exactly once'])
mqtt_client.publish(topic=start_time_topic, payload=start_time, qos=QOS['Exactly once'])
while not quit_publish_loop:
    time.sleep(30)  # wait some seconds until next publish
    mqtt_client.publish(topic=default_topic, payload="True", qos=QOS['Exactly once'])

mqtt_client.publish(topic=shutdown_time_topic, payload=time.time(), qos=QOS['Exactly once'])
mqtt_client.publish(topic=default_topic, payload="False", qos=QOS['Exactly once'])
mqtt_client.loop_stop()
