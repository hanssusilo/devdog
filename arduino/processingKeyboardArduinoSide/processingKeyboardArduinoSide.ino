#include <Wire.h>

int incomingByte; 

int v = 512;
byte addr = B0001101;
byte f;
byte n;

void setup(){
    Serial.begin(9600);
  Wire.begin();
   pinMode(13, OUTPUT);
  delay(2000);
  
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
}
void loop(){
  
  if (Serial.available() > 0) {
  setMotors(Serial.read());
  }
}

int setZero(){
  Wire.beginTransmission(addr);
  Wire.write(B00001111);  //All 4 DACs can be set to the same thing with one command (these bits are to set DACs D, C, B, A)
  Wire.write(B00100111);  //Set them to "off" which means the stick is in the middle so all are at 2.5v
  Wire.write(B11111100);
  return Wire.endTransmission();
}


int setMotors(char key){

  if (key =='W'){  //Uppercase sets DACs to full or near full speed
    Wire.beginTransmission(addr);
    Wire.write(B00000100);  //forwards/backwards is run by DAC C on our AD5315
    Wire.write(B00101011);  //Full forwards, means increasing the voltage up to 1.5v above baseline (so 4V max)
    Wire.write(B00111100);
  return Wire.endTransmission();
  }else if (key == 'A'){
    Wire.beginTransmission(addr);
    Wire.write(B00000001); //rotate CCW, controlled by DAC A
    Wire.write(B00100100);
    Wire.write(B11001100);
  return Wire.endTransmission();
  }else if (key == 'S'){
    Wire.beginTransmission(addr);
    Wire.write(B00000100);
    Wire.write(B00100100);
    Wire.write(B11001100);
  return Wire.endTransmission();
  }else if (key == 'D'){
    Wire.beginTransmission(addr);
    Wire.write(B00000001);
    Wire.write(B00101011);
    Wire.write(B00111100);
  return Wire.endTransmission();
 
  }else if (key =='w'){   ///lower case is to set individual DAC outputs back to 2.5v (center)
    Wire.beginTransmission(addr);
    Wire.write(B00000100);
    Wire.write(B00100111);
    Wire.write(B11111100);
  return Wire.endTransmission();
  }else if (key == 'a'){
    Wire.beginTransmission(addr);
    Wire.write(B00000001);
    Wire.write(B00100111);
    Wire.write(B11111100);
  return Wire.endTransmission();
  }else if (key == 's'){
    Wire.beginTransmission(addr);
    Wire.write(B00000100);
    Wire.write(B00100111);
    Wire.write(B11111100);
  return Wire.endTransmission();
  }else if (key == 'd'){
    Wire.beginTransmission(addr);
    Wire.write(B00000001);
    Wire.write(B00100111);
    Wire.write(B11111100);
  return Wire.endTransmission();
 
  }else{  //zero by default
    setZero();
  }
}
