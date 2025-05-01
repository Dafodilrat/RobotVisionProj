import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class Rosetta(Node):

    def __init__(self):
        super().__init__('pwm_rpm_converter')

        # Publisher for final thrust values
        self.thrust_publisher = self.create_publisher(Float64MultiArray, '/thruster_velocity_controller/commands', 10)

        # Subscriber to raw PWM commands
        self.create_subscription(Float64MultiArray, '/thruster/pwm_commands', self.get_pwm, 10)

        # Init PWM input storage
        self.pwm_inputs = [1500.0] * 8  # Default neutral PWM
        self.get_logger().info('Rosetta PWM-to-Thrust converter node initialized.')

    def get_pwm(self, msg):
        if len(msg.data) == 8:
            self.pwm_inputs = msg.data
            msg = Float64MultiArray()
            msg.data = [self.converter(x) for x in self.pwm_inputs]
            self.thrust_publisher.publish(msg)
        else:
            self.get_logger().warn('Received PWM command array with invalid length.')

    def converter(self, x):
        coeffs = [-1.6453836430727448e-05, 0.07440821248059681, -100.45437634228745, 38769.58439545923]
        
        x = min(x, 1900)
        if 1470 < x < 1530:
            y = 0
        elif 1530 <= x <= 1900:
            y = x**3 * coeffs[0] + x**2 * coeffs[1] + x * coeffs[2] + coeffs[3]
        elif 1100 < x < 1470:
            y = -(x**3 * coeffs[0] + x**2 * coeffs[1] + x * coeffs[2] + coeffs[3])
        else:
            y = 0
        return round(round(y, 4) * 0.1047198, 4)


def main(args=None):
    rclpy.init(args=args)
    node = Rosetta()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
