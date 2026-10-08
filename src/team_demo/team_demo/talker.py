import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    def __init__(self):
        super().__init__('demo_talker')
        self.publisher = self.create_publisher(String, 'demo_topic', 10)
        self.timer = self.create_timer(1.0, self.publish_message)   # 1 Hz
        self.count = 0

    def publish_message(self):
        msg = String()
        msg.data = f'Message #{self.count} from the humanoid team'
        self.publisher.publish(msg)
        self.get_logger().info(f'Sent: "{msg.data}"')
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
