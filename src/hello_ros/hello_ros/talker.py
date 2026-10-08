"""Publishes a counter on /chatter. Rate is a ROS parameter so the team can
see how parameters work: ros2 run hello_ros talker --ros-args -p rate_hz:=10.0
"""
import socket

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.declare_parameter('rate_hz', 2.0)
        rate = self.get_parameter('rate_hz').value
        self.pub = self.create_publisher(String, 'chatter', 10)
        self.timer = self.create_timer(1.0 / rate, self.tick)
        self.count = 0
        self.host = socket.gethostname()
        self.get_logger().info(f'Talker up on {self.host} at {rate} Hz')

    def tick(self):
        msg = String(data=f'Hello #{self.count} from {self.host}')
        self.pub.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.count += 1


def main():
    rclpy.init()
    node = Talker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
