#!/usr/bin/env micropython

import logging
from ev3dev2.motor import MediumMotor, LargeMotor, SpeedPercent, OUTPUT_A, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor, UltrasonicSensor, GyroSensor
from ev3dev2.led import Leds
from ev3dev2.stopwatch import StopWatch
from ev3dev2.console import Console
from ev3dev2.sound import Sound
from random import randint
from threading import Thread
from time import sleep

# Logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)5s: %(message)s')
log = logging.getLogger(__name__)
log.info("Starting Gyro Boy")

# Initialize
running = True
state = "reset"
timer = StopWatch()
timer.start()

# Brick variables
sound = Sound()
leds = Leds()
console = Console()
gyro_sensor = GyroSensor(INPUT_3)
gyro_sensor.mode = GyroSensor.MODE_GYRO_RATE
arms_motor = MediumMotor(OUTPUT_C)
left_motor = LargeMotor(OUTPUT_D)
right_motor = LargeMotor(OUTPUT_A)
color_sensor = ColorSensor(INPUT_1)
ultra_sonic_sensor = UltrasonicSensor(INPUT_4)


class SensorThread(Thread):
    """Sensor thread, based on Color and Ultrasonic sensors."""

    def run(self):
        global state
        global drive_speed
        global steering

        log.debug("Sensor Thread running!")
        while running:
            if state == "reset":
                drive_speed = 0
                steering = 0
            if state == "ready":
                drive_speed = 40
                sleep(4.0)
                drive_speed = 0
                state = "read sensors"
            if state == "read sensors":
                try:
                    if color_sensor.color == color_sensor.COLOR_RED:
                        log.debug("Detected color: " + color_sensor.color_name)
                        #sound.play_note('C7', 0.5)
                        drive_speed = 0
                        steering = 0
                    if color_sensor.color == color_sensor.COLOR_GREEN:
                        log.debug("Detected color: " + color_sensor.color_name)
                        #sound.play_note('C7', 0.5)
                        drive_speed = 150
                        steering = 0
                    if color_sensor.color == color_sensor.COLOR_BLUE:
                        log.debug("Detected color: " + color_sensor.color_name)
                        #sound.play_note('C7', 0.5)
                        steering = 70
                    if color_sensor.color == color_sensor.COLOR_GREEN:
                        log.debug("Detected color: " + color_sensor.color_name)
                        #sound.play_note('C7', 0.5)
                        steering = -70
                    if color_sensor.color == color_sensor.COLOR_WHITE:
                        log.debug("Detected color: " + color_sensor.color_name)
                        #sound.play_note('C7', 0.5)
                        drive_speed = -75
                    if ultra_sonic_sensor.distance_centimeters < 25:
                        log.debug("Detected close object at distance: {:5.2f}".format(
                            ultra_sonic_sensor.distance_centimeters))
                        steering = 0
                        previous_speed = drive_speed
                        drive_speed = -10

                        try:
                            arms_motor.on_for_rotations(
                                SpeedPercent(30), 1.0/12)
                            arms_motor.on_for_rotations(
                                SpeedPercent(30), -1.0/6)
                            arms_motor.on_for_rotations(
                                SpeedPercent(30), 1.0/12)
                        except:
                            pass

                        if randint(1, 2) == 1:
                            steering = 70
                        else:
                            steering = -70

                        sleep(4.0)
                        #sound.play_note('C7', 0.5)
                        drive_speed = previous_speed
                        steering = 0
                except:
                    pass

            sleep(0.2)


def reset_sensors_and_variables():
    global fall_check_start_time
    global motor_position_sum
    global wheel_angle
    global change_in_motor_position
    global change_in_motor_position_1
    global change_in_motor_position_2
    global change_in_motor_position_3
    global drive_speed
    global steering
    global control_loop_count
    global ok
    global robot_body_angle

    left_motor.reset()
    right_motor.reset()
    left_motor.run_direct()
    right_motor.run_direct()
    fall_check_start_time = get_time()
    motor_position_sum = 0
    wheel_angle = 0
    change_in_motor_position = 0
    change_in_motor_position_1 = 0
    change_in_motor_position_2 = 0
    change_in_motor_position_3 = 0
    drive_speed = 0
    steering = 0
    control_loop_count = 0
    ok = True
    robot_body_angle = -0.25


def calibrate_gyro_offset():
    global gyro_offset

    gyro_minimum_rate = 0
    gyro_maximum_rate = 2

    iteration = 0
    while (gyro_maximum_rate - gyro_minimum_rate) >= 2:
        gyro_minimum_rate = 440
        gyro_maximum_rate = -440
        gyro_sum = 0.0
        for i in range(200):
            gyro_sensor_value = gyro_sensor.value()

            gyro_sum += gyro_sensor_value
            if gyro_sensor_value > gyro_maximum_rate:
                gyro_maximum_rate = gyro_sensor_value
            if gyro_sensor_value < gyro_minimum_rate:
                gyro_minimum_rate = gyro_sensor_value
            sleep(0.004)

        log.debug("Calibrating gyro iteration: {:2d}, gyro_sum: {:4.2f}, gyro_minimum_rate: {:4.2f}, gyro_maximum_rate: {:4.2f}".format(
            iteration, gyro_sum, gyro_minimum_rate, gyro_maximum_rate))

        iteration += 1

    gyro_offset = gyro_sum / 200.0


def calculate_control_loop_period():
    global control_loop_count
    global control_loop_period
    global control_loop_start_time

    if control_loop_count == 0:
        control_loop_period = 0.014
        control_loop_start_time = get_time()
    else:
        time = get_time()
        control_loop_period = (time - control_loop_start_time) / \
            (1000.0 * control_loop_count)

    control_loop_count += 1


def calculate_robot_body_angle_and_speed():
    global gyro_offset
    global robot_body_angle
    global robot_body_angular_velocity

    gyro_sensor_value = gyro_sensor.value()

    gyro_offset = 0.0005 * gyro_sensor_value + 0.9995 * gyro_offset

    robot_body_angular_velocity = gyro_sensor_value - gyro_offset
    robot_body_angle += robot_body_angular_velocity * control_loop_period


def calculate_wheel_angle_and_speed():
    global wheel_angular_velocity
    global motor_position_sum
    global wheel_angle
    global change_in_motor_position
    global change_in_motor_position_1
    global change_in_motor_position_2
    global change_in_motor_position_3
    global control_loop_period

    left_motor_sensor_value = left_motor.position
    right_motor_sensor_value = right_motor.position
    previous_motor_sum = motor_position_sum
    motor_position_sum = left_motor_sensor_value + right_motor_sensor_value
    change_in_motor_position = motor_position_sum - previous_motor_sum

    wheel_angle += (change_in_motor_position -
                    (drive_speed * control_loop_period))

    average_change_in_motor_position = (
        change_in_motor_position + change_in_motor_position_1 + change_in_motor_position_2 + change_in_motor_position_3) / 4.0

    wheel_angular_velocity = average_change_in_motor_position / control_loop_period

    change_in_motor_position_3 = change_in_motor_position_2
    change_in_motor_position_2 = change_in_motor_position_1
    change_in_motor_position_1 = change_in_motor_position


def calculate_output_power():
    global output_power

    output_power = -0.01 * drive_speed + 0.8 * robot_body_angular_velocity + \
        15 * robot_body_angle + 0.08 * wheel_angular_velocity + 0.12 * wheel_angle


def check_power_range(power: float) -> float:
    if power > 100:
        return 100
    if power < -100:
        return -100
    return power


def drive_motors():
    left_output_power = check_power_range(output_power - 0.1 * steering)
    right_output_power = check_power_range(output_power + 0.1 * steering)

    left_motor.duty_cycle_sp = left_output_power
    right_motor.duty_cycle_sp = right_output_power


def check_if_robot_fell_down():
    global fall_check_start_time
    global ok

    if abs(output_power) < 100:
        fall_check_start_time = get_time()
    if (get_time() - fall_check_start_time) > 1000:
        ok = False


def get_time() -> int:
    global timer

    return timer.value_ms


# Start sensor thread
sensor_thread = SensorThread(name="sensor_thread")
sensor_thread.daemon = True
sensor_thread.start()

# Main program loop
while running:
    console.reset_console()
    leds.all_off()

    state = "reset"
    reset_sensors_and_variables()
    calibrate_gyro_offset()

    sound.play_file("/home/robot/sounds/Speed up.wav")
    console.reset_console()
    leds.animate_flash('GREEN', duration=None, block=False)

    state = "ready"
    log.debug("Starting control loop")

    while ok == True:
        time = get_time()

        calculate_control_loop_period()
        calculate_robot_body_angle_and_speed()
        calculate_wheel_angle_and_speed()
        calculate_output_power()
        drive_motors()
        check_if_robot_fell_down()

    state = "fell_over"
    right_motor.stop()
    left_motor.stop()
    leds.animate_stop()
    leds.reset()
    leds.animate_flash('RED')
    console.reset_console()
    sound.play_file("/home/robot/sounds/Speed down.wav")
    sleep(3.0)
    running = False

    log.info("Terminating Gyro Boy")
