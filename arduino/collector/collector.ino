
volatile int counter = 0;
const byte interruptPin = 2;
const byte batteryPin = A2;
const byte refPin = A3;
unsigned long last_time = 0;
unsigned long bat_sum = 0;
unsigned long ref_sum = 0;
unsigned int sample_count = 0;
int interval = 250;
int battery_bytes = 0;
float battery_voltage = 0;
float speed = 0;
void setup() {
  Serial.begin(115200);
  pinMode(interruptPin, INPUT_PULLUP);
  pinMode(batteryPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(interruptPin), detect, RISING);
}
void loop() {
  if ((millis()-last_time) > interval){
    float ref_voltage = (5.0 * (float)ref_sum / (float)sample_count) / 1024.0;
    float calib_voltage = 3.3 - ref_voltage;
    battery_voltage = ((5.0 +  calib_voltage) * 2.0 * (float)bat_sum / (float)sample_count) / 1024.0;
    sample_count = 0;
    bat_sum = 0;
    ref_sum = 0;
    float distance = ((float)counter/1490.0); // calibrated
    counter = 0;
    speed = distance / ((float)interval/1000.0);
    Serial.print(battery_voltage);
    Serial.print(";");
    Serial.println(speed);
    last_time = millis();
  }
  bat_sum += analogRead(batteryPin);
  ref_sum += analogRead(refPin);
  sample_count++;
}

void detect() {
  counter += 1;
}
