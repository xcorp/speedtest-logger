#!bin/python3

import speedtest
import json
from pprint import pprint
from influxdb import InfluxDBClient
import datetime
import time



def format_for_influx(cliout):
    data = json.loads(cliout)
    # There is additional data in the speedtest-cli output but it is likely not necessary to store.
    influx_data = [
        {
            'measurement': 'ping',
            'time': data['timestamp'],
            'fields': {
                'latency': data['ping']
            }
        },
        {
            'measurement': 'download',
            'time': data['timestamp'],
            'fields': {
                # Byte to Megabit
                'bandwidth': data['download'],
                'bytes': data['bytes_received']

            }
        },
        {
            'measurement': 'upload',
            'time': data['timestamp'],
            'fields': {
                # Byte to Megabit
                'bandwidth': data['upload'],
                'bytes': data['bytes_sent']
            }
        }
    ]

    return influx_data

def report ():
    try:
        s = speedtest.Speedtest()

        s.get_best_server()
        s.download()
        s.upload()


        result = s.results.json()
        result_dict = s.results.dict()
    except:
        
        result='{"download": 0.0, "upload": 0.0, "ping": 0.0, "bytes_received": 0, "bytes_sent": 0, "timestamp": "%s"}' % (datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

    influx_data=format_for_influx(result)


    client = InfluxDBClient(host='grafana.lan', port=8086)
    client.create_database('speedtest')

    client.switch_database('speedtest')

    client.write_points(influx_data)

    client.close()


while True:
    try:
        report()
        time.sleep(300)
        
    except:
        pass
        time.sleep(300)





