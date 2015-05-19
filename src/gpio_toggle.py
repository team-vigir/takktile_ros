#!/usr/bin/env python
import RPi.GPIO as GPIO
import argparse
import time
import signal
import sys
import gpio_comms

switch_channel = None

def toggle_pin(off_duration):
	global switch_channel
	print "Toggling gpio pin ", switch_channel, "for ", off_duration, " seconds."
	GPIO.output(switch_channel, GPIO.LOW)
	time.sleep(off_duration)
	GPIO.output(switch_channel, GPIO.HIGH)
	print "Completed Toggle."

def init_gpio():
	global switch_channel
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(switch_channel, GPIO.OUT, initial=GPIO.HIGH)

def handle_shutdown(srv):
	print "GPIO toggle shutting down now..."
	GPIO.cleanup()
	gpio_comms.shutdown(srv)
	sys.exit(0)

if __name__ == "__main__":
	print "GPIO toggle process is online."
	parser = argparse.ArgumentParser() 
	parser.add_argument("--pin", type=int, default=14)
	args = parser.parse_args()
	switch_channel = args.pin

	init_gpio()
	
	# Wait for action!
	srv = gpio_comms.init_srv()	
	while True:
		off_duration = gpio_comms.wait_for_msg(srv)
		if off_duration is None:
			handle_shutdown(srv)
		else:
			toggle_pin(off_duration)
