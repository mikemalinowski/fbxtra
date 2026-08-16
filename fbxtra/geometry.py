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


# --------------------------------------------------------------------------------------
def get_mesh_nodes(fbx_scene):
    """
    Returns the FbxNode of every mesh in the scene.

    :param fbx_scene: The scene to search within
    :type fbx_scene: fbx.FbxScene

    :return: list(fbx.FbxNode, ...)
    """
    results = list()

    # -- Walk the node hierarchy rather than the flat document object list, so
    # -- that cloned/merged nodes (which are connected into the graph but not
    # -- the document object list) are still found.
    for node_ in node.get_children(fbx_scene.GetRootNode(), recursive=True):
        if node_.GetMesh():
            results.append(node_)

    return results


# --------------------------------------------------------------------------------------
def get_mesh_node(fbx_scene, name):
    """
    Returns the FbxNode of the mesh with the given name, or None.

    :param fbx_scene: The scene to search within
    :type fbx_scene: fbx.FbxScene

    :param name: The name of the mesh's transform node
    :type name: str

    :return: fbx.FbxNode or None
    """
    for node_ in get_mesh_nodes(fbx_scene):
        if node_.GetName() == name:
            return node_

    return None


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
