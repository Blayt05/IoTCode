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
coordinates_client1 = "24.555555, -99.555555"
type_light_client1 = "Semaforo Vehicular"

coordinates_client2 = "25.666666, -100.666666"
type_light_client2 = "Semaforo Peatonal"

coordinates_client3 = "26.777777, -101.777777"
type_light_client3 = "Semaforo Vehicular"

coordinates_client4 = "27.888888, -102.888888"
type_light_client4 = "Semaforo Peatonal"

coordinates_client5 = "29.999999, -103.999999"
type_light_client5 = "Semaforo Vehicular"

coordinates_client6 = "30.000000, -104.000000"
type_light_client6 = "Semaforo Peatonal"

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
client3 = paho.Client()
client4 = paho.Client()
client5 = paho.Client()
client6 = paho.Client()

data1 = None
data2 = None
data3 = None
data4 = None
data5 = None
data6 = None
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

def message_handling_3(client, userdata, msg):
    global data3
    data3 = int(msg.payload.decode())
    insert_data(coordinates_client3, type_light_client3, data3, 'Verde', 5)

def message_handling_4(client, userdata, msg):
    global data4
    data4 = int(msg.payload.decode())
    insert_data(coordinates_client4, type_light_client4, data4, 'Rojo', 3)

def message_handling_5(client, userdata, msg):
    global data5
    data5 = int(msg.payload.decode())
    insert_data(coordinates_client5, type_light_client5, data5, 'Verde', 5)

def message_handling_6(client, userdata, msg):
    global data6
    data6 = int(msg.payload.decode())
    insert_data(coordinates_client6, type_light_client6, data6, 'Rojo', 3)

def message_handling_color_time(client, userdata, msg):
    try:
        message = msg.payload.decode()
        parts = message.split(",")
        color = parts[0].split(":")[1].strip()
        time_str = parts[1].split(":")[1].strip()
        time_leds = int(time_str.split()[0])

        if client == client1:
            insert_data(coordinates_client1, type_light_client1, data1, color, time_leds)
        elif client == client2:
            insert_data(coordinates_client2, type_light_client2, data2, color, time_leds)
        elif client == client3:
            insert_data(coordinates_client3, type_light_client3, data3, color, time_leds)
        elif client == client4:
            insert_data(coordinates_client4, type_light_client4, data4, color, time_leds)
        elif client == client5:
            insert_data(coordinates_client5, type_light_client5, data5, color, time_leds)
        else:
            insert_data(coordinates_client6, type_light_client6, data6, color, time_leds)

        print(f"Color: {color}, Time: {time_leds}")

    except Exception as e:
        print(f"Error processing the message: {e}")

def loop_1(num):
    global client1
    client1.loop_forever()

def loop_2(num):
    global client2
    client2.loop_forever()

def loop_3(num):
    global client3
    client3.loop_forever()

def loop_4(num):
    global client4
    client4.loop_forever()

def loop_5(num):
    global client5
    client5.loop_forever()

def loop_6(num):
    global client6
    client6.loop_forever()

client1.on_message = message_handling_1
client2.on_message = message_handling_2
client3.on_message = message_handling_3
client4.on_message = message_handling_4
client5.on_message = message_handling_5
client6.on_message = message_handling_6


client1.message_callback_add("arduino_1/led_state", message_handling_color_time)
client1.message_callback_add("arduino_1/sensor_deteccion", message_handling_1)

client2.message_callback_add("arduino_2/led_state", message_handling_color_time)
client2.message_callback_add("arduino_2/sensor_deteccion", message_handling_2)

client3.message_callback_add("arduino_3/led_state", message_handling_color_time)
client3.message_callback_add("arduino_3/sensor_deteccion", message_handling_3)

client4.message_callback_add("arduino_4/led_state", message_handling_color_time)
client4.message_callback_add("arduino_4/sensor_deteccion", message_handling_4)

client5.message_callback_add("arduino_5/led_state", message_handling_color_time)
client5.message_callback_add("arduino_5/sensor_deteccion", message_handling_5)

client6.message_callback_add("arduino_6/led_state", message_handling_color_time)
client6.message_callback_add("arduino_6/sensor_deteccion", message_handling_6)

def signal_handler(sig, frame):
    global client1
    global client2
    global client3
    global client4
    global client5
    global client6
    print('You pressed Ctrl+C!')
    client1.disconnect()
    client2.disconnect()
    client3.disconnect()
    client4.disconnect()
    client5.disconnect()
    client6.disconnect()
    print("Quit")
    exit(0)
    
signal.signal(signal.SIGINT, signal_handler)

if client1.connect("10.22.191.55", 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    exit(1)

if client2.connect("10.22.191.55", 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    exit(1)

if client3.connect("10.22.191.55", 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    exit(1)

if client4.connect("10.22.191.55", 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    exit(1)

if client5.connect("10.22.191.55", 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    exit(1)

if client6.connect("10.22.191.55", 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    exit(1)

client1.subscribe("arduino_1/sensor_deteccion")
client1.subscribe("arduino_1/led_state")
client2.subscribe("arduino_2/sensor_deteccion")
client2.subscribe("arduino_2/led_state")
client3.subscribe("arduino_3/sensor_deteccion")
client3.subscribe("arduino_3/led_state")
client4.subscribe("arduino_4/sensor_deteccion")
client4.subscribe("arduino_4/led_state")
client5.subscribe("arduino_5/sensor_deteccion")
client5.subscribe("arduino_5/led_state")
client6.subscribe("arduino_6/sensor_deteccion")
client6.subscribe("arduino_6/led_state")


try:
    print("Press CTRL+C to exit...")
    t1 = threading.Thread(target=loop_1, args=(0,))
    t2 = threading.Thread(target=loop_2, args=(0,))
    t3 = threading.Thread(target=loop_3, args=(0,))
    t4 = threading.Thread(target=loop_4, args=(0,))
    t5 = threading.Thread(target=loop_5, args=(0,))
    t6 = threading.Thread(target=loop_6, args=(0,))
    
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    while apprun:
        try:
            time.sleep(0.5)
            print("data1:", data1)
            print("data2:", data2)
            print("data3:", data3)
            print("data4:", data4)
            print("data5:", data5)
            print("data6:", data6)
            print("----")
        except KeyboardInterrupt:
            print("Disconnecting")
            apprun = False
            client1.disconnect()
            client2.disconnect()
            client3.disconnect()
            client4.disconnect()
            client5.disconnect()
            client6.disconnect()
            time.sleep(1)
    
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    
except Exception:
    print("Caught an Exception, something went wrong...")