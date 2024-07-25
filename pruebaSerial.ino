
int outByte = 0;               // variable para enviar al puerto usb

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);      // abre el puerto serie a 9600 bps: 
}

void loop() {
  // put your main code here, to run repeatedly:
  outByte = analogRead(A0);         // leer dato analógico
  Serial.println(outByte);          // enviar dato
  delay(10);
}
