#include <Wire.h>

#include <ros.h>
#include <geometry_msgs/Vector3.h>

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

ros::NodeHandle  nh;

int setY();
int setX();

void messageCb( const geometry_msgs::Vector3& speed_msg){
  sideways = -speed_msg.y;
  forwards = speed_msg.x;
  digitalWrite(13, HIGH-digitalRead(13));   // blink the led
}

ros::Subscriber<geometry_msgs::Vector3> sub("set_vel", &messageCb );

void setup()
{
  pinMode(13, OUTPUT);
  nh.initNode();
 
  Wire.begin();
 
  nh.subscribe(sub);
 
  delay(2000);
 
  f= 1;//setZero();
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

void loop()
{ 
  nh.spinOnce();
  //setZero();
  delay(20);
  //setMotors();
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
