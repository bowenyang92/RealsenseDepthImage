from flask import Flask, request, send_file, render_template
from rosbag_utils import MyRosbag
import requests
import os
import sys
from PIL import Image
from io import BytesIO
import base64

app = Flask(__name__)

UPLOAD_DIR = './tmp/rosbag_upload'

@app.route('/')
def index():
    return render_template('index.html', has_depth_result = False)

@app.route('/rosbagupload', methods = ['POST'])
def rosbagupload():
    rosbagfile = request.files['rosbagfile']
    print (rosbagfile.filename)
    filename = os.path.join(UPLOAD_DIR, rosbagfile.filename)
    rosbagfile.save(filename)

    rosbag = MyRosbag(filename)
    print(rosbag.version)

    print (rosbag.depth_size)

    os.remove(filename)

    return render_template('index.html', has_depth_result = False, has_rosbag_result = True,
        filename = rosbagfile.filename,
        fileversion = rosbag.version,
        depth_fps = str(rosbag.depth_fps),
        depth_encoding = rosbag.depth_encoding,
        depth_size = str(rosbag.depth_size),
        color_fps = str(rosbag.color_fps),
        color_encoding = rosbag.color_encoding,
        color_size = str(rosbag.color_size),
        stereo_baseline = str(rosbag.stereo_baseline))


@app.route('/realsense', methods=['POST'])
def realsense():
    r = requests.get('http://50.227.54.146:9000/capture') # Use Bowen's script to capture image
    # r is json with headers 'color-frame', 'depth-frame', and 'distance', each corresponding
    # to a filename

    print (r.json()['depth-frame'])

    parsed = r.json()


    # Both rosbag_app.py and depth processing service are running on 65
    # For some reason cannot access 65 from 65, have to use localhost
    new_image = requests.post('http://localhost:5004/image', parsed['color-frame'])
    cropped_img = requests.post('http://localhost:5004/crop', json = parsed)
    depth_vis = requests.post('http://localhost:5004/depthcolor', parsed['distance'])


    
    # print ('posting blanks')
    # new_image = requests.post('http://localhost:5004/image', '')
    # print ('posting crop')
    # cropped_img = requests.post('http://localhost:5004/crop', '')
    # print ('posting depth')
    # depth_vis = requests.post('http://localhost:5004/depthcolor', '')


    new_image_pil = Image.open(BytesIO(new_image.content))
    cropped_img_pil = Image.open(BytesIO(cropped_img.content))
    depth_vis_pil = Image.open(BytesIO(depth_vis.content))

   

    return render_template('index.html', has_depth_result = True,
        new_color_src = embed_image_html(new_image_pil),
        cropped_src = embed_image_html(cropped_img_pil),
        depth_vis_src = embed_image_html(depth_vis_pil)
    )

def embed_image_html(image):
    """Creates an image embedded in HTML base64 format.
    
    Params:
        image: The output from the recolorization
    """
#     image_pil = Image.fromarray((255 * image).astype('uint8'))
#     image_pil = image_pil.resize((224, 224))
    
    string_buf = BytesIO()
    image.save(string_buf, format='png')
    
    data = base64.b64encode(string_buf.getvalue())
    base = str(data)
    with open("output.txt", "w") as f:
        f.write(base)

    # base = base[2:-1] # Python 3 needs [2:-1], Python 2 doesn't
    
    return 'data:image/png;base64,' + base


if (__name__ == '__main__'):
    if (not os.path.exists(UPLOAD_DIR)):
        os.makedirs(UPLOAD_DIR)
    app.run(host = '0.0.0.0', port = 5005)

