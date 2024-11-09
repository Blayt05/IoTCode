import sys
import threading
import os
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


        cnx.database = database_name

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

def insert_traffic_light(address_light, type_light):
    try:
        cnx = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_name
        )
        cursor = cnx.cursor()

        # Verificar si el semáforo con ese `address_light` y `type_light` ya existe
        select_query = f"SELECT light_id FROM {table_name_traffic_light} WHERE address_light = %s AND type_light = %s"
        cursor.execute(select_query, (address_light, type_light))
        result = cursor.fetchone()

        if result:
            # Si ya existe, usar el `light_id` existente
            light_id_value = result[0]
            print(f"Using existing light_id {light_id_value} for address '{address_light}', type '{type_light}'.")
        else:
            # Si no existe, insertar un nuevo registro y obtener el nuevo `light_id` asignado automáticamente
            insert_light_query = f"INSERT INTO {table_name_traffic_light} (address_light, type_light) VALUES (%s, %s)"
            cursor.execute(insert_light_query, (address_light, type_light))
            cnx.commit()  # Confirmar la inserción

            # Obtener el nuevo `light_id` asignado por `AUTO_INCREMENT`
            light_id_value = cursor.lastrowid
            print(f"Inserted new light_id {light_id_value} for address '{address_light}', type '{type_light}'.")

        return light_id_value

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return None
    finally:
        cursor.close()
        cnx.close()





def insert_traffic_detection(detection, light_id):
    try:
        cnx = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_name
        )
        cursor = cnx.cursor()

        # Insertar en `traffic_detection` usando el light_id
        insert_detection_query = f"INSERT INTO {table_name_detection} (detection, light_id) VALUES (%s, %s)"
        cursor.execute(insert_detection_query, (detection, light_id))

        cnx.commit()
        print(f"Inserted detection {detection} for light_id {light_id}.")

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        cursor.close()
        cnx.close()

def insert_settings_leds(color, time_leds, light_id):
    try:
        cnx = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_name
        )
        cursor = cnx.cursor()

        # Insertar en `settings_leds` usando el light_id
        insert_led_query = f"INSERT INTO {table_name_led_settings} (led_color, time_leds, light_id) VALUES (%s, %s, %s)"
        cursor.execute(insert_led_query, (color, time_leds, light_id))

        cnx.commit()
        print(f"Inserted LED color '{color}' and time {time_leds} for light_id {light_id}.")

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        cursor.close()
        cnx.close()

def insert_data(address_light, type_light, detection, color, time_leds):
    # Insertar en `traffic_light` primero y obtener el light_id
    light_id = insert_traffic_light(address_light, type_light)
    if light_id:  # Si se insertó correctamente en `traffic_light`, procedemos con los otros insertos
        # Insertar en `traffic_detection`
        insert_traffic_detection(detection, light_id)
        
        # Insertar en `settings_leds`
        insert_settings_leds(color, time_leds, light_id)


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
            insert_data(coordinates_client1, type_light_client1, data1, color, time_leds)
        else:
            insert_data(coordinates_client2, type_light_client2, data2, color, time_leds)

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

if client1.connect("10.22.181.132", 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    exit(1)
    
if client2.connect("10.22.181.132", 1883, 60) != 0:
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