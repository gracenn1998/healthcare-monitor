# msg = "Hello world"
# print(msg)

import psycopg2
import config
from datetime import datetime
import time
import paho.mqtt.client as mqtt 
import json
import peak_cnt2



params = config.configDTB()
conn = psycopg2.connect(**params)
reqCnt = {}
#need fix later
reqCnt["1"] = 0

def on_message(client, userdata, message):
    mes = json.loads(message.payload.decode("utf-8"))
    did = mes['did']
    pid = '1'  #mes['pid'] or get data from somewhere else?
    sensor_type = mes['stype']
    
    if(message.topic == "/pulseoximeter"):
        val_json = json.dumps(mes['val'])
        now = datetime.now()
        sql =   """ INSERT INTO sensor_reading(time, patient_id, device_id, sensortype_id, value)
                    VALUES (%s, %s, %s, %s, %s)
                """
        record = (now, pid, did, sensor_type, val_json)

        try: 
            cur = conn.cursor()
            cur.execute(sql, record)
            # time = cur.fetchone()[0]
            conn.commit()
            cur.close()
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)

    if(message.topic == "/monitor/request"):
        request = json.dumps(mes['req'])
        target = json.dumps(mes['targetID'])
        #if request == on -> reqCnt[target]++
        if(request == "on"):
            try:
                reqCnt[target]+=1
            except KeyError:
                reqCnt[target] = 0
        #if(reqCnt[target] > 0) : call publish function(-> call analyze function?) in main
            
            

ir = {}
if __name__ == '__main__':
    time = datetime.now().second
    params = config.configMQTT()
    client = mqtt.Client("test")
    client.connect(params['host'])
    client.on_message = on_message
    client.subscribe("/pulseoximeter")
    client.subscribe("/monitor/request")
    while 1 :
        client.loop_start()
        client.loop_stop()
        if(datetime.now().second - time >= 5):
            time = datetime.now().second
            cnt =0
            cur = conn.cursor()
            read_sql = """ SELECT value->'ir'
                            FROM sensor_reading
                            WHERE time >= NOW() - interval '5 seconds'
            """
            try:
                cur.execute(read_sql)
                rows = cur.fetchall()
                print('ir val cnt: ', cur.rowcount)
                # print(rows)
                # print('.')
                # print(rows[1][0])
                ir = []
                for row in rows:
                    ir.append(row[0])
                #     print(row)
                # print(ir)
                cur.close()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)


            signals = peak_cnt2.peak_detection_smoothed_zscore_v2(ir, 30, 2.5, 0.5)["signals"]
            # print(signals)
            for res in signals:
                if(res==1):
                    if(pre_res == 0):
                        cnt+=1
                    pre_res = 1    
                else: pre_res = 0
            print('peaks: ', cnt)
        
        

    