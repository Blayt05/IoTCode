def insert_traffic_light(address_light, type_light):
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

        check_light_id_query = f"SELECT COUNT(*) FROM {table_name_traffic_light} WHERE light_id = %s"
        cursor.execute(check_light_id_query, (light_id_value,))
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"El light_id {light_id_value} ya está registrado en la base de datos.")
            return

        # Insertar en `traffic_light` con light_id específico
        insert_light_query = f"INSERT INTO {table_name_traffic_light} (light_id, address_light, type_light) VALUES (%s, %s, %s)"
        cursor.execute(insert_light_query, (light_id_value, address_light, type_light))
        
        # Obtener el light_id recién creado
        last_light_id = cursor.lastrowid
        print(f"Inserted light_id {light_id_value}, address_light '{address_light}', type_light '{type_light}' with light_id {last_light_id}.")
        return last_light_id

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
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