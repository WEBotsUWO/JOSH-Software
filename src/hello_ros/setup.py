from glob import glob
from setuptools import find_packages, setup

package_name = 'hello_ros'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Sam',
    maintainer_email='sam2mengistu@gmail.com',
    description='Sample talker/listener used to verify ROS 2 Jazzy setups.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'talker = hello_ros.talker:main',
            'listener = hello_ros.listener:main',
        ],
    },
)
