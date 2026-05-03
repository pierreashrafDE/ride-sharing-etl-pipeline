import json
import csv
import pyodbc

#data sources preparation
drivers_source = {
    "drivers": [
        {"driver_id": 1, "name": "Ali", "city": "cairo"},
        {"driver_id": 2, "name": "Sara", "city": "giza"},
        {"driver_id": 3, "name": "  ", "city": "alex"},
        {"driver_id": 4, "name": "Mona", "city": ""},
        {"driver_id": 5, "name": "Omar", "city": "cairo"}
    ]
}

rides_source = '''ride_id,driver_id,distance_km,fare
2001,1,10,50
2002,2,15,75
2003,3,8,40
2004,4,12,60
2005,5,20,abc
2006,1,-5,30
2007,2,10,50
2008,6,7,35'''

payments_source = '''payment_id,ride_id,method,status
9001,2001,cash,completed
9002,2002,card,completed
9003,2003,cash,completed
9004,2004,card,failed
9005,2005,cash,completed
9006,2006,cash,completed
9007,2007,card,completed
9008,2009,cash,completed'''

with open('drivers.json', 'w') as file:
    json.dump(drivers_source, file, indent=4)

with open('rides.csv', 'w') as file:
    file.write(rides_source)

with open('payments.txt', 'w') as file:
    file.write(payments_source)

#ETL - Pipeline
#E - Extract phase
rides_data = []
drivers_data = []
payments_data = []

with open('drivers.json', 'r') as file:
    drivers = json.load(file)
    for driver in drivers['drivers']:
        drivers_data.append(driver)

with open('rides.csv', 'r') as file:
    rides = csv.DictReader(file)
    for ride in rides:
        rides_data.append(ride)

with open('payments.txt', 'r') as file:
    lines = file.read()
    lines = lines.strip().split('\n')
    lines = lines[1:]
    for line in lines:
        line = line.split(',')
        payments_data.append(line)
    
#T - Transform phase
clean_rides = []
clean_drivers = []
clean_payments = []

rejected_rides = []
rejected_drivers = []
rejected_payments = []

valid_ride_ids = set()
valid_driver_ids = set()

    #cleaning drivers data
for driver in drivers_data:
    driver_id = driver['driver_id']
    name = driver['name'].strip().upper()
    city = driver['city'].strip().upper()
    
    if name == '':
        rejected_drivers.append({
            "record": driver,
            "rejection_reason": "Empty_name"
        })
        continue
    if city == '':
        rejected_drivers.append({
            "record": driver,
            "rejection_reason": "Empty_city"
        })
        continue
    clean_line = (driver_id, name, city)
    clean_drivers.append(clean_line)
    valid_driver_ids.add(driver_id)

    #cleaning rides data
for ride in rides_data:
    try:
        ride_id = int(ride['ride_id'])
        driver_id = int(ride['driver_id'])
        distance_km = int(ride['distance_km'])
        fare = int(ride['fare'])
    except ValueError:
        rejected_rides.append({
            "record": ride,
            "rejection_reason": "Value_error"
        })
        continue

    if distance_km <= 0:
        rejected_rides.append({
            "record": ride,
            "rejection_reason": "Invalid_distance"
        })
        continue
    if driver_id not in valid_driver_ids:
        rejected_rides.append({
            "record": ride,
            "rejection_reason": "Invalid_driver_id"
        })
        continue
    clean_line = (ride_id, driver_id, distance_km, fare)
    valid_ride_ids.add(ride_id)
    clean_rides.append(clean_line)

    #cleaning payments data
for payment in payments_data:
    try:
        payment_id = int(payment[0])
        ride_id = int(payment[1])
        method = payment[2].strip().upper()
        status = payment[3].strip().lower()
    except ValueError:
        rejected_payments.append({
            "record": payment,
            "rejection_reason": "Value_error"
        })
        continue

    if status != 'completed':
        rejected_payments.append({
            "record": payment,
            "rejection_reason": "Invalid_status"
        })
        continue
    if ride_id not in valid_ride_ids:
        rejected_payments.append({
            "record": payment,
            "rejection_reason": "Invalid_ride_id"
        })
        continue
    clean_line = (payment_id, ride_id, method, status)
    clean_payments.append(clean_line)

#L - Load phase
    #loading rejected data into a json file
rejected_data = {
    "Rejected_drivers_data": rejected_drivers,
    "Rejected_rides_data": rejected_rides,
    "Rejected_payments_data": rejected_payments
}

with open('rejected_data.json', 'w') as file:
    json.dump(rejected_data, file, indent=4)

    #loading clean data in SQL Server
driver_name = 'SQL SERVER'
server_name = 'TUF-PC\SQLEXPRESS'
database_name = 'RideSharingPipeline'
connection_string = f"""
    DRIVER={driver_name};SERVER={server_name};DATABASE={database_name};
    Trusted_Connection=yes;
"""

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

    #drop tables if they are already exist
cursor.execute("IF OBJECT_ID('payments', 'U') IS NOT NULL DROP TABLE payments")
cursor.execute("IF OBJECT_ID('rides', 'U') IS NOT NULL DROP TABLE rides")
cursor.execute("IF OBJECT_ID('drivers', 'U') IS NOT NULL DROP TABLE drivers")
conn.commit()

    #SQL Server tables creation
cursor.execute('''
IF OBJECT_ID('drivers', 'U') IS NULL
CREATE TABLE drivers(
    driver_id INT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    city VARCHAR(20) NOT NULL
)
''')

cursor.execute('''
IF OBJECT_ID('rides', 'U') IS NULL
CREATE TABLE rides(
    ride_id INT PRIMARY KEY,
    driver_id INT NOT NULL,
    distance_km INT NOT NULL,
    fare INT NOT NULL,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
)
''')

cursor.execute('''
IF OBJECT_ID('payments', 'U') IS NULL
CREATE TABLE payments(
    payment_id INT PRIMARY KEY,
    ride_id INT NOT NULL,
    method VARCHAR(10) NOT NULL,
    status VARCHAR(10) NOT NULL,
    FOREIGN KEY (ride_id) REFERENCES rides(ride_id)
)
''')
conn.commit()

    #inserting clean data into SQL Server tables
cursor.executemany(
    'INSERT INTO drivers(driver_id, name, city) VALUES(?, ?, ?)',
    clean_drivers
)

cursor.executemany(
    'INSERT INTO rides(ride_id, driver_id, distance_km, fare) VALUES(?, ?, ?, ?)',
    clean_rides
)

cursor.executemany(
    'INSERT INTO payments(payment_id, ride_id, method, status) VALUES(?, ?, ?, ?)',
    clean_payments
)
conn.commit()
conn.close
