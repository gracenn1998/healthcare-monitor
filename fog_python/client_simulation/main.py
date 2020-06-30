# msg = "Hello world"
# print(msg)

import psycopg2
import config
from datetime import datetime
import time
import paho.mqtt.client as mqtt 
import json



params = config.configDTB()
conn = psycopg2.connect(**params)
reqCnt = {}
#need fix later
reqCnt["1"] = 0
ir = {}
peakAnalyze= {}

# def on_message(client, userdata, message):



if __name__ == '__main__':
    clientName = "simulatedC1"
    params = config.configMQTT()
    client = mqtt.Client(clientName)
    pubChannel = "/monitor/request/" + clientName 
    client.connect(params['host'])
    # client.on_message = on_message
    # client.subscribe("/pulseoximeter")
    # client.subscribe("/monitor/request")
    cur = conn.cursor()
    pre_signal = 0
    signal = 0
    preTime = time.time()
    
    cnt =0
    while 1 :
        client.loop_start()
        read_sql = """ SELECT value->'ir'
                            FROM sensor_reading
                            WHERE device_id = 1
                            ORDER BY TIME DESC LIMIT 1
        """
        # try:
        cur.execute(read_sql)
        row = cur.fetchone()
        
        client.publish(pubChannel, "beep")
        now = time.time()
        
        client.loop_stop()
        
        

    