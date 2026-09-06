#include "Arduino.h"
#include "RFID.h"

// The ATmega32U4 brings hardware SPI out only on the ICSP header, so the driver
// bit-bangs the bus on these ordinary digital pins instead.
#define RFID_PIN_RST   2
#define RFID_PIN_SDA   10
#define RFID_PIN_SCK   7
#define RFID_PIN_MOSI  8
#define RFID_PIN_MISO  9

RFID rfid(RFID_PIN_SDA, RFID_PIN_RST, RFID_PIN_SCK, RFID_PIN_MOSI, RFID_PIN_MISO);

void setup()
{
    Serial.begin(115200);
    while (!Serial);
    Serial.println("start");
    rfid.init();
}

void loop()
{
    String rfidtag = rfid.readTag();
    if (rfidtag != "None") {
        Serial.println(rfidtag);
        delay(500);
    }
}
