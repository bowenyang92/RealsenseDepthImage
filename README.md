
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

1. Removing Background

c++ program: `caputure Frame and save to disk`
