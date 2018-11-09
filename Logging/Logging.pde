import processing.serial.*;

PrintWriter writer; // local file to log to
String data; // data read from serial
Serial serial; // serial port to listen to

void setup() {
  writer = createWriter("log.txt");
  String portName = "/dev/ttyACM0";
  println("Waiting for " + portName + "...");
  while (!(Serial.list()[0].equals(portName))); // wait until portName is opened
  delay(50);
  serial = new Serial(this, portName, 9600);
  serial.bufferUntil('\n');
  println("Made serial!");
}

void draw() {
  if (serial.available() > 0) {
    data = serial.readStringUntil('\n');
    if (data != null) {
      writer.println(data);
    }
  }
}
