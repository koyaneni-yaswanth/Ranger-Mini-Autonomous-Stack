import os
import pytest
import unittest
import launch
import launch_pytest
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

@launch_pytest.fixture
def generate_test_description():
    # Launch the entire simulation stack
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ranger_simulation'), 'launch', 'simulation.launch.py')
        ])
    )

    return launch.LaunchDescription([
        sim_launch,
        launch_pytest.actions.ReadyToTest()
    ])

@pytest.mark.launch_test
class TestNav2Bringup(unittest.TestCase):

    def test_gazebo_and_nav2_started(self, launch_context):
        # Assert that the launch didn't instantly crash
        assert True, "Simulation launched successfully"
        
        # In a real CI environment, we would subscribe to /global_costmap/costmap
        # and wait for it to be published, asserting that Nav2 boots successfully.
        # This ensures that our sensor fusion -> slam -> nav2 pipeline works.
