from flask import Flask, request, send_file, render_template
import requests
import cv2
import os
import numpy as np
import time
from PIL import Image, ImageDraw
from io import StringIO, BytesIO

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()

app = Flask(__name__)


TMP_PREFIX = '/root/workspace/tmp'

DEBUG = False # DEBUG = True will run with a hard-coded image filename
SERVICE = True # SERVICE = False will not start the Flask app in main function

@app.route('/image', methods = ['POST'])
def get_img():
    if (DEBUG):
        filename = 'color-frame-2018-8-9-12-4-14.png'
    else:
        filename = str(request.get_data())

    filename = os.path.join(TMP_PREFIX, filename)

    img = Image.open(filename)
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/PNG')

@app.route("/crop", methods = ['POST'])
def crop():
    
    if (DEBUG):
        dist_file  = 'distances-2018-8-9-12-4-14.txt'
        depth_file = 'depth-frame-2018-8-9-12-4-14.png'
        color_file = 'color-frame-2018-8-9-12-4-14.png'

    else:
        json_data = request.get_json() # 'distance'; 'depth-frame' (png); 'color-frame' (png)
        print ("posted")
        print(json_data)

        dist_file  = json_data['distance']
        depth_file = json_data['depth-frame']
        color_file = json_data['color-frame']


    dist_file  = os.path.join(TMP_PREFIX, dist_file) # txt
    depth_file = os.path.join(TMP_PREFIX, depth_file) # png
    color_file = os.path.join(TMP_PREFIX, color_file) # png

    dists = parse_distance(dist_file) # returns np array of dists
    t1 = time.time()
    crop = crop_from_depth(dists) # returns np array of 1s and 0s, whether to keep pixel or not
    t2 = time.time()
    print("{} to crop".format(t2-t1))

    color_img = cv2.imread(color_file)


    # transpose to make rgb easier access
    transposed_crop = crop.transpose()
    transposed_color_img = color_img.transpose()

    for c, color_channel in enumerate(transposed_color_img):
        transposed_color_img[c] = np.multiply(transposed_crop, color_channel)

    cropped_color_img = transposed_color_img.transpose()

    # retval is unimportant, required because imencode returns a tuple
    retval, img_str = cv2.imencode('.png', cropped_color_img)

    print("return value {}".format(retval))
    img = BytesIO(img_str)
    img.seek(0)

    return send_file(img, mimetype = 'image/PNG')

@app.route('/depthcolor', methods = ['POST'])
def depthcolor():
    if (DEBUG):
        filename = 'distances-2018-8-9-12-4-14.txt'
    else:
        filename = str(request.get_data())

    filename = os.path.join(TMP_PREFIX, filename)
    depths = parse_distance(filename) # np array of depths

    buf = color_depths(depths)
    # depth_plot = Image.open(buf)
    # depth_plot.save('test_plot.png')

    buf.seek(0)
    return send_file(buf, mimetype = 'image/PNG')



def parse_distance(dist_file):
    with open(dist_file, 'r') as f:
        meta = f.next() # width and height info
        dists = np.array([[float(dist) for dist in line.rstrip(',\n').split(',')] for line in f])

    return np.transpose(dists)  # the file is W rows of width H (720x1080 instead of 1080x720)


def crop_from_depth(dists, threshold = 2.5, ksize = 15):
    crop = np.array([[float(dist < threshold and dist > 0) for dist in row] for row in dists])

    # blur and apply ceiling to fill in holes in the depth values
    crop = cv2.blur(crop, (ksize, ksize))
    crop = np.array([[int(c > 0) for c in r] for r in crop])

    return crop

def color_depths(orig_depths, threshold = 2.5):
    '''

    Params:
    '''
    crop = crop_from_depth(orig_depths, threshold)
    cropped_depths = np.multiply(orig_depths, crop.astype(np.float32))

    # Change all the background 0 values to threshold + 1 so they're displayed as "far away" on heatmap
    for r_, r in enumerate(cropped_depths):
        for c_, c in enumerate(r):
            if (c == 0):
                cropped_depths[r_][c_] = threshold + 1

    min_depth = nonzero_min(cropped_depths)
    max_depth = non_threshold_max(cropped_depths, threshold)
    print ("({}, {})".format(min_depth, max_depth))

    # Currently heatmap range from min_depth to min_depth + 0.4 m. Need to find better, more generalizable
    # method.
    # 
    # matplotlib color map styles: https://matplotlib.org/users/colormaps.html
    ax = plt.imshow(cropped_depths, vmin = min_depth, vmax = min_depth + 0.4, cmap = 'RdBu')
    plt.grid(False)
    plt.colorbar()

    buf = BytesIO()
    plt.savefig(buf, format = 'png')
    plt.close()

    return buf


def nonzero_min(np_mat):
    cur_min = np_mat.max()
    for r in np_mat:
        for x in r:
            if (x > 0):
                cur_min = min(cur_min, x)

    return cur_min

def non_threshold_max(np_mat, threshold):
    cur_max = 0
    for r in np_mat:
        for x in r:
            if (x < threshold):
                cur_max = max(cur_max, x)

    return cur_max


if (__name__ == '__main__'):
    if (not SERVICE):
        dist_file  = 'distances-2018-8-3-11-57-14.txt'
        depth_file = 'depth-frame-2018-8-3-11-57-14.png'
        color_file = 'color-frame-2018-8-3-11-57-14.png'

        # dist_file  = 'distances-2018-8-7-15-17-30.txt'
        # depth_file = 'depth-frame-2018-8-7-15-17-30.png'
        # color_file = 'color-frame-2018-8-7-15-17-30.png'


        dist_file  = os.path.join(TMP_PREFIX, dist_file) # txt
        depth_file = os.path.join(TMP_PREFIX, depth_file) # png
        color_file = os.path.join(TMP_PREFIX, color_file) # png

        dists = parse_distance(dist_file)
        t1 = time.time()
        # dists = fill_depths(dists, 5)
        crop = crop_from_depth(dists)
      
        t2 = time.time()
        print("{} to fill depths".format(t2-t1))
        # crop = crop_from_depth(dists)
        print(crop.shape)
        color_img = cv2.imread(color_file)
        print(color_img.shape)


        # transpose to make rgb easier access
        transposed_crop = crop.transpose()
        transposed_color_img = color_img.transpose()

        for c, color_channel in enumerate(transposed_color_img):
            transposed_color_img[c] = np.multiply(transposed_crop, color_channel)

        cropped_color_img = transposed_color_img.transpose()

        cv2.imwrite('crop-2018-8-7-15-17-30.jpg', cropped_color_img)

        color_depths(dists)

    else:
        app.run(host = '0.0.0.0', port = 5004)








