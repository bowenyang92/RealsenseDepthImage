''' Utilities manipulating ROS .bag videos recorded by Intel RealSense cameras.


'''
import rosbag
import std_msgs.msg
import numpy as np
import cv2
from cv_bridge import CvBridge # implementation by ROS to convert to OpenCV images
import itertools

class Topics():
    # topics from https://github.com/IntelRealSense/librealsense/blob/master/src/media/readme.md
    FILE_VERSION = '/file_version'
    DEVICE_INFO = '/device_0/info'
    DEPTH_INFO = '/device_0/sensor_0/Depth_0/info'
    DEPTH_CAMERA_INFO = '/device_0/sensor_0/Depth_0/info/camera_info'
    COLOR_INFO = '/device_0/sensor_1/Color_0/info'
    COLOR_CAMERA_INFO = '/device_0/sensor_1/Color_0/info/camera_info'

    DEPTH_SENSOR_INFO = '/device_0/sensor_0/info'
    COLOR_SENSOR_INFO = '/device_0/sensor_1/info'

    # DEPTH OPTIONS
    DEPTH_UNITS_VALUE = '/device_0/sensor_0/option/Depth Units/value'
    DEPTH_UNITS_DESCRIP = '/device_0/sensor_0/option/Depth Units/description'
    STEREO_BASELINE_VALUE = '/device_0/sensor_0/option/Stereo Baseline/value'   # Distance between two lens
    STEREO_BASELINE_DESCRIP = '/device_0/sensor_0/option/Stereo Baseline/description' 

    COLOR_DATA = '/device_0/sensor_1/Color_0/image/data'
    COLOR_METADATA = '/device_0/sensor_1/Color_0/image/metadata'

    DEPTH_DATA = '/device_0/sensor_0/Depth_0/image/data'
    DEPTH_METADATA = '/device_0/sensor_0/Depth_0/image/metadata'


class MyRosbag:

    def __init__(self, file, topics = [
        Topics.FILE_VERSION, Topics.DEPTH_INFO, Topics.DEPTH_CAMERA_INFO,
        Topics.COLOR_INFO, Topics.COLOR_CAMERA_INFO, Topics.DEPTH_SENSOR_INFO, Topics.COLOR_SENSOR_INFO,
        Topics.DEPTH_UNITS_VALUE, Topics.DEPTH_UNITS_DESCRIP, Topics.STEREO_BASELINE_VALUE,
        Topics.STEREO_BASELINE_DESCRIP
    ]):
        ''' Stores important values from the rosbag file.

        Usage:
            Initialize such as 
                my_rosbag = MyRosbag(rosbagfile)

            Access values like 
                my_rosbag.version
                my_rosbag.depth_fps
                etc

        Defines:
            version
            depth_fps
            depth_encoding
            depth_size
            color_fps
            color_encoding
            color_size
            depth_unit
            stereo_baseline
        '''

        self.bag = rosbag.Bag(file)

        for topic, msg, t in self.bag.read_messages(topics = topics):
            # Need to hardcode topic conditions because bag.read_messages returns a tuple generator
            # that can only be iterated, so can't pick specific topics.

            msg_data = std_msgs.msg.String(msg).data
            if (topic == Topics.FILE_VERSION):
                self.version = msg_data.data
            elif (topic == Topics.DEPTH_INFO):
                self.depth_fps = msg_data.fps
                self.depth_encoding = msg_data.encoding
            elif (topic == Topics.DEPTH_CAMERA_INFO):
                w = msg_data.width
                h = msg_data.height
                self.depth_size = (w, h)
            elif (topic == Topics.COLOR_INFO):
                self.color_fps = msg_data.fps
                self.color_encoding = msg_data.encoding
            elif (topic == Topics.COLOR_CAMERA_INFO):
                w = msg_data.width
                h = msg_data.height
                self.color_size = (w, h)
            elif (topic == Topics.DEPTH_UNITS_VALUE):
                self.depth_unit = msg_data.data     # in meters
            elif (topic == Topics.STEREO_BASELINE_VALUE):
                self.stereo_baseline = msg_data.data # in millimeters




    def __del__(self):
        self.bag.close()


    def get_color_frame(self, k):
        ''' Returns an OpenCV color image for frame k in the rosbag video.

        Note that the returned image is BGR encoded for OpenCV compatibility, but CvBridge
        returns RGB images. 
        To convert, use cv2.cvtColor(img, cv2.COLOR_BGR2RGB) or cv2.cvtColor(img, cv2.COLOR_RGB2BGR).

        '''
        topic, msg, t = next(itertools.islice(
            self.bag.read_messages(topics = Topics.COLOR_DATA), k, k+1))

        bridge = CvBridge()
        rgb_img = bridge.imgmsg_to_cv2(msg) # CvBridge returns RGB

        bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR) # OpenCV reads images in BGR

        return bgr_img

    def get_depth_frame(self, k):
        topic, msg, t = next(itertools.islice(
            self.bag.read_messages(topics = Topics.DEPTH_DATA), k, k+1))

        bridge = CvBridge()
        depth_img = bridge.imgmsg_to_cv2(msg)
        return depth_img
        














