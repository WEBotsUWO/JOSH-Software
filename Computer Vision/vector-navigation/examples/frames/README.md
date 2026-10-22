# Frames

Put an ordered image sequence here (`.jpg`, `.jpeg`, `.png`, or `.bmp`).

[monocular_vslam.m](../monocular_vslam.m) reads this folder. One camera, moving through a room, is enough for a first run. A single snapshot will not initialize a map.

The script's intrinsics assume 640-by-480. If your frames are another size, edit `imageSize`, `focal`, and `principal` in the script before running. Label those numbers assumed until someone calibrates the camera.
