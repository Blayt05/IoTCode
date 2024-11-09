import sys
import threading
import paho.mqtt.client as paho
import time
import signal
import json

import mysql.connector
from mysql.connector import errorcode

# Replace these variables with your MySQL server's credentials
host = "localhost"
user = "root"
password = "booz2005"

# Database and table names
database_name = "ciudadesinteligentes"
table_name_detection = "traffic_detection"
table_name_led_settings = "settings_leds"
table_name_traffic_light = "traffic_light"

# Coordenadas y tipo de semáforo definidos para cada cliente
coordinates_client1 = "25.651417, -100.292138"
type_light_client1 = "Semaforo Vehicular"

coordinates_client2 = "25.671234, -100.312345"
type_light_client2 = "Semaforo Peatonal"

# Setup the MySQL database and table
def setup_database():
    try:
        cnx = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = cnx.cursor()

        # Create the database if it doesn't exist
        try:
            cursor.execute(f"CREATE DATABASE {database_name}")
            print(f"Database '{database_name}' created successfully.")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DB_CREATE_EXISTS:
                print(f"Database '{database_name}' already exists.")
            else:
                print(err.msg)

        # Connect to the newly created or existing database
        cnx.database = database_name

        # Create the tables if they don't exist
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name_traffic_light} ("
            "light_id INT AUTO_INCREMENT PRIMARY KEY, "
            "address_light VARCHAR(255), "
            "type_light VARCHAR(255))"
        )
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name_detection} ("
            "id INT AUTO_INCREMENT PRIMARY KEY, "
            "detection INT NOT NULL, "
            "light_id INT, "
            "FOREIGN KEY (light_id) REFERENCES {table_name_traffic_light}(light_id))"
        )
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name_led_settings} ("
            "id INT AUTO_INCREMENT PRIMARY KEY, "
            "led_color VARCHAR(50), "
            "time_leds INT, "
            "light_id INT, "
            "FOREIGN KEY (light_id) REFERENCES {table_name_traffic_light}(light_id))"
        )
        print("Tables are ready.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        cnx.close()

setup_database()

client1 = paho.Client()
client2 = paho.Client()

data1 = None
data2 = None
data_color_time = None

apprun = True

def insert_data(address_light, type_light, detection, color, time_leds):
    try:
        cnx = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_name
        )
        cursor = cnx.cursor()

        # Determinar el valor de light_id basado en el tipo de semáforo
        if type_light == "Semaforo Vehicular":
            light_id_value = 1
        elif type_light == "Semaforo Peatonal":
            light_id_value = 2
        else:
            print("Unknown light type")
            return

        # Insertar en `traffic_light` con light_id específico
        insert_light_query = (
            f"INSERT INTO {table_name_traffic_light} (light_id, address_light, type_light) "
            "VALUES (%s, %s, %s)"
        )
        cursor.execute(insert_light_query, (light_id_value, address_light, type_light))
        
        # Obtener el light_id recién creado
        last_light_id = cursor.lastrowid

        # Insertar en `traffic_detection` usando el light_id
        insert_detection_query = (
            f"INSERT INTO {table_name_detection} (detection, light_id) VALUES (%s, %s)"
        )
        cursor.execute(insert_detection_query, (detection, last_light_id))

        # Insertar en `settings_leds` usando el light_id
        insert_led_query = (
            f"INSERT INTO {table_name_led_settings} (led_color, time_leds, light_id) VALUES (%s, %s, %s)"
        )
        cursor.execute(insert_led_query, (color, time_leds, last_light_id))

        # Confirmar la transacción
        cnx.commit()

        print(f"Inserted light_id {light_id_value}, address_light '{address_light}', type_light '{type_light}', "
              f"detection {detection}, color '{color}', time {time_leds} with light_id {last_light_id}.")

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        cursor.close()
        cnx.close()
    

def message_handling_1(client, userdata, msg):
    global data1
    data1 = int(msg.payload.decode())
    insert_data(coordinates_client1, type_light_client1, data1, 'Verde', 5)

def message_handling_2(client, userdata, msg):
    global data2
    data2 = int(msg.payload.decode())
    insert_data(coordinates_client2, type_light_client2, data2, 'Rojo', 3)

def message_handling_color_time(client, userdata, msg):
    try:
        message = msg.payload.decode()
        parts = message.split(",")
        color = parts[0].split(":")[1].strip()
        time_str = parts[1].split(":")[1].strip()
        time_leds = int(time_str.split()[0])

        if client == client1:
            insert_data(coordinates_client1, type_light_client1, 1, color, time_leds)
        else:
            insert_data(coordinates_client2, type_light_client2, 1, color, time_leds)

        print(f"Color: {color}, Time: {time_leds}")

    except Exception as e:
        print(f"Error processing the message: {e}")

def loop_1(num):
    global client1
    client1.loop_forever()

def loop_2(num):
    global client2
    client2.loop_forever()

client1.on_message = message_handling_1
client2.on_message = message_handling_2

client1.message_callback_add("arduino_1/led_state", message_handling_color_time)
client1.message_callback_add("arduino_1/sensor_deteccion", message_handling_1)

client2.message_callback_add("arduino_2/led_state", message_handling_color_time)
client2.message_callback_add("arduino_2/sensor_deteccion", message_handling_2)

def signal_handler(sig, frame):
    global client1
    global client2
    print('You pressed Ctrl+C!')
    client1.disconnect()
    client2.disconnect()
    print("Quit")
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

if client1.connect("172.20.10.3", 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    exit(1)
    
if client2.connect("172.20.10.3", 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    exit(1)

client1.subscribe("arduino_1/sensor_deteccion")
client1.subscribe("arduino_1/led_state")
client2.subscribe("arduino_2/sensor_deteccion")
client2.subscribe("arduino_2/led_state")

try:
    print("Press CTRL+C to exit...")
    t1 = threading.Thread(target=loop_1, args=(0,))
    t2 = threading.Thread(target=loop_2, args=(0,))
    
    t1.start()
    t2.start()
    
    while apprun:
        try:
            time.sleep(0.5)
            print("data1:", data1)
            print("data2:", data2)
            print("----")
        except KeyboardInterrupt:
            print("Disconnecting")
            apprun = False
            client1.disconnect()
            client2.disconnect()
            time.sleep(1)
    
    t1.join()
    t2.join()
    
except Exception:
    print("Caught an Exception, something went wrong...")
