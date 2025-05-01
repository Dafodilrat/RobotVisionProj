# auv_pid_controller.py
#! /usr/bin/python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
import math
import numpy as np
import time

class PID:
    def __init__(self, kp, ki=0.0, kd=0.0, dt=0.1, output_limits=(None, None)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt

        self.last_error = 0.0
        self.integral = 0.0
        self.start_time= time.time()

        self.min_output, self.max_output = output_limits

    def reset(self):
        self.last_error = 0.0
        self.integral = 0.0

    def update(self, current_value, target_value):
        error = target_value - current_value
        self.integral += error * (time.time()-self.start_time)
        derivative = (error - self.last_error) / (time.time()-self.start_time)

        output = (
            self.kp * error +
            self.ki * self.integral +
            self.kd * derivative
        )

        self.last_error = error

        # Clamp output if needed
        if self.max_output is not None:
            output = min(output, self.max_output)
        if self.min_output is not None:
            output = max(output, self.min_output)

        return output

def yaw_from_quat(q):
    siny_cosp = 2 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)

class AUVPIDController(Node):
    def __init__(self):
        super().__init__('calypso2_pid_controller')

        self.min_thrust=-600
        self.max_thrust=600

        # PID controllers for x, y, and yaw
        self.pid_x = PID(kp=1, kd=0.2, dt=0.1)
        self.pid_y = PID(kp=1, kd=0.2, dt=0.1)
        self.pid_z = PID(kp=0.9, ki=0.001 ,kd=0.5)

        self.pid_yaw = PID(kp=2.0, kd=0.5, dt=0.1, output_limits=(-10, 10))

        self.current_pose = None
        self.target_pose = None

        # ROS setup
        # self.create_subscription(Odometry, '/odometry/filtered', self.odom_callback, 10)
        self.create_subscription(PoseStamped, '/target_pose', self.target_callback, 10)
        self.create_subscription(Odometry, '/calypso2/pose', self.pose_callback, 10)
        self.cmd_pub = self.create_publisher(Float64MultiArray, '/thruster_velocity_controller/commands', 10)

        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info("calypso PID controller node started.")

    def pose_callback(self,msg):
        self.current_pose = msg.pose.pose
    
    # def odom_callback(self, msg):

    def target_callback(self, msg):
        self.target_pose = msg.pose

    def control_loop(self):
        if self.current_pose is None or self.target_pose is None:
            return

        # Extract current state
        x = self.current_pose.position.x
        y = self.current_pose.position.y
        z = self.current_pose.position.z
        yaw = yaw_from_quat(self.current_pose.orientation)

        # Target position (auto-calculate yaw)
        x_t = self.target_pose.position.x
        y_t = self.target_pose.position.y
        z_t = self.target_pose.position.z
        dx = x_t - x
        dy = y_t - y
        yaw_t = math.atan2(dy, dx)

        # PID outputs
        pid_surge = self.pid_x.update(x, x_t)    # forward/backward
        pid_sway  = self.pid_y.update(y, y_t)    # lateral
        pid_heave = self.pid_z.update(z, z_t)    # vertical
        yaw_error = math.atan2(math.sin(yaw_t - yaw), math.cos(yaw_t - yaw))
        pid_yaw   = 0#self.pid_yaw.update(0.0, yaw_error)

        # Base thrust (if needed, e.g., 0.0)
        self.base_thrust = 515

        heave_thrust = 0
        
        
        # Manual thrust mixing (inward-facing X configuration)
        heave_thrust = self.base_thrust + pid_heave
        thruster_1 = pid_yaw - pid_surge + pid_sway  # t1
        thruster_2 = pid_yaw - pid_surge - pid_sway  # t2
        thruster_3 = pid_yaw + pid_surge - pid_sway  # t3
        thruster_4 = pid_yaw + pid_surge + pid_sway  # t4


        # thruster_1 = 0
        # thruster_2 = 0
        # thruster_3 = 0
        # thruster_4 = 0

        #Map [-1, 1] → [min_thrust, max_thrust]
        # scaled = ((val + 1) / 2) * (max - min) + min
        # scaled_thrusts = [((val + 1) / 2) * (self.max_thrust - self.min_thrust) + self.min_thrust for val in normalized]


        thrusts =[heave_thrust, heave_thrust, heave_thrust, heave_thrust,thruster_1,thruster_2,thruster_3,thruster_4]

        # Normalize to [-1, 1]
        max_abs = max(abs(t) for t in thrusts)
        if max_abs > 1e-6:
            normalized = [t / max_abs for t in thrusts]
        else:
            normalized = [0.0 for _ in thrusts]

        msg = Float64MultiArray()
        msg.data = [float(x) for x in thrusts]
        self.cmd_pub.publish(msg)

        # Optional debug
        self.get_logger().info(f"Thrusts: {['{:.2f}'.format(t) for t in thrusts]}")

def main(args=None):
    rclpy.init(args=args)
    node = AUVPIDController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
