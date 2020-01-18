#include <M5Stack.h> 
#include <Wire.h> 
#include "Ambient.h"
#include "MAX30100.h"

// Sampling is tightly related to the dynamic range of the ADC.
// refer to the datasheet for further info
#define SAMPLING_RATE                       MAX30100_SAMPRATE_100HZ

// The LEDs currents must be set to a level that avoids clipping and maximises the
// dynamic range
#define IR_LED_CURRENT                      MAX30100_LED_CURR_50MA
#define RED_LED_CURRENT                     MAX30100_LED_CURR_27_1MA

// The pulse width of the LEDs driving determines the resolution of
// the ADC (which is a Sigma-Delta).
// set HIGHRES_MODE to true only when setting PULSE_WIDTH to MAX30100_SPC_PW_1600US_16BITS
#define PULSE_WIDTH                         MAX30100_SPC_PW_1600US_16BITS
#define HIGHRES_MODE                        true


// Instantiate a MAX30100 sensor class
MAX30100 sensor;

#define REPORTING_PERIOD_MS     6000

uint32_t tsLastReport = 0;
#define PERIOD 60

WiFiClient client;
Ambient ambient;

const  char * ssid = "A" ; 
const  char * password = "cfkx3236" ; 

unsigned  int channelId = 17905; // Channel ID of Ambient 
const  char * writeKey = "c2b5ad3f77c39350" ; // Light key 
int number = 1 ;
 unsigned  long t;
 void setup () {
    M5.begin ();
    Wire.begin (); // Initialize I2C 
    Serial.begin (115200);
    delay ( 100 );
    

    M5.Lcd.println( "\r\n M5Stack + BME280-> Ambient test" );

    WiFi.begin(ssid, password);   // Connect to Wi-Fi AP 
    while (WiFi.status()!= WL_CONNECTED) {   // Wait for Wi-Fi AP connection 
        delay ( 100 );
    }

//    M5.Lcd.print ( "WiFi connected\r\n IP address:" );
//    M5.Lcd.print (WiFi.localIP());

    ambient.begin (channelId, writeKey, & client); // Initialize Ambient by specifying channel ID and write key
    if (!sensor.begin()) {
        Serial.println("FAILED");
        for(;;);
    } else {
        Serial.println("SUCCESS");
    }
    sensor.setMode(MAX30100_MODE_SPO2_HR);
    sensor.setLedsCurrent(IR_LED_CURRENT, RED_LED_CURRENT);
    sensor.setLedsPulseWidth(PULSE_WIDTH);
    sensor.setSamplingRate(SAMPLING_RATE);
    sensor.setHighresModeEnabled(HIGHRES_MODE);
}

void loop () {
  uint16_t ir, red;

  sensor.update();

  while (sensor.getRawValues(&ir, &red)) {
      Serial.print(ir);
      Serial.print('\t');
      Serial.println(red);
  }
  if (millis() - tsLastReport > REPORTING_PERIOD_MS) {
    number = (number + 1 )% 10 ;
//        ambient.set ( 1 , number);
//        ambient.send ();
        M5.Lcd.println (number);
//        Serial.print("Heart rate:");
//        Serial.print(pox.getHeartRate());
//        Serial.print("bpm / SpO2:");
//        Serial.print(pox.getSpO2());
//        Serial.println("%");

        tsLastReport = millis();
  }
    
//    delay ( 6000 );
}

//void loop()
//{
//    uint16_t ir, red;
//
//    sensor.update();
//
//    while (sensor.getRawValues(&ir, &red)) {
//        Serial.print(ir);
//        Serial.print('\t');
//        Serial.println(red);
//    }
//}
