#!/usr/bin/env python
import RPi.GPIO as GPIO
import argparse
import time

def toggle_pin(switch_channel, off_duration):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(switch_channel, GPIO.OUT, initial=GPIO.HIGH)
	
	GPIO.output(switch_channel, GPIO.LOW)
	time.sleep(off_duration)
	GPIO.output(switch_channel, GPIO.HIGH)

if __name__ == "__main__":
	parser = argparse.ArgumentParser() 
	parser.add_argument("--pin", type=int, default=14)
	parser.add_argument("--duration", type=float, default=2)
	args = parser.parse_args()

	toggle_pin(args.pin, args.duration)
	
