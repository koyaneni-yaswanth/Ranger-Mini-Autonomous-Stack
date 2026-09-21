from setuptools import find_packages, setup

package_name = 'ranger_missions'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yash',
    maintainer_email='yash@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'patrol_mission = ranger_missions.patrol_mission:main',
            'ai_commander = ranger_missions.ai_commander:main',
            'master_mission_orchestrator = ranger_missions.master_mission_orchestrator:main',
        ],
    },
)
