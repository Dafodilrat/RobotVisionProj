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
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dafodilrat',
    maintainer_email='haroon@bu.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
