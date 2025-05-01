from setuptools import find_packages, setup
from glob import glob

package_name = 'calypso2_thruster'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/src', glob('src/*.py')),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dafodilrat',
    maintainer_email='haroon@bu.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pwm_rpm_converter = calypso2_thruster.converter:main'
        ],
    },
)
