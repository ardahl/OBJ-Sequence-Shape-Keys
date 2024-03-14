# OBJ-Sequence-Shape-Keys
Import a sequence of OBJ files in Blender as a set of keyframed shape keys

Heavily based on [Stop Motion OBJ](https://github.com/neverhood311/Stop-motion-OBJ), this imports the obj sequence as shape keys instead.

The first mesh in the sequence is used as the base. Each frame is then read in as a per-vertex translation from the base and put into a shape key. Each shape key is keyframed so only the ith shape key is active for the ith frame.

## Installation
Clone the repo for the script, then follow the normal addon procedure. Go to Edit -> Preferences -> Addons, then click Install and navigate to the script location.
