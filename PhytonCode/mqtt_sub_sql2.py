import sys
import threading
import paho.mqtt.client as paho
import time
import signal


import mysql.connector
from mysql.connector import errorcode

# Replace these variables with your MySQL server's credentials
host = "Localhost"
user = "root"
password = "booz2005"

# Database and table names
database_name = "ciudadesinteligentes"
table_name = "traffic_detection"

# Setup the MySQL database and table
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

    # Create the table if it doesn't exist
    table_creation_query = (
        f"CREATE TABLE IF NOT EXISTS {table_name} ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "value INT NOT NULL)"
    )
    cursor.execute(table_creation_query)
    print(f"Table '{table_name}' is ready.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    cursor.close()
    cnx.close()
    
client1 = paho.Client()
client2 = paho.Client()

data1 = None
data2 = None

apprun = True

def insert_into_db(data):
    try:
        # Connect to the MySQL server
        cnx = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_name
        )
        cursor = cnx.cursor()

        # Insert the received payload into the table
        insertion_query = f"INSERT INTO {table_name} (detection) VALUES ({data})"
        cursor.execute(insertion_query)
        cnx.commit()
        print(f"Inserted value {data} into table '{table_name}'.")

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        cursor.close()
        cnx.close()

def message_handling_1(client, userdata, msg):
    global data1
    data1 = msg.payload.decode()
    insert_into_db(data1)
    #print(f"{msg.topic}: {data1}")

def message_handling_2(client, userdata, msg):
    global data2
    data2 = msg.payload.decode()
    insert_into_db(data2)
    #print(f"{msg.topic}: {data2}")

def loop_1(num):
    global client1
    client1.loop_forever()

def loop_2(num):
    global client2
    client2.loop_forever()
        
client1.on_message = message_handling_1
client2.on_message = message_handling_2

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
client2.subscribe("arduino_2/hello_esp8266")

try:
    print("Press CTRL+C to exit...")
    t1 = threading.Thread(target=loop_1, args=(0,))
    t2 = threading.Thread(target=loop_2, args=(0,))
    
    t1.start()
    t2.start()
    
    while(apprun):
        try:
            time.sleep(0.5)
            print("data1:" + str(data1))
            print("data2:" + str(data2))
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
