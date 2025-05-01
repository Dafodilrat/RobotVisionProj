from setuptools import find_packages, setup
import glob
import os

package_name = 'calypso2'


def package_files(source, destination):
    paths = []
    for dirpath, _, filenames in os.walk(source):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(full_path, source)  # Preserve nested structure
            install_path = os.path.join('share', package_name, destination, os.path.dirname(relative_path))
            paths.append((install_path, [full_path]))
    return paths


data_files=[
    ('share/ament_index/resource_index/packages',['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    ('share/' + package_name + '/urdf', glob.glob('urdf/*.urdf.xacro')),
    ('share/' + package_name + '/world', glob.glob('world/*.sdf')),
    ('share/' + package_name + '/launch', glob.glob('launch/*.launch.py')),
    ('share/' + package_name + '/config', glob.glob('config/*.yaml'))
]

data_files.extend(package_files('meshes', 'meshes'))

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files= data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your@email.com',
    description='Ground truth pose publisher for calypso2 AUV',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'calypso2_ground_truth = calypso2.ppose:main',
        ],
    },
)
