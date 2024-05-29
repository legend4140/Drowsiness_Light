const int redPin = D2;
const int greenPin = D1;
const int bluePin = D0;

unsigned long lastBlinkTime = 0;
bool isDrowsy = false;

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String emotionInput = Serial.readStringUntil('\n');
    emotionInput.trim(); // Remove leading/trailing whitespaces
    setColorFromSerialInput(emotionInput);
  }

  displayColor();
}

void displayColor() {
  if (!isDrowsy) {
    // Set LED to full brightness green when not drowsy
    setColor(0, 255, 0); // Green
  } else {
    // Blink in red when drowsy
    unsigned long currentTime = millis();
    if (currentTime - lastBlinkTime >= 500) {
      digitalWrite(redPin, !digitalRead(redPin));
      digitalWrite(greenPin, LOW); // Turn off green
      digitalWrite(bluePin, LOW); // Turn off blue
      lastBlinkTime = currentTime;
    }
  }
}

void setColorFromSerialInput(String emotionInput) {
  if (emotionInput.equals("drowsy")) {
    isDrowsy = true;
  } else if (emotionInput.equals("not_drowsy")) {
    isDrowsy = false;
    // Turn off LED when not drowsy
    setColor(0,255,0);
  }
}

void setColor(int red, int green, int blue) {
  analogWrite(redPin, red);
  analogWrite(greenPin, green);
  analogWrite(bluePin, blue);
}
