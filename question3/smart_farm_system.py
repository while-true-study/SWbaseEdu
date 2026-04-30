#!/usr/bin/env python3
'''Smart farm sensor, queue, and MySQL storage system.

Requirements addressed:
1. ParmSensor class with random sensor values.
2. Five sensor instances running on separate threads every 10 seconds.
3. FIFO queue named sensorQ.
4. Separate database writer thread polling the queue every second.
5. MySQL table creation, insert, and select helpers.
6. Hourly average temperature graph using only the standard library.

Important constraint note:
- External Python packages are not used.
- MySQL access is performed through the mysql command line client via subprocess.
- Therefore mysql CLI must be installed and available in PATH.
'''

from __future__ import annotations

import collections
import datetime
import math
import subprocess
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional


DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '1234',
    'database': 'smart_farm',
}

SENSOR_INTERVAL_SECONDS = 10
QUEUE_POLL_INTERVAL_SECONDS = 1
SENSOR_COUNT = 5
RUN_DURATION_SECONDS = 60


@dataclass
class SensorRecord:
    '''Single sensor data record.'''

    sensor_name: str
    input_time: datetime.datetime
    temperature: int
    illuminance: int
    humidity: int


class ParmSensor:
    '''Smart farm sensor.'''

    def __init__(self, sensor_name: str) -> None:
        self.sensor_name = sensor_name
        self.temperature = 0
        self.illuminance = 0
        self.humidity = 0
        self._lock = threading.Lock()

    def set_data(self) -> None:
        '''Fill sensor properties with random values in the required ranges.'''
        with self._lock:
            import random
            self.temperature = random.randint(20, 30)
            self.illuminance = random.randint(5000, 10000)
            self.humidity = random.randint(40, 70)

    def get_data(self) -> Dict[str, int]:
        '''Return current sensor values.'''
        with self._lock:
            return {
                'temperature': self.temperature,
                'illuminance': self.illuminance,
                'humidity': self.humidity,
            }

    def SetData(self) -> None:  # noqa: N802
        self.set_data()

    def GetData(self) -> Dict[str, int]:  # noqa: N802
        return self.get_data()


class SensorQueue:
    '''Thread-safe FIFO queue.'''

    def __init__(self) -> None:
        self._items: Deque[SensorRecord] = collections.deque()
        self._condition = threading.Condition()

    def enqueue(self, item: SensorRecord) -> None:
        with self._condition:
            self._items.append(item)
            self._condition.notify()

    def dequeue(self) -> Optional[SensorRecord]:
        with self._condition:
            if not self._items:
                return None
            return self._items.popleft()

    def size(self) -> int:
        with self._condition:
            return len(self._items)

    def is_empty(self) -> bool:
        with self._condition:
            return not self._items


class MemoryFrame:
    '''Simple in-memory table-like structure for the bonus requirement.'''

    def __init__(self) -> None:
        self._rows: List[Dict[str, object]] = []
        self._lock = threading.Lock()

    def add_row(self, record: SensorRecord) -> None:
        with self._lock:
            self._rows.append(
                {
                    'sensor_name': record.sensor_name,
                    'input_time': record.input_time,
                    'temperature': record.temperature,
                    'illuminance': record.illuminance,
                    'humidity': record.humidity,
                }
            )

    def get_five_minute_averages(self) -> List[Dict[str, object]]:
        buckets: Dict[tuple, Dict[str, int]] = {}
        with self._lock:
            rows_copy = list(self._rows)

        for row in rows_copy:
            row_time = row['input_time']
            bucket_minute = (row_time.minute // 5) * 5
            bucket_time = row_time.replace(
                minute = bucket_minute,
                second = 0,
                microsecond = 0,
            )
            key = (row['sensor_name'], bucket_time)
            if key not in buckets:
                buckets[key] = {
                    'count': 0,
                    'temperature_sum': 0,
                    'illuminance_sum': 0,
                    'humidity_sum': 0,
                }
            buckets[key]['count'] += 1
            buckets[key]['temperature_sum'] += int(row['temperature'])
            buckets[key]['illuminance_sum'] += int(row['illuminance'])
            buckets[key]['humidity_sum'] += int(row['humidity'])

        averages = []
        for (sensor_name, bucket_time), value in sorted(buckets.items()):
            count = value['count']
            averages.append(
                {
                    'sensor_name': sensor_name,
                    'bucket_time': bucket_time,
                    'avg_temperature': value['temperature_sum'] / count,
                    'avg_illuminance': value['illuminance_sum'] / count,
                    'avg_humidity': value['humidity_sum'] / count,
                    'count': count,
                }
            )
        return averages


def get_mysql_command(database: Optional[str] = None) -> List[str]:
    command = [
        'mysql',
        f"--host={DB_CONFIG['host']}",
        f"--port={DB_CONFIG['port']}",
        f"--user={DB_CONFIG['user']}",
        f"--password={DB_CONFIG['password']}",
        '--default-character-set=utf8mb4',
        '--batch',
        '--raw',
        '--silent',
    ]
    if database:
        command.append(database)
    return command


def run_mysql(sql: str, database: Optional[str] = None) -> str:
    try:
        completed = subprocess.run(
            get_mysql_command(database),
            input = sql,
            capture_output = True,
            text = True,
            check = True,
        )
        return completed.stdout.strip()
    except FileNotFoundError as exc:
        raise RuntimeError(
            'mysql command not found. Install MySQL client and add it to PATH.'
        ) from exc
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or 'Unknown MySQL error'
        raise RuntimeError(message) from exc


def initialize_database() -> None:
    sql = (
        'CREATE DATABASE IF NOT EXISTS smart_farm '
        'CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
    )
    run_mysql(sql)


def create_table_if_not_exists() -> None:
    sql = '''
    CREATE TABLE IF NOT EXISTS parm_data (
        id INT NOT NULL AUTO_INCREMENT,
        input_time DATETIME NOT NULL,
        sensor_name VARCHAR(30) NOT NULL,
        temperature INT NOT NULL,
        illuminance INT NOT NULL,
        humidity INT NOT NULL,
        PRIMARY KEY (id)
    );
    '''
    run_mysql(sql, DB_CONFIG['database'])


def escape_sql_string(value: str) -> str:
    return value.replace('\\', '\\\\').replace("'", "\\'")


def insert_sensor_data(
    input_time: datetime.datetime,
    sensor_name: str,
    temperature: int,
    illuminance: int,
    humidity: int,
) -> None:
    sql = f'''
    INSERT INTO parm_data (
        input_time,
        sensor_name,
        temperature,
        illuminance,
        humidity
    ) VALUES (
        '{escape_sql_string(input_time.strftime('%Y-%m-%d %H:%M:%S'))}',
        '{escape_sql_string(sensor_name)}',
        {temperature},
        {illuminance},
        {humidity}
    );
    '''
    run_mysql(sql, DB_CONFIG['database'])


def get_sensor_data() -> List[SensorRecord]:
    sql = '''
    SELECT
        sensor_name,
        DATE_FORMAT(input_time, '%Y-%m-%d %H:%i:%s'),
        temperature,
        illuminance,
        humidity
    FROM parm_data
    ORDER BY input_time ASC, id ASC;
    '''
    output = run_mysql(sql, DB_CONFIG['database'])
    records: List[SensorRecord] = []
    if not output:
        return records

    for line in output.splitlines():
        parts = line.split('\t')
        if len(parts) != 5:
            continue
        sensor_name, input_time_text, temp, light, humi = parts
        input_time = datetime.datetime.strptime(
            input_time_text,
            '%Y-%m-%d %H:%M:%S',
        )
        records.append(
            SensorRecord(
                sensor_name = sensor_name,
                input_time = input_time,
                temperature = int(temp),
                illuminance = int(light),
                humidity = int(humi),
            )
        )
    return records


def get_sensor_counts_by_sensor() -> Dict[str, int]:
    sql = '''
    SELECT sensor_name, COUNT(*)
    FROM parm_data
    GROUP BY sensor_name
    ORDER BY sensor_name;
    '''
    output = run_mysql(sql, DB_CONFIG['database'])
    result: Dict[str, int] = {}
    if not output:
        return result

    for line in output.splitlines():
        sensor_name, count_text = line.split('\t')
        result[sensor_name] = int(count_text)
    return result


def get_hourly_average_data() -> Dict[str, List[Dict[str, object]]]:
    records = get_sensor_data()
    grouped: Dict[tuple, Dict[str, object]] = {}

    for record in records:
        hour_time = record.input_time.replace(
            minute = 0,
            second = 0,
            microsecond = 0,
        )
        key = (record.sensor_name, hour_time)
        if key not in grouped:
            grouped[key] = {
                'count': 0,
                'temperature_sum': 0,
                'has_humidity_over_90': False,
            }
        grouped[key]['count'] += 1
        grouped[key]['temperature_sum'] += record.temperature
        if record.humidity > 90:
            grouped[key]['has_humidity_over_90'] = True

    result: Dict[str, List[Dict[str, object]]] = {}
    for (sensor_name, hour_time), value in sorted(grouped.items()):
        if sensor_name not in result:
            result[sensor_name] = []
        result[sensor_name].append(
            {
                'hour_time': hour_time,
                'avg_temperature': value['temperature_sum'] / value['count'],
                'has_humidity_over_90': value['has_humidity_over_90'],
            }
        )
    return result


def print_five_minute_averages(memory_frame: MemoryFrame) -> None:
    averages = memory_frame.get_five_minute_averages()
    if not averages:
        print('No five-minute average data available.')
        return

    print('\n[5-minute averages]')
    for row in averages:
        print(
            f"{row['bucket_time']} {row['sensor_name']} - "
            f"avg_temp {row['avg_temperature']:.2f}, "
            f"avg_light {row['avg_illuminance']:.2f}, "
            f"avg_humi {row['avg_humidity']:.2f}, "
            f"count {row['count']}"
        )


def print_sensor_counts() -> None:
    counts = get_sensor_counts_by_sensor()
    if not counts:
        print('No sensor data count found in DB.')
        return

    print('\n[DB row count by sensor]')
    for sensor_name, count in counts.items():
        print(f'{sensor_name}: {count}')


def draw_hourly_temperature_graph() -> None:
    grouped = get_hourly_average_data()
    if not grouped:
        print('No database data available to draw a graph.')
        return

    all_points = []
    for sensor_rows in grouped.values():
        for row in sensor_rows:
            all_points.append(row)

    min_time = min(row['hour_time'] for row in all_points)
    max_time = max(row['hour_time'] for row in all_points)
    min_temp = min(float(row['avg_temperature']) for row in all_points)
    max_temp = max(float(row['avg_temperature']) for row in all_points)

    if math.isclose(min_temp, max_temp):
        min_temp -= 1
        max_temp += 1

    width = 1000
    height = 600
    padding = 60

    root = tk.Tk()
    root.title('Hourly Average Temperature by Sensor')
    canvas = tk.Canvas(root, width = width, height = height, bg = 'white')
    canvas.pack()

    canvas.create_line(
        padding,
        height - padding,
        width - padding,
        height - padding,
    )
    canvas.create_line(padding, padding, padding, height - padding)

    time_range = max((max_time - min_time).total_seconds(), 1)
    temp_range = max_temp - min_temp

    def to_x(value: datetime.datetime) -> float:
        seconds = (value - min_time).total_seconds()
        return padding + (seconds / time_range) * (width - (padding * 2))

    def to_y(value: float) -> float:
        return height - padding - ((value - min_temp) / temp_range) * (
            height - (padding * 2)
        )

    for step in range(6):
        temp_value = min_temp + (temp_range / 5) * step
        y = to_y(temp_value)
        canvas.create_line(padding - 5, y, padding, y)
        canvas.create_text(
            padding - 30,
            y,
            text = f'{temp_value:.1f}',
            anchor = 'e',
        )

    for index, sensor_name in enumerate(sorted(grouped.keys())):
        rows = grouped[sensor_name]
        previous = None
        for row in rows:
            x = to_x(row['hour_time'])
            y = to_y(float(row['avg_temperature']))
            if previous is not None:
                canvas.create_line(previous[0], previous[1], x, y, width = 2)
            point_radius = 4
            fill_color = 'red' if row['has_humidity_over_90'] else 'black'
            canvas.create_oval(
                x - point_radius,
                y - point_radius,
                x + point_radius,
                y + point_radius,
                fill = fill_color,
            )
            previous = (x, y)

        legend_y = padding + (index * 20)
        canvas.create_line(width - 180, legend_y, width - 150, legend_y, width = 2)
        canvas.create_text(width - 140, legend_y, text = sensor_name, anchor = 'w')

    unique_times = sorted({row['hour_time'] for row in all_points})
    for value in unique_times:
        x = to_x(value)
        canvas.create_line(x, height - padding, x, height - padding + 5)
        canvas.create_text(
            x,
            height - padding + 20,
            text = value.strftime('%m-%d %H:%M'),
            anchor = 'n',
            angle = 30,
        )

    root.mainloop()


def safe_draw_hourly_temperature_graph() -> None:
    try:
        draw_hourly_temperature_graph()
    except tk.TclError:
        print('GUI environment not available. Printing hourly averages instead.')
        grouped = get_hourly_average_data()
        for sensor_name, rows in grouped.items():
            print(f'[{sensor_name}]')
            for row in rows:
                flag = ' (humidity > 90)' if row['has_humidity_over_90'] else ''
                print(
                    f"{row['hour_time']}: avg_temp "
                    f"{row['avg_temperature']:.2f}{flag}"
                )


def sensor_worker(
    sensor: ParmSensor,
    sensor_queue: SensorQueue,
    memory_frame: MemoryFrame,
    stop_event: threading.Event,
) -> None:
    while not stop_event.is_set():
        sensor.set_data()
        values = sensor.get_data()
        input_time = datetime.datetime.now()
        record = SensorRecord(
            sensor_name = sensor.sensor_name,
            input_time = input_time,
            temperature = values['temperature'],
            illuminance = values['illuminance'],
            humidity = values['humidity'],
        )
        memory_frame.add_row(record)
        sensor_queue.enqueue(record)
        print(
            f"{input_time.strftime('%Y-%m-%d %H:%M:%S')} "
            f"{sensor.sensor_name} — temp {record.temperature:02d}, "
            f"light {record.illuminance:05d}, humi {record.humidity:02d}"
        )

        if stop_event.wait(SENSOR_INTERVAL_SECONDS):
            break


def queue_db_worker(
    sensor_queue: SensorQueue,
    stop_event: threading.Event,
) -> None:
    while not stop_event.is_set() or not sensor_queue.is_empty():
        record = sensor_queue.dequeue()
        if record is None:
            time.sleep(QUEUE_POLL_INTERVAL_SECONDS)
            continue

        try:
            insert_sensor_data(
                input_time = record.input_time,
                sensor_name = record.sensor_name,
                temperature = record.temperature,
                illuminance = record.illuminance,
                humidity = record.humidity,
            )
            print(
                f"DB inserted: {record.input_time.strftime('%Y-%m-%d %H:%M:%S')} "
                f"{record.sensor_name} (queue size: {sensor_queue.size()})"
            )
        except RuntimeError as exc:
            print(f'DB insert failed: {exc}')
            time.sleep(QUEUE_POLL_INTERVAL_SECONDS)


def run_sensor_system(run_duration_seconds: int = RUN_DURATION_SECONDS) -> None:
    initialize_database()
    create_table_if_not_exists()

    stop_event = threading.Event()
    memory_frame = MemoryFrame()
    sensorQ = SensorQueue()
    sensors = [ParmSensor(f'Parm{i}') for i in range(1, SENSOR_COUNT + 1)]
    threads = []

    db_thread = threading.Thread(
        target = queue_db_worker,
        args = (sensorQ, stop_event),
        daemon = True,
        name = 'db-writer-thread',
    )
    db_thread.start()
    threads.append(db_thread)

    for sensor in sensors:
        thread = threading.Thread(
            target = sensor_worker,
            args = (sensor, sensorQ, memory_frame, stop_event),
            daemon = True,
            name = f'{sensor.sensor_name}-thread',
        )
        thread.start()
        threads.append(thread)

    try:
        time.sleep(run_duration_seconds)
    finally:
        stop_event.set()
        for thread in threads:
            thread.join(timeout = 3)

    print_five_minute_averages(memory_frame)
    print_sensor_counts()
    safe_draw_hourly_temperature_graph()


def main() -> None:
    run_sensor_system()


if __name__ == '__main__':
    main()
