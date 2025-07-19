import fbx

from . import scene
from . import node
from . import manager


# --------------------------------------------------------------------------------------
def freeze(fbx_node):
    if not fbx_node.GetGeometry():
        return

    fbx_node.ResetPivotSet(fbx_node.eSourcePivot)

    matrix = fbx_node.EvaluateLocalTransform()
    fbx_node.GetGeometry().SetPivot(matrix)
    node.zero(fbx_node)


# ----------------------------------------------------------------------------------------------------------------------
def merge_all(fbx_scene):
    """
    Merges all the meshes in the scene

    :return: fbx.FbxNode
    """
    # -- Create an array of all the meshes we want to merge
    mesh_nodes = fbx.FbxNodeArray()

    for node_ in scene.get_all(fbx_scene):
        if isinstance(node_, fbx.FbxMesh):
            mesh_nodes.Add(node_.GetNode())

    # -- Merge the meshes into a new node
    merged_mesh = fbx.FbxGeometryConverter(manager.get()).MergeMeshes(
        mesh_nodes,
        "MergedMesh",
        fbx_scene,
    )

    # -- Add the new node to the scene hierarchy
    fbx_scene.GetRootNode().AddChild(merged_mesh)

    # -- Destroy all the original meshes
    for mesh_node in mesh_nodes:
        mesh_node.Destroy()

    return merged_mesh
