#!/usr/bin/env python3
import odrive
from odrive.enums import *

from UDPComms import Subscriber, Publisher
import time

cmd = Subscriber("f t", b"ff", 8830, timeout = 0.3)
telemetry = Publisher("bat_voltage F0_cur F1_cur M0_cur M1_cur B0_cur B1_cur", b"f6f", 8810)

print("finding an odrives...")
middle_odrive = odrive.find_any(serial_number="208037853548")
print("found middle odrive")
front_odrive = odrive.find_any(serial_number="376136493137")
print("found front odrive")
back_odrive = odrive.find_any(serial_number="208037843548")
print("found back odrive")
print("found all odrives")

middle_odrive.axis0.requested_state = AXIS_STATE_IDLE
middle_odrive.axis1.requested_state = AXIS_STATE_IDLE
front_odrive.axis0.requested_state = AXIS_STATE_IDLE
front_odrive.axis1.requested_state = AXIS_STATE_IDLE
back_odrive.axis0.requested_state = AXIS_STATE_IDLE
back_odrive.axis1.requested_state = AXIS_STATE_IDLE

# this makes sure there are no old messages queued up that can make
# the rover drive
first_msg = cmd.recv()
start_time = time.time()
while (time.time() - start_time) < 5:
    ignore_msg = cmd.recv()

while True:
    try:
        msg = cmd.recv()
        print(msg)

        telemetry.send( middle_odrive.vbus_voltage,
                        front_odrive.axis0.motor.current_control.Iq_measured,
                        front_odrive.axis1.motor.current_control.Iq_measured,
                        middle_odrive.axis0.motor.current_control.Iq_measured,
                        middle_odrive.axis1.motor.current_control.Iq_measured,
                        back_odrive.axis0.motor.current_control.Iq_measured,
                        back_odrive.axis1.motor.current_control.Iq_measured)

        if (msg.t == 0 and msg.f == 0):
            middle_odrive.axis0.requested_state = AXIS_STATE_IDLE
            middle_odrive.axis1.requested_state = AXIS_STATE_IDLE
            front_odrive.axis0.requested_state = AXIS_STATE_IDLE
            front_odrive.axis1.requested_state = AXIS_STATE_IDLE
            back_odrive.axis0.requested_state = AXIS_STATE_IDLE
            back_odrive.axis1.requested_state = AXIS_STATE_IDLE
        else:
            middle_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            middle_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            front_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            front_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            back_odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            back_odrive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

            middle_odrive.axis0.controller.vel_setpoint = -(msg.f + msg.t)
            middle_odrive.axis1.controller.vel_setpoint = (msg.f - msg.t)
            front_odrive.axis0.controller.vel_setpoint = (-msg.f - msg.t)
            front_odrive.axis1.controller.vel_setpoint = -(-msg.f + msg.t)

            # back odrive is reversed left to right
            back_odrive.axis1.controller.vel_setpoint = (msg.f - msg.t)
            back_odrive.axis0.controller.vel_setpoint = -(msg.f + msg.t)
    except:
        middle_odrive.axis0.requested_state = AXIS_STATE_IDLE
        middle_odrive.axis1.requested_state = AXIS_STATE_IDLE
        front_odrive.axis0.requested_state = AXIS_STATE_IDLE
        front_odrive.axis1.requested_state = AXIS_STATE_IDLE
        back_odrive.axis0.requested_state = AXIS_STATE_IDLE
        back_odrive.axis1.requested_state = AXIS_STATE_IDLE
        middle_odrive.axis0.controller.vel_setpoint = 0
        middle_odrive.axis1.controller.vel_setpoint = 0
        front_odrive.axis0.controller.vel_setpoint = 0
        front_odrive.axis1.controller.vel_setpoint = 0
        back_odrive.axis0.controller.vel_setpoint = 0
        back_odrive.axis1.controller.vel_setpoint = 0
        raise

