"""
This is a utility module to make it a little easier to interact with 
FbxScenes and objects. It offers high level functionality to tasks
which are common place when working with the Fbx SDK.

This module assumes you already have the standard fbx module - which
is available from here: 

    https://www.autodesk.com/developer-network/platform-technologies/fbx-sdk-2019-0


"""
# -- Import fbx as a wildcard, allowing users to import
# -- fbxtra without having to also import fbx
from fbx import *

# -- Now import our own higher level modules
from . import animation
from . import constants
from . import files
from . import manager
from . import node
from . import scene
