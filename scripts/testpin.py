import RPi.GPIO as GPIO
import time

# Pironman default is usually GPIO 12. 
# Change to 10 if your jumper is set to SPI/10.
TEST_PIN = 12 

GPIO.setmode(GPIO.BCM)
GPIO.setup(TEST_PIN, GPIO.OUT)

print(f"Testing GPIO {TEST_PIN}. Press CTRL+C to stop.")

try:
    while True:
        GPIO.output(TEST_PIN, GPIO.HIGH)
        print("ON  (3.3 Volts)")
        time.sleep(3)
        
        GPIO.output(TEST_PIN, GPIO.LOW)
        print("OFF (0 Volts)")
        time.sleep(3)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nTest stopped.")