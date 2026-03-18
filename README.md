This is a utility module to make it a little easier to interact with 
FbxScenes and objects. It offers high level functionality to tasks
which are common place when working with the Fbx SDK.

This module assumes you already have the standard fbx module - which
is available from here: 

    https://www.autodesk.com/developer-network/platform-technologies/fbx-sdk-2019-0

Alternatively, there is a pre-compiled version that works with Maya 2026 within 
this repository.

This module is particularly useful if you're exporting an fbx out of an 
application such as Maya, Blender or 3dsmax. Instead of modifying the users
scene we can instead do a greedy export and then use the fbx sdk to clean 
the fbx. This way we're not being destructive to the users environment.

```python
import fbxtra

fbx_path = "your path to an fbx file"

# -- Load the fbx file 
fbx_scene = fbxtra.files.load(fbx_path)

# -- Remove namespaces
fbxtra.scene.clear_namespaces(fbx_scene)

# -- Get the skeleton root and make it a child of the scene root
skeletal_root_name = "RootBone"
fbx_skeletal_root = fbxtra.scene.get(fbx_scene, name=skeletal_root_name)
fbxtra.node.set_parent(fbx_skeletal_root, parent=None)

# -- Remove all items that are not part of the skeleton
fbxtra.scene.clear(fbx_scene, excluding=[fbx_skeletal_root])

# -- Remove animation on the skeletal root (much like removing
# -- root motion)
fbxtra.animation.remove_tr_keys(
    fbx_skeletal_root,
    zero=True,
)

# -- Ensure the time frame is specifically set in the fbx file
fbxtra.animation.set_time_range(
    fbx_scene,
    start_frame=10,
    end_frame=100,
)

# -- Name the take according to the file name, removing the
# -- suffix
fbxtra.animation.set_current_take_name(
    fbx_scene,
    "example_take",
)

# -- Finally, save the fbx file
fbxtra.files.save(fbx_scene, fbx_path)
```

You can also use fbxtra to quickly get access to things like document properties
in order to look up where an fbx was exported from:

```python
import fbxtra

# -- Load the fbx 
path = r"path to your fbx file"
scene = fbxtra.files.load(path)

# -- If the fbx was exported from maya then this would return the 
# -- .ma or .mb file it was exported from for instance.
filepath_exported_from = fbxtra.document.get_property(scene, "ApplicationNativeFile")
print(filepath_exported_from)
```

Finally, here is an example of easily traversing and interacting with the 
scene

```python
import fbxtra

# -- Load the fbx
path = r"your fbx file path"
scene = fbxtra.files.load(path)

# -- Read the root nodes and then the first children
for node in fbxtra.scene.get_top_level(scene):
    node_name = node.GetName()

    children = [
        child.GetName()
        for child in fbxtra.node.get_children(node)
    ]
    print(f"{node_name} : {children}")

# -- We can also easily get all the nodes in the scene
for node in fbxtra.scene.get_all(scene):
    print(node.GetName())

```