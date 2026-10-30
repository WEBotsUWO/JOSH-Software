# Vector Navigation plan

[Back to the team list](../README.md)

## What SLAM gives us

A map of points and a pose for the camera at each keyframe, including loop closure when the camera revisits a place. That is the job of `monovslam` in Computer Vision Toolbox. We use that object. A custom `poseGraph` or `factorGraph` is out of scope this semester.

`stereovslam` and `rgbdvslam` are the same family for stereo and RGB-D. They wait on hardware we do not have. `lidarSLAM` waits on a range sensor. `slamMapBuilder` is the interactive app for clicking through loop closures once. The pipeline is `monovslam`.

## Heading comes after the map

The team builds a heading the humanoid can walk along. SLAM supplies where things are and where the camera is. The heading is step 6, a planner on an occupancy slice of that map:

- A potential field: goal attracts, obstacles repel, the gradient is the direction.
- A vector field histogram: `controllerVFH` in Navigation Toolbox bins obstacles and picks a free sector.

The pasted `artificialPotentialField` script is not verified against a toolbox release. Step 6 starts from the Navigation Toolbox page for the MATLAB version on the machine, then writes a short script whose only output is a heading.

A humanoid cannot take that heading as a wheel speed. Locomotion turns it into footsteps. This folder stops at the heading.

## Scale

Monocular SLAM is up to a scale factor. A pose of `[1 0 0]` might be one meter or three. Step 3's output note has to say that. Metric scale needs a known object, depth, or stereo. Until then, RL can use the direction of the heading more safely than its length.

## 2D and 3D

`monovslam` estimates a 3-D camera trajectory. Walking wants a heading in the floor plane. Step 5 flattens the cloud into a 2-D occupancy slice. Step 6's heading is 2-D in that slice, not a 3-D velocity.

## Calls that exist

On `monovslam`: `addFrame`, `checkStatus`, `hasNewKeyFrame`, `isDone`, `mapPoints`, `poses`, `plot`.

`addFrame` accepts RGB or grayscale and returns before the frame is finished. Read `mapPoints` and `poses` after `isDone`. There is no `mapPointsAndPoses` method. The example in `examples/monocular_vslam.m` follows that.
