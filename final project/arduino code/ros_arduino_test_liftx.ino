#include <Adafruit_PWMServoDriver.h>
#include <Wire.h>
#include <ros.h>
#include <geometry_msgs/Twist.h>

// Adafruit PWM Servo Driver °´Ã¼ »ý¼º
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// ROS Åë½ÅÀ» À§ÇÑ NodeHandle °´Ã¼
ros::NodeHandle nh;

// ÈÙ ¸ðÅÍ ¹æÇâ Á¦¾î ÇÉ ¼³Á¤
const int IN1 = 2;
const int IN2 = 3;
const int IN3 = 4;
const int IN4 = 5;
const int IN5 = 6;
const int IN6 = 7;
const int IN7 = 8;
const int IN8 = 9;

// PWM ÇÉ ¼³Á¤
const int Ena = 0;
const int Enb = 1;
const int Enc = 14;
const int End = 15;

// cmd_vel µ¥ÀÌÅÍ¸¦ À§ÇÑ º¯¼ö
float linear_x = 0.0;
float linear_y = 0.0;
float angular_z = 0.0;

// ROSÀÇ /cmd_vel ÅäÇÈÀ» Ã³¸®ÇÏ±â À§ÇÑ ÄÝ¹é ÇÔ¼ö
void cmdVelCallback(const geometry_msgs::Twist& cmd_msg) {
  linear_x = cmd_msg.linear.x;
  linear_y = -cmd_msg.linear.y;
  angular_z = cmd_msg.angular.z;
  angular_z = angular_z / 3;

}

// /cmd_vel ÅäÇÈÀ» ±¸µ¶ÇÏ±â À§ÇÑ Subscriber °´Ã¼
ros::Subscriber<geometry_msgs::Twist> cmd_sub("cmd_vel", &cmdVelCallback);

void setup() {
  // PWM ¼³Á¤
  pwm.begin();
  pwm.setPWMFreq(1600);  // ÁÖÆÄ¼ö ¼³Á¤

  // ½Ã¸®¾ó Åë½Å ÃÊ±âÈ­
  Serial.begin(9600);

  // ÇÉ¸ðµå ¼³Á¤
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(IN5, OUTPUT);
  pinMode(IN6, OUTPUT);
  pinMode(IN7, OUTPUT);
  pinMode(IN8, OUTPUT);
  //pinMode(lift1,OUTPUT);
  //pinMode(lift2,OUTPUT);

  // save I2C bitrate
  uint8_t twbrbackup = TWBR;
  // must be changed after calling Wire.begin() (inside pwm.begin())
  TWBR = 12; // upgrade to 400KHz!
  
  // ROS ³ëµå ÃÊ±âÈ­
  nh.initNode();
  nh.subscribe(cmd_sub);

  // ÃÊ±â ¼³Á¤: ¸ðµç ¸ðÅÍ ¹× PWM ÇÉ ÃÊ±âÈ­
  stopAllMotors();
}

void stopAllMotors() {
  // ¸ðÅÍ Á¤Áö
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  digitalWrite(IN5, LOW);
  digitalWrite(IN6, LOW);
  digitalWrite(IN7, LOW);
  digitalWrite(IN8, LOW);
  pwm.setPWM(Ena, 0, 0);
  pwm.setPWM(Enb, 0, 0);
  pwm.setPWM(Enc, 0, 0);
  pwm.setPWM(End, 0, 0);
}

void moveMecanumWheels(float linear_x, float linear_y, float angular_z) {
  // Mecanum ÈÙ Á¦¾î °ø½Ä
  float motor1_speed = linear_x + linear_y - angular_z; //앞 왼쪽 모터
  float motor2_speed = linear_x - linear_y + angular_z; // 앞 오른쪽 모터
  float motor3_speed = linear_x + linear_y + angular_z; // 뒤 오른쪽 모터
  float motor4_speed = linear_x - linear_y - angular_z; // 뒤 왼쪽 모터

  // ¸ðÅÍ ¹æÇâ ¼³Á¤ ¹× PWM ¼³Á¤
  controlMotor(IN1, IN2, motor1_speed, Ena);
  controlMotor(IN3, IN4, motor2_speed, Enb);
  controlMotor(IN5, IN6, motor3_speed, Enc);
  controlMotor(IN7, IN8, motor4_speed, End);
}

void controlMotor(int pin1, int pin2, float speed, int pwm_pin) {
  /*if (speed > 0.1) {
    digitalWrite(pin1, HIGH);
    digitalWrite(pin2, LOW);
  } else if (speed < -0.1) {
    digitalWrite(pin1, LOW);
    digitalWrite(pin2, HIGH);
  } else {
    digitalWrite(pin1, LOW);
    digitalWrite(pin2, LOW);
  }
  pwm.setPWM(pwm_pin, 0, map(1, 0, 1, 0, 4095));  // 원래코드*/
  if (speed >= 0.01) {
    digitalWrite(pin1, HIGH);
    digitalWrite(pin2, LOW);
  } else if (speed < -0.01) {
    digitalWrite(pin1, LOW);
    digitalWrite(pin2, HIGH);
  } else {
    digitalWrite(pin1, LOW);
    digitalWrite(pin2, LOW);
  }
  int pwm_value=0;
  // speed°¡ 0.01 ~ 0.3
  if (abs(speed) > 0.01 && abs(speed) <= 0.4) {
    pwm_value = 3276;
  } else {
    pwm_value = 4095;
  }

  pwm.setPWM(pwm_pin, 0, pwm_value);
}

void loop() {
  // /cmd_vel·ÎºÎÅÍ ¹ÞÀº µ¥ÀÌÅÍ¸¦ ¹ÙÅÁÀ¸·Î Mecanum ÈÙ Á¦¾î
  moveMecanumWheels(linear_x, linear_y, angular_z);

  // ROS ³ëµå Ã³¸®
  nh.spinOnce();
  delay(10);
}
