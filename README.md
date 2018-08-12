
## [RealSense DS435 Applications]

 Overview: 

RealSense D400 Series Depth Cameras are for development and research mostly, not for customers. The Realsens SDK 2.0 works well on this camera but most of other workable applications on some previous realsense camera does not work well on D400 (since this one is still pretty new).
  
 Also, compared to other Depth Cameras, comments from other customers indicates that RealSense does not have a very good depth quality. (They say kinect is better). We can see that from the real time depth viewer, the edges of the image are not very smooth. (But some research on the topic: depth completion is solving this problem)

> Rough numbers on the depth accuracy:
> range: 0.25m - 25 m , details see [hardware specs](https://click.intel.com/intelr-realsensetm-depth-camera-d435.html), [wiki](https://en.wikipedia.org/wiki/Intel_RealSense)
> *the rgb and detph sensor have different field of view, need to be aligned


###  Contents :
- SDK, APIs and environment
- Applications and related tools
- Our project and component
- Reference and papers

***

### 1. SDK, APIs and environment:
[**Intel® RealSense™ SDK 2.0**](https://github.com/IntelRealSense/librealsense)

- Available platform:

Linux
Windows
MacOS
Raspberry Pi 3 ( Ubuntu Mate )
Nvidia Jetson TX2


- Tested Environment (need to build from source):

MacOS
Raspberry Pi 3 ( Ubuntu Mate )  (*viewer application is very slow on raspberry pi)

- Code Language:

C++ ( with other wrappers available like Python , NodeJS etc. )



### 2. Applications and related tools

- hand/head tracking
- body skeleton tracking. [Video demo](https://www.youtube.com/watch?v=gMPtV4NXtUo) and [API Download](http://download.3divi.com/Nuitrack/doc/Installation_page.html#realsense)

- object recognition
- remove background ( like OBS streaming software, do not support D400 Series Depth Cameras for now ) [Video demo1](https://www.youtube.com/watch?v=cxyZDOMviwE) and [Video demo2](https://www.youtube.com/watch?v=wW4HiiksDcU)


### 3. Our project and component

####(1). Removing Background

>**Flow of program:**

`webpage`: capture button
->
`c++ program`: caputure Frame and save to disk
->
fetch distance data and rgb image
->
`python program`
1.one layer of convolution, asign invalid points (zero points) surrounding value
2.make all values to 0s and 1s
3.crop rgb image based on 0s and 1s
-> 
display on web page

>**problems about depth data:**

1. Depth sensor and RGB sensor have different field of view


2. After depth and rgb are aligned, some of distance values are invalid (zero)


![alt text](https://github.com/antonioybw/RealsenseDepthImage/blob/master/img/depth-frame-aligned.png)


3. Choose smaller resolution, less invalid values , but there's still shadow behind objects

![alt text](https://github.com/antonioybw/RealsenseDepthImage/blob/master/img/depth-frame-smaller.png)

4. When too close, the depth data are messed up. (mixed with zero and other higher values)


![alt text](https://github.com/antonioybw/RealsenseDepthImage/blob/master/img/TooClose.png)

---



 >**some useful demos for sdk:**


| Component | Function | notes|
| ------- | ------- | ------- |
| **Realsense Viewer** | real time depth and rgb viewer,  record rosbag file | |
| **Measure** | mesure object distance | |
| **Capture** | capture a frame and display | |
| **Save to disk** | save rgb frame and depth frame | |
| **Align** | align depth and rgb frame (since the two sensors have different field of view) , remove background and display| |



---

**our program: program on mac to save frames in folder for webpage to fetch **


**code snipet:**
`config stream resolution`

```
    rs2::config cfg;
  cfg.enable_stream(RS2_STREAM_INFRARED, 1);
    cfg.enable_stream(RS2_STREAM_INFRARED, 2);
    cfg.enable_stream(RS2_STREAM_DEPTH, 0);
    cfg.enable_stream(RS2_STREAM_COLOR, 0,1280,720);

    rs2::pipeline_profile profile = pipe.start(cfg);
```


`align color and depth frames and get a single frame`

```
    profile = pipe.get_active_profile();
    align_to = find_stream_to_align(profile.get_streams());
    align = rs2::align(align_to);
  auto processed_frameset = align.process(frames);
    rs2::pipeline_profile profile = pipe.start(cfg);

  rs2::depth_frame depth = processed_frameset.get_depth_frame();
    rs2::video_frame color_frame = processed_frameset.get_color_frame();
```


`get distance on a depth frame position/pixel`

```
depth.get_distance(i,j) 
```



#### (2). Recorded Depth File extraction

`rosbag file`：
Recorded file saved by the viewer

`depth frame format`:  mono16

**what can we do from a rosbag file**

`ROS`: (Robot Operating System), often used in the robots and SLAM area
- get meta data 
- color frame
- depth frame
- 
(There are many topics to select from and print out)

[Playback and topic list](https://github.com/IntelRealSense/librealsense/blob/master/src/media/readme.md)



#### (3). Single Depth Completion

>what is detph completion ?
>
>To complete the depth channel of an RGB-D image. 
>Commodity-grade depth cameras often fail to sense depth for shiny, bright, transparent, and distant surfaces

Depth images are smooth on the edges and invalid points could be solved:

*the essential step is to use a larger value to invert distance value, and dilate the image. Afterwards the values need to be inverted again back to original values

![alt text](https://github.com/antonioybw/RealsenseDepthImage/blob/master/img/DepthCompletion.png)


### 4. Reference and papers


- [Image Processing for Basic Depth Completion](https://github.com/kujason/ip_basic)

- [Depth Completion using Deep Learning](http://deepcompletion.cs.princeton.edu)
[paper](http://deepcompletion.cs.princeton.edu/paper.pdf)
[github](https://github.com/yindaz/DeepCompletionRelease)

- <https://www.researchgate.net/publication/301683004_Real-time_tracking_of_rigid_objects_using_depth_data>
- <https://www.intechopen.com/books/motion-tracking-and-gesture-recognition/gesture-recognition-by-using-depth-data-comparison-of-different-methodologies>
- <https://gvv.mpi-inf.mpg.de/files/3DV2013/PersonalizedDepthTracker.pdf>