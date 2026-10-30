% Minimal monocular visual SLAM on a folder of frames.
% Vector Navigation step 3, in miniature. See ../README.md.
%
% Requires Computer Vision Toolbox (monovslam, cameraIntrinsics, imageDatastore).
% From R2025a, monovslam also runs under Navigation Toolbox when that
% Computer Vision Toolbox license is present.
%
% Outputs: sparse 3-D map points and keyframe poses.
% Scale is not meters. A walking direction is step 6, not this script.
% addFrame accepts RGB. The loop converts to grayscale so the input is obvious.
% addFrame returns before the frame is finished, so mapPoints and poses
% are read only after isDone.

framesDir = fullfile(fileparts(mfilename("fullpath")), "frames");
if ~isfolder(framesDir)
    error("monocular_vslam:NoFrames", ...
        "Put images in %s and run again.", framesDir);
end

imds = imageDatastore(framesDir, FileExtensions={'.jpg', '.jpeg', '.png', '.bmp'});
if isempty(imds.Files)
    error("monocular_vslam:NoFrames", ...
        "No jpg or png frames in %s.", framesDir);
end

% Assumed intrinsics for 640-by-480 frames. Replace after calibration.
% imageSize is [height width] and must match the frames.
focal = [700 700];
principal = [320 240];
imageSize = [480 640];

first = readimage(imds, 1);
if size(first, 1) ~= imageSize(1) || size(first, 2) ~= imageSize(2)
    error("monocular_vslam:ImageSize", ...
        "Frames are %d-by-%d. Intrinsics assume %d-by-%d. Edit imageSize, focal, and principal.", ...
        size(first, 1), size(first, 2), imageSize(1), imageSize(2));
end

intrinsics = cameraIntrinsics(focal, principal, imageSize);
vslam = monovslam(intrinsics);

for i = 1:numel(imds.Files)
    frame = readimage(imds, i);
    if size(frame, 3) == 3
        frame = rgb2gray(frame);
    end

    addFrame(vslam, frame);

    if hasNewKeyFrame(vslam)
        plot(vslam);
        drawnow limitrate
    end

    status = checkStatus(vslam);
    fprintf("Frame %d status: %s\n", i, char(string(status)));
end

while ~isDone(vslam)
    if hasNewKeyFrame(vslam)
        plot(vslam);
        drawnow limitrate
    end
    pause(0.01);
end

xyzPoints = mapPoints(vslam);
[camPoses, keyFrameIDs] = poses(vslam);

fprintf("Map points: %d\n", size(xyzPoints, 1));
fprintf("Keyframes: %d\n", numel(keyFrameIDs));
fprintf("Scale is not metric. Coordinates are up to a scale factor.\n");
