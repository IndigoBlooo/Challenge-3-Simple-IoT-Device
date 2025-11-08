#!/bin/bash

from umqtt.robust import MQTTClient
import network
import time
import machine

#----Network ID Information-----

ssid = "Digital Native Cyber City"
password = "dnc-wireless"

#-------------------------------

#-----Wi-Fi station interface-----
station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(SSID, PASSWORD)

print ("Attempting to connect to WiFi network:", ssid)

#----- This will check if it is already conntected-------

if not wlan.isconntected():
    wlan.conntect(ssid, password)
    
    max_wait_seconds = 15
    start_time = time.ticks_ms()

    print ("Conntecting", end="")
    while not wlan.isconnected() and time.ticks_diff(time.ticks_ms(), start_time) < max_wait_seconds * 1000:
        print(".", end="")
        time.sleep(1)
    print()

if wlan.isconnected():
    print("WiFi connected successfully!")
    network_config = wlan.ifconfig()
    print("IP address:", network_config[0])

else:
    print("Failed to connect to Wifi.")



#------ LED Pin Setup------- CHANGE THIS PIN LATER!

try
    LED_PIN = 2
    led = machine.Pin(LED_PIN, machine.Pin.OUT)
    led.off()
    print(f"LED initialized on Pin 2)

except Exception as e:
    print(f"Error setting up hardware pin: {e})

#---- This is where I will configure MQTT-----

#An indicator incase WiFi is not working
if not wlan.isconnected():

    print("Error: WiFi not connected. Cannot use MQTT.")

else:

# The public test broker

    mqtt_broker = "broker.hivemq.com"


    # This is where the unique client ID will go

    client_id = b"esp32_led_controller_" + machine.unique_id()

# Two topics
    topic_pub = b"wyohack/Madeleine_Wallace/led/command"
    topic_pub = b"wyohack/Madeleine_Wallace/led/status"

#----Callback Function for .../command topic-------

def mqtt_callback(topic, msg):
    message = msg.decode().strip().upper()
    print ("Received:", message)

    if message == "ON":
        led.value(1)
        publish_status("ON")

    elif message == "OFF":
        led.value(0)
        publish_status("OFF")

    else:
        print("Unknown command:", message)

#-------Connecting MQTT---------
def conntect_mqtt():
    global client
    print("Conntecting to MQTT broker...")
    client = MQTTClient(CLIENT_ID, BROKER)

    client.set.callback(mqtt_callback)
    client.connect()
    print("MQTT has connected!")

    client.subscribe(TOPIC_COMMAND)
    print("Subscribed to:", TOPIC_COMMAND)

    client.subscribe(TOPIC_STATUS)
    print("Subscribed to:", TOPIC_STATUS)


#-------- Reconneting Logic ---------
def reconnect():
    print("Reconnecting...")
    time.sleep(2)
    machine.reset()

if not connect_wifi():
    reconnect()

try:
    connect_mqtt()
except Exception as e:
    print("MQTT connect error:", e)
    reconnect()

print("Running main loop...\n")


#----- The Main MQTT Loop --------
while True:
    try:
        client.check_msg() #This will check 4 pending messages
        time.sleep(0.5)
    
    except OSError as e:
        print(f"Error connecting or subscribing via MQTT: {e}")
        reconnect()

except Exception as e:
    print(f"An unexpected error occurred:{e}")

finally:
    print("MQTT Loop finished or an error occurred.")