import processing.serial.*;

String currentPath; // points to script location
PrintWriter writer; // local file to log to
String data; // data read from serial
Serial serial; // serial port to listen to

void setup() {
  currentPath = dataPath("").substring(0, dataPath("").length() - 4);
  // go through numbers until we find first log#.txt that doesn't exist
  int i;
  for (i = 0; new File(currentPath + "log" + i + ".txt").exists(); i++);
  writer = createWriter("log" + i + ".txt");
  println("Creating logfile log" + i + ".txt");
  
  // wait until something is detected at portName
  String portName = "/dev/ttyACM0";
  println("Waiting for " + portName + "...");
  while (!(Serial.list()[0].equals(portName)));
  delay(50); // give a bit of time, otherwise serial might fail
  
  // open the port and begin listening
  serial = new Serial(this, portName, 9600);
  serial.bufferUntil('\n');
  println("Serial connection successful!");
}

void draw() {
  if (serial.available() > 0) {
    data = serial.readStringUntil('\n');
    if (data != null) {
      writer.println(data);
    }
  }
}
