var utils;
var streaming = false;
var video=null,src=null,dst=null, cap = null, videoInput= null;
var frames = {};
var framedata = {};
var backgrounds = {};
var begin=0;

var camcallback = null;
var cameraType = null;

var cameraReady = function(){
    if(camcallback == null){
        console.log('no callback for camera permission granted. '+camcallback);
        return;
    }

    var startvid = function() {
          onVideoStarted();
          camcallback();
        };

    if(utils == null){
        utils = new Utils();
        utils.loadOpenCv(() => {
            utils.stopCamera();
            video = document.createElement('video');
            video.id = 'videoInput'; video.width = "160px"; video.height = "120px";
            cvresults.append(video);
            utils.startCamera('qvga', startvid, 'videoInput');
        });
    }else{
            utils.stopCamera();
            video = document.createElement('video');
            video.id = 'videoInput'; video.width = "160px"; video.height = "120px";
            cvresults.append(video);
            utils.startCamera('qvga', startvid, 'videoInput');
    }

}
var startCV = function(cam, callback){
    cameraType = cam; //user/environment. front or back cam
    camcallback = callback;
/*    if(typeof JSBridge != 'undefined'){
        if(!JSBridge.isCameraAvailable()){
            JSBridge.getCameraPermission();
            return;
            }
    }*/
    cameraReady();

}

function onVideoStarted() {
    videoInput = document.getElementById('videoInput');
    videoInput.width = videoInput.videoWidth;
    videoInput.height = videoInput.videoHeight;
      streaming = true;
    //setTimeout(processVideo, 0);
}


function stopCV(){
    streaming = false;
    framedata = {};
    frames = {};
}
function processVideo() {
    let video = document.getElementById('videoInput');
    let src = new cv.Mat(video.height, video.width, cv.CV_8UC4);
    let dst = new cv.Mat(video.height, video.width, cv.CV_8UC1);
    let cap = new cv.VideoCapture(video);

    const FPS = 5;


    try {
        if (!streaming) {
            // clean and stop.
            src.delete();
            dst.delete();
            return;
        }
        begin = Date.now();
        // start processing.
        cap.read(src);
        cv.cvtColor(src, dst, cv.COLOR_RGBA2GRAY);

    keypoints  = simpleBlobDetector(src);

    for (const keypoint of keypoints) {
      const center = new cv.Point(keypoint.pt.x, keypoint.pt.y)
      cv.circle(dst, center, keypoint.size, [255, 0, 0, 255], 3)
    }

        cv.imshow('canvasOutput', dst);
        // schedule the next one.
        let delay = 1000/FPS - (Date.now() - begin);
        setTimeout(processVideo, delay);
    } catch (err) {
        utils.printError(err);
    }
};


function getFrame(id, preview, callback) {
    cap = new cv.VideoCapture(video);
    if(preview)
        if(!(id in frames)){
                frames[id] = document.createElement('canvas');
                frames[id].id = id; frames[id].width = 64; frames[id].height = 48;
                cvresults.append(frames[id]);
                console.log(frames[id]);
        }
    framedata[id] = new cv.Mat(video.height, video.width, cv.CV_8UC4);
    cap.read(framedata[id]);
    if(preview)cv.imshow(id, framedata[id]);
    FPS = 10;
    let delay = 1000/FPS - (Date.now() - begin);
    setTimeout(function(){callback(id);}, delay);
    return id;
};


function toGray(id,myid, preview) {
    if(preview)
        if(!(myid in frames)){
            frames[myid] = document.createElement('canvas');
            frames[myid].id = myid; frames[myid].width = 64; frames[myid].height = 48;
            cvresults.append(frames[myid]);
    }
    let dst = new cv.Mat(video.height, video.width, cv.CV_8UC1);
    cv.cvtColor(framedata[id], dst, cv.COLOR_RGBA2GRAY);
    framedata[id] = dst;
    if(preview)cv.imshow(myid, framedata[id]);
    return id;
};

function subtractBG(id,myid, preview) {
    if(preview)
        if(!(myid in frames)){
            frames[myid] = document.createElement('canvas');
            frames[myid].id = myid; frames[myid].width = 64; frames[myid].height = 48;
            cvresults.append(frames[myid]);
    }
    if(!(id in backgrounds)){
            backgrounds[id] = new cv.BackgroundSubtractorMOG2(500, 16, false);
    }
    let fgmask = new cv.Mat(video.height, video.width, cv.CV_8UC1);
    backgrounds[id].apply(framedata[id],fgmask);
    cv.bitwise_not(fgmask, fgmask);
    framedata[id] = fgmask;
    if(preview)cv.imshow(myid, framedata[id]);
    return id;
};



function cv_subtract(id,id2,myid, preview) {
    if(preview)
        if(!(myid in frames)){
            frames[myid] = document.createElement('canvas');
            frames[myid].id = myid; frames[myid].width = 64; frames[myid].height = 48;
            cvresults.append(frames[myid]);
    }
    let fgmask = new cv.Mat(video.height, video.width, cv.CV_8UC1);
    let fgbg = new cv.BackgroundSubtractorMOG2(500, 16, true);
    cv.subtract(framedata[id], framedata[id2], dst, mask, dtype);
    cv.bitwise_not(dst, dst);
    framedata[id] = dst;
    if(preview)cv.imshow(myid, framedata[id]);
    return id;
};

function getBiggestCircle(id,myid, preview) {
    if(preview)
        if(!(myid in frames)){
            frames[myid] = document.createElement('canvas');
            frames[myid].id = myid; frames[myid].width = 64; frames[myid].height = 48;
            cvresults.append(frames[myid]);
    }

    keypoints  = simpleBlobDetector(framedata[id]);
    msg=[0,0,0];
    biggest = 0;
    for (const keypoint of keypoints) {
      if(keypoint.size > biggest){
        msg=[keypoint.pt.x,keypoint.pt.y,keypoint.size];
        biggest  = keypoint.size;
      }
    }
    if(preview)
        if(biggest>0){ // At least one found
            const center = new cv.Point(msg[0], msg[1])
            cv.circle(framedata[id], center, msg[2], [255, 0, 0, 255], 3)
            cv.imshow(myid, framedata[id]);
        }

    return myInterpreter.nativeToPseudo(msg);
};

function getBlobs(id, myid, preview) {
    if(preview)
        if(!(myid in frames)){
            frames[myid] = document.createElement('canvas');
            frames[myid].id = myid; frames[myid].width = 64; frames[myid].height = 48;
            cvresults.append(frames[myid]);
        }

    keypoints  = simpleBlobDetector(framedata[id]);
    msg=[];
    for (const keypoint of keypoints) {
        if(keypoint.size>5){
            blb=[keypoint.pt.x,keypoint.pt.y,keypoint.size];
            const center = new cv.Point(blb[0], blb[1])
            cv.circle(framedata[id], center, blb[2], [0, 0, 0, 255], 2)
            msg.push(blb);
        }
    }
    if(preview)cv.imshow(myid, framedata[id]);
    return myInterpreter.nativeToPseudo(msg);
};
function getLines(id,myid, preview) {
    if(preview)
        if(!(myid in frames)){
            frames[myid] = document.createElement('canvas');
            frames[myid].id = myid; frames[myid].width = 64; frames[myid].height = 48;
            cvresults.append(frames[myid]);
        }
    const grayScaleImage = framedata[id].clone();
    console.log('he');
    let lines = new cv.Mat();
    let color = new cv.Scalar(255, 0, 0);
    cv.Canny(grayScaleImage, grayScaleImage, 50, 200, 3);
    cv.HoughLinesP(grayScaleImage, lines, 1, Math.PI / 180, 2, 0, 0);
    // draw lines
    msg = [];
    for (let i = 0; i < lines.rows; ++i) {
        let startPoint = new cv.Point(lines.data32S[i * 4], lines.data32S[i * 4 + 1]);
        let endPoint = new cv.Point(lines.data32S[i * 4 + 2], lines.data32S[i * 4 + 3]);
        cv.line(framedata[id], startPoint, endPoint, color);
        msg += [lines.data32S[i * 4], lines.data32S[i * 4 + 1],lines.data32S[i * 4 + 2], lines.data32S[i * 4 + 3] ];
    }
    if(preview)cv.imshow(myid, framedata[id]);
    grayScaleImage.delete(); lines.delete();
    return msg;

};


function Utils() { // eslint-disable-line no-unused-vars
    let self = this;

    const OPENCV_URL = 'cv/opencv4.5.js';
    this.loadOpenCv = function(onloadCallback) {
        let script = document.createElement('script');
        script.setAttribute('async', '');
        script.setAttribute('type', 'text/javascript');
        script.addEventListener('load', async () => {
            if (cv.getBuildInformation)
            {
                console.log(cv.getBuildInformation());
                onloadCallback();
            }
            else
            {
                // WASM
                if (cv instanceof Promise) {
                    cv = await cv;
                    console.log(cv.getBuildInformation());
                    onloadCallback();
                } else {
                    cv['onRuntimeInitialized']=()=>{
                        console.log(cv.getBuildInformation());
                        onloadCallback();
                    }
                }
            }
        });
        script.addEventListener('error', () => {
            self.printError('Failed to load ' + OPENCV_URL);
        });
        script.src = OPENCV_URL;
        let node = document.getElementsByTagName('script')[0];
        node.parentNode.insertBefore(script, node);
    };


    this.printError = function(err) {
        console.log(err);
    };


    function onVideoCanPlay() {
        if (self.onCameraStartedCallback) {
            self.onCameraStartedCallback(self.stream, self.video);
        }
    };

    this.startCamera = function(resolution, callback, videoId) {

        const constraints = {
            'qvga': {width: {exact: 320}, height: {exact: 240}, facingMode: cameraType},
            'vga': {width: {exact: 640}, height: {exact: 480}}, facingMode: cameraType};
        let video = document.getElementById(videoId);
        if (!video) {
            video = document.createElement('video');
        }

        let videoConstraint = constraints[resolution];
        if (!videoConstraint) {
            videoConstraint = true;
        }



        navigator.mediaDevices.getUserMedia({video: videoConstraint, audio: false})
            .then(function(stream) {
                video.srcObject = stream;
                video.play();
                self.video = video;
                self.stream = stream;
                self.onCameraStartedCallback = callback;
                video.addEventListener('canplay', onVideoCanPlay, false);
            })
            .catch(function(err) {
                self.printError('Camera Error: ' + err.name + ' ' + err.message);
            });
    };

    this.stopCamera = function() {
        if (this.video) {
            this.video.pause();
            this.video.srcObject = null;
            this.video.removeEventListener('canplay', onVideoCanPlay);
        }
        if (this.stream) {
            this.stream.getVideoTracks()[0].stop();
        }
    };
};


// Port of https://github.com/opencv/opencv/blob/a50a355/modules/features2d/src/blobdetector.cpp
// By https://gist.github.com/janpaul123/8b9061d1d093ec0b36dac2230434d34a 
// But with special `faster` option which has slightly different semantics,
// but is a whole bunch faster.

function diff(v1, v2) {
  if (v1.x !== undefined) return { x: v1.x - v2.x, y: v1.y - v2.y };
  return v1.map((value, index) => value - v2[index]);
}

function norm(vector) {
  if (vector.x !== undefined) return norm([vector.x, vector.y]);
  return Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0));
}

var defaultParams = {
  thresholdStep: 10,
  minThreshold: 20,
  maxThreshold: 240,
  minRepeatability: 2,
  minDistBetweenBlobs: 10,

  filterByColor: true,
  blobColor: 0,

  filterByArea: true,
  minArea: 25,
  maxArea: 5000,

  filterByCircularity: false,
  minCircularity: 0.8,
  maxCircularity: 1000000,

  filterByInertia: false,
  //minInertiaRatio: 0.6,
  minInertiaRatio: 0.1,
  maxInertiaRatio: 1000000,

  filterByConvexity: true,
  //minConvexity: 0.8,
  minConvexity: 0.90,
  maxConvexity: 1000000,

  faster: true,
};

function setParam(p, val){
    defaultParams[p] = val;
    console.log(defaultParams[p]);
}

function findBlobs(image, binaryImage, params) {
  const contours = new cv.MatVector();
  const hierarchy = new cv.Mat();
  if (params.faster) {
    cv.findContours(binaryImage, contours, hierarchy, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE);
  } else {
    cv.findContours(binaryImage, contours, hierarchy, cv.RETR_LIST, cv.CHAIN_APPROX_NONE);
  }
  hierarchy.delete();

  const centers = [];
  const objectsToDelete = [];
  for (let i = 0; i < contours.size(); i++) {
    const contour = contours.get(i);
    objectsToDelete.push(contour);
    const area = cv.contourArea(contour);

    if (area == 0) continue;

    let center, moms;
    if (params.faster) {
      const { x, y, width, height } = cv.boundingRect(contour);
      center = {
        confidence: 1,
        location: { x: x + width / 2, y: y + height / 2 },
        radius: (width + height) / 4,
      };
    } else {
      moms = cv.moments(contour);
      center = {
        confidence: 1,
        location: { x: moms.m10 / moms.m00, y: moms.m01 / moms.m00 },
      };
    }

    if (params.filterByArea) {
      if (area < params.minArea || area >= params.maxArea) continue;
    }

    if (params.filterByCircularity) {
      const perimeter = cv.arcLength(contour, true);
      const ratio = 4 * cv.CV_PI * area / (perimeter * perimeter);
      if (ratio < params.minCircularity || ratio >= params.maxCircularity) continue;
    }

    if (params.filterByInertia) {
      if (params.faster) {
        throw new Error('Cannot both set params.faster and params.filterByInertia');
      }

      const denominator = Math.sqrt(
        Math.pow(2 * moms.mu11, 2) + Math.pow(moms.mu20 - moms.mu02, 2)
      );
      let ratio;
      if (denominator > 0.01) {
        const cosmin = (moms.mu20 - moms.mu02) / denominator;
        const sinmin = 2 * moms.mu11 / denominator;
        const cosmax = -cosmin;
        const sinmax = -sinmin;

        const imin =
          0.5 * (moms.mu20 + moms.mu02) -
          0.5 * (moms.mu20 - moms.mu02) * cosmin -
          moms.mu11 * sinmin;
        const imax =
          0.5 * (moms.mu20 + moms.mu02) -
          0.5 * (moms.mu20 - moms.mu02) * cosmax -
          moms.mu11 * sinmax;
        ratio = imin / imax;
      } else {
        ratio = 1;
      }

      if (ratio < params.minInertiaRatio || ratio >= params.maxInertiaRatio) continue;

      center.confidence = ratio * ratio;
    }

    if (params.filterByConvexity) {
      const hull = new cv.Mat();
      cv.convexHull(contour, hull);
      const hullArea = cv.contourArea(hull);
      const ratio = area / hullArea;
      hull.delete();
      if (ratio < params.minConvexity || ratio >= params.maxConvexity) continue;
    }

    if (params.filterByColor) {
      if (
        binaryImage.ucharAt(Math.round(center.location.y), Math.round(center.location.x)) !=
        params.blobColor
      )
        continue;
    }

    if (!params.faster) {
      const dists = [];
      for (let pointIdx = 0; pointIdx < contour.size().height; pointIdx++) {
        const pt = contour.intPtr(pointIdx);
        dists.push(norm(diff(center.location, { x: pt[0], y: pt[1] })));
      }
      dists.sort();
      center.radius =
        (dists[Math.floor((dists.length - 1) / 2)] + dists[Math.floor(dists.length / 2)]) / 2;
    }

    centers.push(center);
  }
  objectsToDelete.forEach(obj => obj.delete());
  contours.delete();
  return centers;
}

function simpleBlobDetector(grayScaleImage, params) {
  params = { ...defaultParams, ...params };

  let centers = [];
  for (
    let thresh = params.minThreshold;
    thresh < params.maxThreshold;
    thresh += params.thresholdStep
  ) {
    const binaryImage = new cv.Mat(grayScaleImage.rows, grayScaleImage.cols, cv.CV_8UC1);
    cv.threshold(grayScaleImage, binaryImage, thresh, 255, cv.THRESH_BINARY);
    let curCenters = findBlobs(grayScaleImage, binaryImage, params);
    binaryImage.delete();
    let newCenters = [];

    for (let i = 0; i < curCenters.length; i++) {
      let isNew = true;
      for (let j = 0; j < centers.length; j++) {
        const dist = norm(
          diff(centers[j][Math.floor(centers[j].length / 2)].location, curCenters[i].location)
        );
        isNew =
          dist >= params.minDistBetweenBlobs &&
          dist >= centers[j][Math.floor(centers[j].length / 2)].radius &&
          dist >= curCenters[i].radius;
        if (!isNew) {
          centers[j].push(curCenters[i]);

          let k = centers[j].length - 1;
          while (k > 0 && centers[j][k].radius < centers[j][k - 1].radius) {
            centers[j][k] = centers[j][k - 1];
            k--;
          }
          centers[j][k] = curCenters[i];
          break;
        }
      }
      if (isNew) newCenters.push([curCenters[i]]);
    }
    centers = centers.concat(newCenters);
  }

  //grayScaleImage.delete();

  const keyPoints = [];
  for (let i = 0; i < centers.length; i++) {
    if (centers[i].length < params.minRepeatability) continue;
    const sumPoint = { x: 0, y: 0 };
    let normalizer = 0;
    for (let j = 0; j < centers[i].length; j++) {
      sumPoint.x += centers[i][j].confidence * centers[i][j].location.x;
      sumPoint.y += centers[i][j].confidence * centers[i][j].location.y;
      normalizer += centers[i][j].confidence;
    }
    sumPoint.x *= 1 / normalizer;
    sumPoint.y *= 1 / normalizer;
    let size = Math.round(centers[i][Math.floor(centers[i].length / 2)].radius * 2);
    size = Math.min(
      size,
      sumPoint.x * 2,
      sumPoint.y * 2,
      (grayScaleImage.cols - sumPoint.x) * 2,
      (grayScaleImage.rows - sumPoint.y) * 2
    );
    keyPoints.push({ pt: sumPoint, size });
  }

  return keyPoints;
}




/*---Start the camera----*/
Blockly.Blocks['start_camera'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Start Camera(Beta)")
        .appendField(new Blockly.FieldDropdown([["FRONT","user"],["BACK","environment"]]), "CAMERA");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(52);
 this.setTooltip("Start Camera");
 this.setHelpUrl("");
  }
};



Blockly.JavaScript['start_camera'] = function(block) {
  var cam = block.getFieldValue("CAMERA");
  var code = "startCV('"+cam+"');\n";
  return code;
};


Blockly.Python['start_camera'] = function(block) {
  var code = '# Camera Not implemented in Python\n';
  return code;
};

/*---Start the camera----*/
Blockly.Blocks['choose_blob_shade'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Blob Colour is ")
        .appendField(new Blockly.FieldDropdown([["BLACK","0"],["WHITE","1"]]), "SHADE");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(52);
 this.setTooltip("Start Camera");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['choose_blob_shade'] = function(block) {
  var shade = block.getFieldValue("SHADE");
  var code = "set_param('blobColor',"+parseInt(shade)+");\n";
  return code;
};

Blockly.Python['choose_blob_shade'] = function(block) {
  var code = '';
  return code;
};


Blockly.Blocks['get_frame'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Get Frame");
    this.appendDummyInput()
        .appendField(new Blockly.FieldCheckbox("FALSE"), "PREVIEW")
        .appendField("Preview");
    this.setOutput(true);
    this.setColour(52);
 this.setTooltip("Get a single frame from the camera");
 this.setInputsInline(false);
 this.setHelpUrl("");
  }
};



Blockly.JavaScript['get_frame'] = function(block) {
  var pv = block.getFieldValue('PREVIEW')=='TRUE' ? true:false;
  console.log(block.id);
  var code = "get_frame('"+block.id+"',"+pv+")";
  return [code,Blockly.JavaScript.ORDER_NONE];
};
Blockly.Python['get_frame'] = function(block) {  return '# Camera Not implemented in Python\n'; };

// To Grayscale
Blockly.Blocks['to_gray'] = {
  init: function() {
    this.appendValueInput("ID")
        .appendField("To Grayscale. Frame:");
    this.appendDummyInput()
        .appendField(new Blockly.FieldCheckbox("FALSE"), "PREVIEW")
        .appendField("Preview");
    this.setOutput(true);
    this.setColour(52);
 this.setInputsInline(false);
 this.setTooltip("convert frame to gray");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['to_gray'] = function(block) {
  var id = Blockly.JavaScript.valueToCode(block, 'ID', Blockly.JavaScript.ORDER_NONE);
  var pv = block.getFieldValue('PREVIEW')=='TRUE' ? true:false;
  var code = "to_gray("+id+",'"+block.id+"',"+pv+")";
  return [code,Blockly.JavaScript.ORDER_NONE];
};
Blockly.Python['to_gray'] = function(block) {  return ''; };

// Subtract Background
Blockly.Blocks['subtract_bg'] = {
  init: function() {
    this.appendValueInput("ID")
        .appendField("Subtract Background from:");
    this.appendDummyInput()
        .appendField("MOG2 Algorithm");
    this.appendDummyInput()
        .appendField(new Blockly.FieldCheckbox("FALSE"), "PREVIEW")
        .appendField("Preview");
    this.setOutput(true);
    this.setColour(52);
 this.setInputsInline(false);
 this.setTooltip("subtract background");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['subtract_bg'] = function(block) {
  var id = Blockly.JavaScript.valueToCode(block, 'ID', Blockly.JavaScript.ORDER_NONE);
  var pv = block.getFieldValue('PREVIEW')=='TRUE' ? true:false;
  var code = "subtract_bg("+id+",\""+block.id+"\","+pv+")";
  return [code,Blockly.JavaScript.ORDER_NONE];
};
Blockly.Python['subtract_bg'] = function(block) {  return ''; };

// SUBTRACT FRAMES
Blockly.Blocks['cv_subtract'] = {
  init: function() {
    this.appendValueInput("ID")
        .appendField("From Frame1:");
    this.appendValueInput("ID2")
        .appendField("Subtract Frame2:");
    this.appendDummyInput()
        .appendField("Store mask to Frame1");
    this.appendDummyInput()
        .appendField(new Blockly.FieldCheckbox("FALSE"), "PREVIEW")
        .appendField("Preview");
    this.setOutput(true);
    this.setColour(52);
 this.setInputsInline(false);
 this.setTooltip("Background Subtraction");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['cv_subtract'] = function(block) {
  var id = Blockly.JavaScript.valueToCode(block, 'ID', Blockly.JavaScript.ORDER_NONE);
  var id2 = Blockly.JavaScript.valueToCode(block, 'ID2', Blockly.JavaScript.ORDER_NONE);
  var pv = block.getFieldValue('PREVIEW')=='TRUE' ? true:false;
  var code = "cv_subtract("+id+","+id2+",'"+block.id+"',"+pv+")";
  return [code,Blockly.JavaScript.ORDER_NONE];
};
Blockly.Python['cv_subtract'] = function(block) {  return ''; };



// GET BLOBS
Blockly.Blocks['get_blobs'] = {
  init: function() {
    this.appendValueInput("ID")
        .appendField("Get Blobs. Frame: ");
    this.appendDummyInput()
        .appendField(new Blockly.FieldCheckbox("FALSE"), "PREVIEW")
        .appendField("Preview");
    this.setOutput(true, null);
    this.setColour(52);
 this.setTooltip("get blobs");
 this.setInputsInline(false);
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['get_blobs'] = function(block) {
  var id = Blockly.JavaScript.valueToCode(block, 'ID', Blockly.JavaScript.ORDER_NONE);
  var pv = block.getFieldValue('PREVIEW')=='TRUE' ? true:false;
  var code = "get_blobs("+id+",\""+block.id+"\","+pv+")";
  return [code,Blockly.JavaScript.ORDER_NONE];
};
Blockly.Python['get_blobs'] = function(block) {    return ['', Blockly.Python.ORDER_NONE];  };


Blockly.Blocks['get_biggest_circle'] = {
  init: function() {
    this.appendValueInput("ID")
        .appendField("Biggest Circle: ");
    this.appendDummyInput()
        .appendField(new Blockly.FieldCheckbox("FALSE"), "PREVIEW")
        .appendField("Preview");
    this.appendDummyInput()
        .appendField("Returns X,Y,Radius");
    this.setOutput(true, null);
    this.setColour(52);
 this.setTooltip("get circle");
 this.setInputsInline(false);
 this.setHelpUrl("");
  }
};



Blockly.JavaScript['get_biggest_circle'] = function(block) {
  var id = Blockly.JavaScript.valueToCode(block, 'ID', Blockly.JavaScript.ORDER_NONE);
  var pv = block.getFieldValue('PREVIEW')=='TRUE' ? true:false;
  var code = "get_biggest_circle("+id+",\""+block.id+"\","+pv+")";
  return [code,Blockly.JavaScript.ORDER_NONE];
};
Blockly.Python['get_biggest_circle'] = function(block) {    return ['', Blockly.Python.ORDER_NONE];  };


Blockly.Blocks['get_lines'] = {
  init: function() {
    this.appendValueInput("ID")
        .appendField("Get Lines ");
    this.appendDummyInput()
        .appendField(new Blockly.FieldCheckbox("FALSE"), "PREVIEW")
        .appendField("Preview");
    this.setOutput(true, null);
    this.setColour(52);
 this.setTooltip("get lines");
 this.setInputsInline(false);
 this.setHelpUrl("");
  }
};



Blockly.JavaScript['get_lines'] = function(block) {
  var id = Blockly.JavaScript.valueToCode(block, 'ID', Blockly.JavaScript.ORDER_NONE);
  var pv = block.getFieldValue('PREVIEW')=='TRUE' ? true:false;
  var code = "get_lines("+id+",\""+block.id+"\","+pv+")";
  return [code,Blockly.JavaScript.ORDER_NONE];
};
Blockly.Python['get_lines'] = function(block) {    return ['', Blockly.Python.ORDER_NONE];  };



function initCV(interpreter, scope) {

		  interpreter.setProperty(scope, 'startCV', interpreter.createAsyncFunction(
                        function(cam,callback) {
                              startCV(cam,callback);
                            })
                        );

		  interpreter.setProperty(scope, 'get_frame', interpreter.createAsyncFunction(
                        function(id,preview,callback) {
                              return getFrame(id,preview, callback);
                            })
                        );
		  interpreter.setProperty(scope, 'set_param', interpreter.createNativeFunction(
                        function(p,val) {
                              return setParam(p,val);
                            })
                        );

		  interpreter.setProperty(scope, 'to_gray', interpreter.createNativeFunction(
                        function(id,myid,preview) {
                              return toGray(id,myid,preview);
                            })
                        );
		  interpreter.setProperty(scope, 'subtract_bg', interpreter.createNativeFunction(
                        function(id,myid,preview) {
                              return subtractBG(id,myid,preview);
                            })
                        );
		  interpreter.setProperty(scope, 'cv_subtract', interpreter.createNativeFunction(
                        function(id,id2,myid,preview) {
                              return cv_subtract(id,id2, myid,preview);
                            })
                        );
		  interpreter.setProperty(scope, 'get_lines', interpreter.createNativeFunction(
                        function(id,myid,preview) {
                              return getLines(id,myid,preview);
                            })
                        );
		  interpreter.setProperty(scope, 'get_blobs', interpreter.createNativeFunction(
                        function(id, myid,preview) {
                              return getBlobs(id, myid,preview);
                            })
                        );

		  interpreter.setProperty(scope, 'get_biggest_circle', interpreter.createNativeFunction(
                        function(id,myid,preview) {
                              return getBiggestCircle(id,myid,preview);
                            })
                        );

	}










