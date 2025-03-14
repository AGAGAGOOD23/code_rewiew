import sqlite3
from datetime import datetime


def get_all_stops():
    conn = sqlite3.connect('bus_schedule.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM stops')
    stops = cursor.fetchall()
    conn.close()

    return [stop[0] for stop in stops]


def get_schedule_for_stop(selected_stop):
    conn = sqlite3.connect('bus_schedule.db')
    cursor = conn.cursor()


    current_time = datetime.now().strftime('%H:%M')

    cursor.execute('''
        SELECT schedule.time
        FROM schedule
        JOIN stops ON schedule.stop_id = stops.id
        WHERE stops.name = ? AND schedule.time > ?
        ORDER BY schedule.time
    ''', (selected_stop, current_time))

    data = cursor.fetchall()
    conn.close()


    schedule = [time[0] for time in data]
    if schedule:
        first_ride_time = schedule[0]
        time_left = calculate_time_difference(first_ride_time)
    else:
        first_ride_time = None
        time_left = None

    return {
        "schedule": schedule,
        "first_ride_time": first_ride_time,
        "time_left": time_left
    }


def calculate_time_difference(first_ride_time):

    current_time = datetime.now()
    first_ride_time_obj = datetime.strptime(first_ride_time, '%H:%M')


    time_diff = first_ride_time_obj - current_time
    if time_diff.total_seconds() < 0:
        return None

    minutes_left = time_diff.total_seconds() // 60
    hours_left = minutes_left // 60
    minutes_left = minutes_left % 60

    return f"{int(hours_left)} ч. {int(minutes_left)} мин."

def create_tables():
    conn = sqlite3.connect('bus_schedule.db')
    cursor = conn.cursor()


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stop_id INTEGER,
            time TEXT,
            FOREIGN KEY (stop_id) REFERENCES stops (id)
        )
    ''')

    conn.commit()
    conn.close()



def insert_stops(stops):
    conn = sqlite3.connect('bus_schedule.db')
    cursor = conn.cursor()

    for stop in stops:
        cursor.execute('INSERT OR IGNORE INTO stops (name) VALUES (?)', (stop,))

    conn.commit()
    conn.close()



def insert_schedule(schedule):
    conn = sqlite3.connect('bus_schedule.db')
    cursor = conn.cursor()


    for row in schedule:
        stop_name = row[0]
        times = row[1:]

        cursor.execute('SELECT id FROM stops WHERE name = ?', (stop_name,))
        stop_id = cursor.fetchone()

        if stop_id:
            stop_id = stop_id[0]
            for time in times:
                cursor.execute('INSERT INTO schedule (stop_id, time) VALUES (?, ?)', (stop_id, time))

    conn.commit()
    conn.close()
