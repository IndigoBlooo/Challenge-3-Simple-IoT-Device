from umqtt.robust import MQTTClient
import network
import time
import machine

#----Network ID Information-----

ssid = "********"
password = "*******"

#-------------------------------

#-----Wi-Fi station interface-----
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print ("Attempting to connect to WiFi network:", ssid)

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
    return

else:
    print("Failed to connect to Wifi.")
    return None



#------ LED Pin Setup------- CHANGE THIS PIN LATER!

try:
    LED_PIN = 2
    led = machine.Pin(LED_PIN, machine.Pin.OUT)
    led.off()
    print(f"LED initialized on Pin 2")

except Exception as e:
    print(f"Error setting up hardware pin: {e})

#---- This is where I will configure MQTT-----

# The public test broker

BROKER = "broker.hivemq.com"


# This is where the unique client ID will go

CLIENT_ID = b"esp32_led_controller_" + machine.unique_id()

# Two topics
TOPIC_COMMAND = b"wyohack/Madeleine_Wallace/led/command"
TOPIC_STATUS = b"wyohack/Madeleine_Wallace/led/status"

#------- A publish status ----------
def publish_status(state):
    try:
        client.publish(TOPIC_STATUS, state)
        print("Status published:", state)
    except Exception as e:
        print("Failed to publish status", e)

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
def connect_mqtt():
    global client
    print("Connecting to MQTT broker...")
    client = MQTTClient(CLIENT_ID, BROKER)

    client.set_callback(mqtt_callback)
    client.connect()
    print("MQTT has connected!")

    client.subscribe(TOPIC_COMMAND)
    print("Subscribed to:", ...TOPIC_COMMAND)

    client.subscribe(TOPIC_STATUS)
    print("Subscribed to:", ...TOPIC_STATUS)


#-------- Reconneting Logic ---------
def reconnect():
    print("Reconnecting...")
    time.sleep(2)
    machine.reset()


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
