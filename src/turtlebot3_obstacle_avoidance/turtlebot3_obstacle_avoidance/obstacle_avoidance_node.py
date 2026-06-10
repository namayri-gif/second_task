import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from turtlebot3_obstacle_avoidance.avoidance_logic import AvoidanceLogic
from geometry_msgs.msg import Twist
from turtlebot3_obstacle_interfaces.srv import SetAvoidanceMode


class Sub(Node):
    def __init__(self):
        super().__init__('Sub')

        self.declare_parameter('forward_threshold', 0.5)
        self.declare_parameter('clear_threshold', 1.0)
        self.declare_parameter('turn_threshold', 0.4)
        self.declare_parameter('mode', 'CAUTIOUS')

        forward_threshold = self.get_parameter('forward_threshold').value
        clear_threshold = self.get_parameter('clear_threshold').value
        turn_threshold = self.get_parameter('turn_threshold').value
        mode = self.get_parameter('mode').value

        self.controller = AvoidanceLogic(
            forward_threshold=forward_threshold,
            clear=clear_threshold,
            turn=turn_threshold)
        self.controller.mode = mode

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
        self.subscription

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.srv = self.create_service(
            SetAvoidanceMode,
            'set_avoidance_mode',
            self.mode_callback)

    def mode_callback(self, request, response):
        valid_modes = ['AGGRESSIVE', 'CAUTIOUS', 'STOP']
        if request.mode in valid_modes:
            self.controller.mode = request.mode
            response.success = True
            response.message = f'Mode changed to {request.mode}'
        else:
            response.success = False
            response.message = f'Invalid mode. Choose from: {valid_modes}'
        return response

    def scan_callback(self, msg):
        front, left, right = self.controller.process_scan_data(msg)
        action = self.controller.decide_action(front, left, right)
        direction = self.controller.direction(left, right)
        speed = self.controller.get_speed()

        cmd = Twist()
        if action == 'FORWARD':
            linear_x = speed
            angular_z = 0.0
        elif action == 'TURN':
            linear_x = 0.0
            angular_z = 0.5 if direction == 'LEFT' else -0.5
        elif action == 'REVERSE':
            linear_x = -0.1
            angular_z = 0.0
        else:
            linear_x = 0.0
            angular_z = 0.0

        cmd.linear.x = linear_x
        cmd.angular.z = angular_z
        self.publisher.publish(cmd)

        self.get_logger().info(
            f'Front: {front:.2f}, Left: {left:.2f}, Right: {right:.2f}')


def main(args=None):
    rclpy.init(args=args)
    subscriber = Sub()
    rclpy.spin(subscriber)
    subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()