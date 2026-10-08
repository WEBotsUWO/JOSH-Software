import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):
    def __init__(self):
        super().__init__('demo_listener')
        self.subscription = self.create_subscription(
            String, 'demo_topic', self.on_message, 10)

    def on_message(self, msg):
        self.get_logger().info(f'Received: "{msg.data}"')


def main():
    rclpy.init()
    node = Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
