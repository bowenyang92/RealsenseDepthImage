import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from io import BytesIO

# Full kernels
FULL_KERNEL_3 = np.ones((3, 3), np.uint8)
FULL_KERNEL_5 = np.ones((5, 5), np.uint8)
FULL_KERNEL_7 = np.ones((7, 7), np.uint8)
FULL_KERNEL_9 = np.ones((9, 9), np.uint8)
FULL_KERNEL_31 = np.ones((31, 31), np.uint8)

# 3x3 cross kernel
CROSS_KERNEL_3 = np.asarray(
    [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ], dtype=np.uint8)

# 5x5 cross kernel
CROSS_KERNEL_5 = np.asarray(
    [
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [1, 1, 1, 1, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
    ], dtype=np.uint8)

# 5x5 diamond kernel
DIAMOND_KERNEL_5 = np.array(
    [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [1, 1, 1, 1, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0],
    ], dtype=np.uint8)

# 7x7 cross kernel
CROSS_KERNEL_7 = np.asarray(
    [
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
    ], dtype=np.uint8)

# 7x7 diamond kernel
DIAMOND_KERNEL_7 = np.asarray(
    [
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
    ], dtype=np.uint8)


TMP_PREFIX = '/root/workspace/tmp'


def depthComplete(filename):
    

    filename = os.path.join(TMP_PREFIX, filename)
    depth_map = parse_distance(filename) # np array of depths

    ## step 1
    valid_pixels = (depth_map > 0.1)
    depth_map[valid_pixels] = 100 - depth_map[valid_pixels]

    ## step 2
    depth_map = cv2.dilate(depth_map, DIAMOND_KERNEL_5)

    ## step 3
    depth_map = cv2.morphologyEx(depth_map, cv2.MORPH_CLOSE, FULL_KERNEL_5)

    ## step 4
    empty_pixels = (depth_map < 0.1)
    dilated = cv2.dilate(depth_map, FULL_KERNEL_7)
    depth_map[empty_pixels] = dilated[empty_pixels]

    # step 5
    top_row_pixels = np.argmax(depth_map > 0.1, axis=0)
    top_pixel_values = depth_map[top_row_pixels, range(depth_map.shape[1])]

    for pixel_col_idx in range(depth_map.shape[1]):
        depth_map[0:top_row_pixels[pixel_col_idx], pixel_col_idx] = \
            top_pixel_values[pixel_col_idx]

    # Large Fill
    empty_pixels = depth_map < 0.1
    dilated = cv2.dilate(depth_map, FULL_KERNEL_31)
    depth_map[empty_pixels] = dilated[empty_pixels]



    ## step 7
    valid_pixels = (depth_map > 0.1)
    depth_map[valid_pixels] = 100 - depth_map[valid_pixels]

    depth_map[depth_map > 10 ] = 10


    image_color = cv2.applyColorMap(
            np.uint8(depth_map / np.amax(depth_map) * 255),
            cv2.COLORMAP_RAINBOW)

    retval, img_str = cv2.imencode('.png', image_color)

    img = BytesIO(img_str)
    img.seek(0)

    # buf = color_depths(depths)
    # # depth_plot = Image.open(buf)
    # # depth_plot.save('test_plot.png')

    # buf.seek(0)
    return img


def parse_distance(dist_file):
    with open(dist_file, 'r') as f:
        meta = f.next() # width and height info
        dists = np.array([[float(dist) for dist in line.rstrip(',\n').split(',')] for line in f])

    return np.transpose(dists)  # the file is W rows of width H (720x1080 instead of 1080x720)

