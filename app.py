from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)


def get_stops():
    conn = sqlite3.connect('bus_schedule.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM stops')
    stops = cursor.fetchall()
    conn.close()

    return [stop[0] for stop in stops]

def get_nearby_schedule_for_stop(selected_stop):
    conn = sqlite3.connect('bus_schedule.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT schedule.time
        FROM schedule
        JOIN stops ON schedule.stop_id = stops.id
        WHERE stops.name = ?
        ORDER BY schedule.time
    ''', (selected_stop,))

    data = cursor.fetchall()
    conn.close()

    schedule = [time[0] for time in data]


    current_time = datetime.now().strftime('%H:%M')
    future_schedule = [ride for ride in schedule if ride > current_time]


    first_ride_time = future_schedule[0] if future_schedule else None
    time_left = calculate_time_difference(first_ride_time) if first_ride_time else None

    return {
        "schedule": future_schedule,
        "first_ride_time": first_ride_time,
        "time_left": time_left
    }


def calculate_time_difference(first_ride_time):
    current_time = datetime.now()

    first_ride_time_obj = datetime.strptime(first_ride_time, '%H:%M').replace(year=current_time.year, month=current_time.month, day=current_time.day)

    if first_ride_time_obj < current_time:
        first_ride_time_obj += timedelta(days=1)

    time_diff = first_ride_time_obj - current_time

    if time_diff.total_seconds() < 0:
        return None

    minutes_left = time_diff.total_seconds() // 60
    hours_left = minutes_left // 60
    minutes_left = minutes_left % 60

    return f"{int(hours_left)} ч. {int(minutes_left)} мин."

@app.route('/', methods=['GET', 'POST'])
def index():
    stops = get_stops()
    selected_stop = None
    schedule = []
    first_ride_time = None
    time_left = None

    if request.method == 'POST':
        selected_stop = request.form.get('stop')
        schedule_data = get_nearby_schedule_for_stop(selected_stop)
        schedule = schedule_data["schedule"]
        first_ride_time = schedule_data["first_ride_time"]
        time_left = schedule_data["time_left"]

    return render_template('schedule.html', stops=stops, schedule=schedule, selected_stop=selected_stop,
                           first_ride_time=first_ride_time, time_left=time_left)


if __name__ == '__main__':
    app.run(debug=True)
