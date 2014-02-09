#include <PS2X_lib.h>  //for v1.6
#include <Wire.h>

float forwards = 0;
float sideways = 0;
byte highX = B00100000;
byte highY = B00100000;
byte lowX, lowY;
byte xCmd, yCmd;

const byte dacRadius = 54;
const byte up4mask = B11110000;
byte f;
byte n;

byte addr = B0001101;

/******************************************************************
 * set pins connected to PS2 controller:
 *   - 1e column: original 
 *   - 2e colmun: Stef?
 * replace pin numbers by the ones you use
 ******************************************************************/
#define PS2_DAT        3  //14    
#define PS2_CMD        4  //15
#define PS2_SEL        5  //16
#define PS2_CLK        6  //17

/******************************************************************
 * select modes of PS2 controller:
 *   - pressures = analog reading of push-butttons 
 *   - rumble    = motor rumbling
 * uncomment 1 of the lines for each mode selection
 ******************************************************************/
//#define pressures   true
#define pressures   false
//#define rumble      true
#define rumble      false

PS2X ps2x; // create PS2 Controller Class

//right now, the library does NOT support hot pluggable controllers, meaning 
//you must always either restart your Arduino after you connect the controller, 
//or call config_gamepad(pins) again after connecting the controller.

int error = 0;
byte type = 0;
byte vibrate = 0;

void setup(){
 
  Serial.begin(57600);
  Wire.begin();
  
  delay(300);  //added delay to give wireless ps2 module some time to startup, before configuring it
     f= setZero();
  if (f != 0){
    n = 0;
    while(n<f){

      digitalWrite(13,HIGH);
      delay(300);
      digitalWrite(13,LOW);
      n++;
    }
  }
  //CHANGES for v1.6 HERE!!! **************PAY ATTENTION*************
  
  //setup pins and settings: GamePad(clock, command, attention, data, Pressures?, Rumble?) check for error
  error = ps2x.config_gamepad(PS2_CLK, PS2_CMD, PS2_SEL, PS2_DAT, pressures, rumble);
  
  if(error == 0){
    Serial.print("Found Controller, configured successful ");
    Serial.print("pressures = ");
	if (pressures)
	  Serial.println("true ");
	else
	  Serial.println("false");
	Serial.print("rumble = ");
	if (rumble)
	  Serial.println("true)");
	else
	  Serial.println("false");
    Serial.println("Try out all the buttons, X will vibrate the controller, faster as you press harder;");
    Serial.println("holding L1 or R1 will print out the analog stick values.");
    Serial.println("Note: Go to www.billporter.info for updates and to report bugs.");
  }  
  else if(error == 1)
    Serial.println("No controller found, check wiring, see readme.txt to enable debug. visit www.billporter.info for troubleshooting tips");
   
  else if(error == 2)
    Serial.println("Controller found but not accepting commands. see readme.txt to enable debug. Visit www.billporter.info for troubleshooting tips");

  else if(error == 3)
    Serial.println("Controller refusing to enter Pressures mode, may not support it. ");
  
//  Serial.print(ps2x.Analog(1), HEX);
  
  type = ps2x.readType(); 
  switch(type) {
    case 0:
      Serial.print("Unknown Controller type found ");
      break;
    case 1:
      Serial.print("DualShock Controller found ");
      break;
    case 2:
      Serial.print("GuitarHero Controller found ");
      break;
	case 3:
      Serial.print("Wireless Sony DualShock Controller found ");
      break;
   }
}

void loop() {
  /* You must Read Gamepad to get new values and set vibration values
     ps2x.read_gamepad(small motor on/off, larger motor strenght from 0-255)
     if you don't enable the rumble, use ps2x.read_gamepad(); with no values
     You should call this at least once a second
   */  
  if(error == 1) //skip loop if no controller found
    return; 
  else { //DualShock Controller
    ps2x.read_gamepad(false, vibrate); //read controller and set large motor to spin at 'vibrate' speed
    if(ps2x.Button(PSB_L1) || ps2x.Button(PSB_R1)) { //print stick values if either is TRUE
      Serial.println(ps2x.Analog(PSS_LX), DEC); 
      
      Serial.println(ps2x.Analog(PSS_RY), DEC); 

      sideways = -ps2x.Analog(PSS_LX)+127;
      forwards = ps2x.Analog(PSS_RY)-127;
      setMotors();
    }     
  }
  delay(50);  
}


int setZero(){
  Wire.beginTransmission(addr);
  Wire.write(B00001111);  //All 4 DACs can be set to the same thing with one command (these bits are to set DACs D, C, B, A)
  Wire.write(B00100111);  //Set them to "off" which means the stick is in the middle so all are at 2.5v
  Wire.write(B11111100);
  return Wire.endTransmission();
}

void setMotors(){
  cleanInputs();
  setX();
  setY();
}

void cleanInputs(){
  if(abs(forwards)<5){
    forwards = 0;
  }
  forwards = constrain(forwards, -dacRadius, dacRadius);

  if(abs(sideways)<5){
    sideways = 0;
  }
  sideways = constrain(sideways, -dacRadius, dacRadius);
}

int setX(){
  xCmd = byte(125.0+sideways);
  highX = ((highX&up4mask)|(xCmd>>4));
  lowX = xCmd<<4;
  Wire.beginTransmission(addr);
  Wire.write(B00000001);
  Wire.write(highX);
  Wire.write(lowX);
  return Wire.endTransmission();
}

int setY(){
  yCmd = byte(125.0+forwards);
  highY = ((highY&up4mask)|(yCmd>>4));
  lowY = yCmd<<4;
  Wire.beginTransmission(addr);
  Wire.write(B00000100);
  Wire.write(highY);
  Wire.write(lowY);
  return Wire.endTransmission();
}
