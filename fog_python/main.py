# msg = "Hello world"
# print(msg)

import psycopg2
import config
from datetime import datetime
import time
import paho.mqtt.client as mqtt 
import json
import peak_cnt2
import peak_rt



params = config.configDTB()
conn = psycopg2.connect(**params)
reqCnt = {}
#need fix later
reqCnt["1"] = 0
ir = {}
peakAnalyze= {}

def on_message(client, userdata, message):
    
    
    if(message.topic == "/pulseoximeter"):
        mes = json.loads(message.payload.decode("utf-8"))
        did = mes['did']
        pid = '1'  #mes['pid'] or get data from somewhere else?
        sensor_type = mes['stype']
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
        print(message.payload.decode("utf-8"))
        mes = json.loads(message.payload.decode("utf-8"))
        request = json.dumps(mes['req'])
        target = json.dumps(mes['targetID'])
        # print('target: ', target)
        #if request == on -> reqCnt[target]++
        if(request == "\"on\""):
            try:
                reqCnt[target]+=1
            except KeyError:
                reqCnt[target] = 1
            if(reqCnt[target]==1): #init data
                cur = conn.cursor()
                read_sql = """ SELECT value->'ir'
                                FROM sensor_reading
                                WHERE time >= NOW() - interval '5 seconds'
                """
                # try:
                cur.execute(read_sql)
                rows = cur.fetchall()
                ir = []
                if(cur.rowcount<30) :
                    for i in range(0,(30 - cur.rowcount)):
                        ir.append(0)
                for row in rows:
                    ir.append(row[0])
                cur.close()
                # except (Exception, psycopg2.DatabaseError) as error:
                #     print(error)
                
                peakAnalyze[target] = peak_rt.real_time_peak_detection(ir, 30, 2.5, 0.5)
                print('peak arr: ', peakAnalyze)
        #if(reqCnt[target] > 0) : call publish function(-> call analyze function?) in main
        if(request == "\"off\""):
            reqCnt[target]-=1
            #if(reqCnt==0): remove target pointer? 
            


if __name__ == '__main__':
    params = config.configMQTT()
    client = mqtt.Client("test")
    client.connect(params['host'])
    client.on_message = on_message
    client.subscribe("/pulseoximeter")
    client.subscribe("/monitor/request")
    cur = conn.cursor()
    pre_signal = 0
    signal = 0
    preTime = time.time()
    
    cnt =0
    while 1 :
        client.loop_start()
        for target in peakAnalyze:
            read_sql = """ SELECT value->'ir'
                            FROM sensor_reading
                            WHERE device_id = 1
                            ORDER BY TIME DESC LIMIT 1
            """
        # try:
            cur.execute(read_sql)
            row = cur.fetchone()
            # print(row)
            signal = peakAnalyze[target].thresholding_algo(row[0])
            pubChannel = "/monitor/response/" + target.replace("\"", '')
            if(signal==1):
                if(pre_signal == 0):
                    cnt+=1
                    client.publish(pubChannel, "beep")
            pre_signal = signal
                # cur.close()
            # except (Exception, psycopg2.DatabaseError) as error:
            #     print(error)
            #     print('ten ten')
            now = time.time()
            # if(now<time) now = time
            # print('??: ',now - time)
            if(now - preTime >= 5): 
                print('cnt:' , cnt)
                preTime = now
                avgBPM = (cnt/5)*60
                cnt = 0
                client.publish(pubChannel, int(avgBPM))

        # signals = peak_cnt2.peak_detection_smoothed_zscore_v2(ir, 30, 2.5, 0.5)["signals"]
        # print(signals)
        # for res in signals:
        #     if(res==1):
        #         if(pre_res == 0):
        #             cnt+=1
        #         pre_res = 1    
        #     else: pre_res = 0
        # print('peaks: ', cnt)
        
        client.loop_stop()
        
        

    