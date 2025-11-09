from umqtt.robust import MQTTClient
import network
import time
import machine

#----Network ID Information-----

SSID = "digital native cyber city"
PASSWORD = "dnc-wireless"

#-------------------------------

#-----Wi-Fi station interface-----
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print ("Attempting to connect to WiFi network:", SSID )

    wlan.connect(SSID, PASSWORD)
    
    max_wait_seconds = 15
    start_time = time.ticks_ms()

    print ("Connecting", end="")
    while not wlan.isconnected() and time.ticks_diff(time.ticks_ms(), start_time) < max_wait_seconds * 1000:
        print(".", end="")
        time.sleep(1)
    print()

    if wlan.isconnected():
        print("WiFi connected successfully!")
        print("IP address:", wlan.ifconfig()[0])
        return wlan

    else:
        print("Failed to connect to Wifi.")
        return None



#------ LED Pin Setup ------- 

try:
    LED_PIN = 34
    led = machine.Pin(LED_PIN, machine.Pin.OUT)
    led.off()
    print("LED initialized on Pin 34")

except Exception as e:
    print(f"Error setting up hardware pin: {e}")


# ----- The public test broker ------- 

BROKER = "broker.hivemq.com"


#----- This is the unique client ID ------

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

#---- Callback Function for .../command topic -------

def mqtt_callback(topic, msg):
    message = msg.decode().strip().upper()
    print ("Received:", message)

    if message == "ON":
        led.value(1)
        publish_status(b"ON")

    elif message == "OFF":
        led.value(0)
        publish_status(b"OFF")

    else:
        print("Unknown command:", message)



#------- Connecting MQTT ---------
def connect_mqtt():
    global client
    print("Connecting to MQTT broker...")
    client = MQTTClient(CLIENT_ID, BROKER)

    client.set_callback(mqtt_callback)
    client.connect()
    print("MQTT has connected!")

    client.subscribe(TOPIC_COMMAND)
    print("Subscribed to:", TOPIC_COMMAND)

    client.subscribe(TOPIC_STATUS)
    print("Subscribed to:", TOPIC_STATUS)


#-------- Reconnecting Logic ---------
def reconnect():
    print("Reconnecting...")
    time.sleep(2)
    machine.reset()

wlan = connect_wifi()
if not wlan:
    raise SystemExit

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
        reconnect()