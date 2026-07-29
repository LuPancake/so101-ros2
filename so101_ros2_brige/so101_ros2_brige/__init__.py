

from pathlib import Path
from ament_index_python.packages import get_package_share_directory

PACKAGE_DIR = Path(get_package_share_directory('so101_ros2_bridge'))

CALIBRATION_BASE_DIR = PACKAGE_DIR / 'config' / 'calibration'