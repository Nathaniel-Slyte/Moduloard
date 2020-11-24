#if (RAMEND < 1000)
  #define SERIAL_BUFFER_SIZE 16
#else
  #define SERIAL_BUFFER_SIZE 64
#endif

#include <Muca.h>
#include <string.h>
#include <bluefruit.h>
#include <Adafruit_LittleFS.h>
#include <InternalFileSystem.h>
#include "Wire.h"

// gain 0 -> 31

Muca muca;

BLEDfu  bledfu;  // OTA DFU service
BLEDis  bledis;  // device information
BLEUart bleuart; // uart over ble
BLEBas  blebas;  // battery

#define CALIBRATION_STEPS 20
short currentCalibrationStep = 0;
unsigned int calibrationGrid[NUM_ROWS * NUM_COLUMNS];


String ID       = "BPC";
String message  = "";

void setup() {

  Serial.begin(115200);
  
  Bluefruit.begin();
  Bluefruit.setTxPower(4);    // Check bluefruit.h for supported values
  Bluefruit.setName("BPC");
  Bluefruit.Periph.setConnectCallback(connect_callback);
  Bluefruit.Periph.setDisconnectCallback(disconnect_callback);
  
  bledfu.begin();

  bledis.setManufacturer("Adafruit Industries");
  bledis.setModel("Bluefruit Feather52");
  bledis.begin();

  bleuart.begin();

  blebas.begin();
  blebas.write(100);

  startAdv();

  muca.init();
  muca.useRawData(true); // If you use the raw data, the interrupt is not working

  delay(50);
  muca.setGain(8);
}




void startAdv(void)
{
  // Advertising packet
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();

  // Include bleuart 128-bit uuid
  Bluefruit.Advertising.addService(bleuart);

  // Secondary Scan Response packet (optional)
  // Since there is no room for 'Name' in Advertising packet
  Bluefruit.ScanResponse.addName();

  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(32, 244);    // in unit of 0.625 ms
  Bluefruit.Advertising.setFastTimeout(30);      // number of seconds in fast mode
  Bluefruit.Advertising.start(0);                // 0 = Don't stop advertising after n seconds  
}

// callback invoked when central connects
void connect_callback(uint16_t conn_handle)
{
  // Get the reference to current connection
  BLEConnection* connection = Bluefruit.Connection(conn_handle);

  char central_name[32] = { 0 };
  connection->getPeerName(central_name, sizeof(central_name));

  //Serial.print("Connected to ");
  //Serial.println(central_name);
}

void disconnect_callback(uint16_t conn_handle, uint8_t reason)
{
  (void) conn_handle;
  (void) reason;
}






void ButcherByte(uint8_t rawByteValues[]){
  
  uint8_t token[20];
  uint16_t counter = 0;
  
  for (int i = 0; i < NUM_ROWS * NUM_COLUMNS ; i++) {
    token[counter] = rawByteValues[i]+1;
    //Serial.println(token[counter]);
    counter++;
    
    if (counter == 20 || i == NUM_ROWS * NUM_COLUMNS -1){
      if (counter != 20 && i == NUM_ROWS * NUM_COLUMNS -1){
        token[counter] = (0x00<<8);
        //Serial.println("0 - 0");
      }
      bleuart.write(token, 20);
      
      if (counter == 20 && i == NUM_ROWS * NUM_COLUMNS -1){
        bleuart.write((0x00<<8), 1);
        //Serial.println("0 - 1");
      }
      counter = 0;
    }  
  }
}

void GetRaw() {
  if (muca.updated()) {
    uint8_t rawByteValues[252];
    
    if (currentCalibrationStep >= CALIBRATION_STEPS) {
      // Print the array value
      for (int i = 0; i < NUM_ROWS * NUM_COLUMNS; i++) {
        if (muca.grid[i] > 0) rawByteValues[i] = (muca.grid[i] - calibrationGrid[i] ) + 20; // The +30 is to be sure it's positive
        Serial.print(muca.grid[i]);
        Serial.print(",");
      }
      Serial.println();
      ButcherByte(rawByteValues);
    }
    else { // Once the calibration is done
      //Save the grid value to the calibration array
      for (int i = 0; i < NUM_ROWS * NUM_COLUMNS; i++) {
        if (currentCalibrationStep == 0) calibrationGrid[i] = muca.grid[i]; // Copy array
        else calibrationGrid[i] = (calibrationGrid[i] + muca.grid[i]) / 2 ; // Get average
      }
        currentCalibrationStep++;
        Serial.print("Calibration performed "); Serial.print(currentCalibrationStep); Serial.print("/"); Serial.println(CALIBRATION_STEPS);
    }

  } // End Muca Updated

  delay(1);
}


void SendFalseRawByte() {
  // Print the array value
  uint8_t rawByteValues[252];
  for (int i = 0; i < NUM_ROWS * NUM_COLUMNS; i++) {
    rawByteValues[i] = byte(i); // i The +30 is to be sure it's positive
  }
  
  ButcherByte(rawByteValues);

}

void loop() {
  
  //if (muca.updated()) {
    //SendRawByte(); // Faster
    //SendRawString();  
  //}
  
  while ( bleuart.available() )
  {
    uint8_t ch;
    ch = (uint8_t) bleuart.read();
    //Serial.write(ch);
    message += (char) ch;
  }
  
  if (message != "")
  {
    Serial.println(message);
    message = "";
  }
  else
  {
    SendFalseRawByte();  
  }
  

  delay(16); // waiting 16ms for 60fps

}
