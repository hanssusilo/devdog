#include <Wire.h>

#include <ros.h>
#include <geometry_msgs/Vector3.h>

#include <I2Cdev.h>
#include <MPU6050.h>

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


MPU6050 accelgyro;

int16_t ax, ay, az;
int16_t gx, gy, gz;
int16_t mx, my, mz;

geometry_msgs::Vector3 imu;

ros::NodeHandle  nh;

int setY();
int setX();

void messageCb( const geometry_msgs::Vector3& speed_msg){
  sideways = -speed_msg.y;
  forwards = speed_msg.x;
  digitalWrite(13, HIGH-digitalRead(13));   // blink the led
}

ros::Subscriber<geometry_msgs::Vector3> sub("set_vel", &messageCb );

ros::Publisher accel_pub("raw_accel", &imu);
ros::Publisher gyro_pub("raw_gyro", &imu);
ros::Publisher mag_pub("raw_mag", &imu);

void setup()
{
  pinMode(13, OUTPUT);
  nh.initNode();

  Wire.begin();

  accelgyro.initialize();

  nh.advertise(accel_pub);
  nh.advertise(gyro_pub);
  nh.advertise(mag_pub);

  nh.subscribe(sub);

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

void loop()
{ 
  accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
  //CORRECTED VALUES
  pubIMU(-ay, -ax, az, gx, gy, gz, mx, my, mz);
  nh.spinOnce();
  delay(250);
  setMotors();
}


void pubIMU(int ax, int ay, int az, int gx, int gy, int gz, int mx, int my, int mz){
  imu.x = ax;
  imu.y = ay;
  imu.z = az;
  accel_pub.publish(&imu);

  imu.x = gx;
  imu.y = gy;
  imu.z = gz;
  gyro_pub.publish(&imu);

  imu.x = mx;
  imu.y = my;
  imu.z = mz;
  mag_pub.publish(&imu);

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




