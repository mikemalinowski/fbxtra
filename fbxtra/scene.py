"""
Functionality for accessing and altering data within an FBXScene
"""
import fbx

from . import node as _node


# --------------------------------------------------------------------------
def get(scene, name):
    """
    Gives direct access to the fbx.FbxObject with the given
    name. If none exists then None will be returned/

    :param scene: The fbx.FbxScene to search within
    :type scene: fbx.FbxScene

    :param name: The name of the fbx object you want to get
    :type name: str

    :return: fbx.FbxObject
    """
    for fbx_object in get_all(scene):
        if fbx_object.GetName() == name:
            return fbx_object

    return None


# --------------------------------------------------------------------------
def get_top_level(scene):
    """
    Returns all the FbxNodes in the scene which are direct children of the scene
    root.
    
    :param scene: The fbx.FbxScene to search within
    :type scene: fbx.FbxScene
    
    :return list(fbx.FbxNode)
    """
    results = list()
    
    for node in of_type(scene, fbx.FbxNode):
        
        if node.GetParent():
            continue
        
        results.append(node)
    
    return results


# --------------------------------------------------------------------------
def get_all(scene):
    """
    Returns all the objects within the FbxScene.

    :param scene: The scene to get a list of objects from
    :type scene: fbx.FbxScene

    :return: list of fbx.FbxObject
    """
    objects = []
    object_count = scene.RootProperty.GetSrcObjectCount()

    # -- Loop through the root property and get the node for each index
    for idx in range(object_count):
        fbx_object = scene.RootProperty.GetSrcObject(idx)

        if fbx_object:
            objects.append(fbx_object)

    return objects


# --------------------------------------------------------------------------
def of_type(scene, required_type):
    """
    Returns all the nodes of the given type.

    :param scene: The scene which the search should occur
    :type scene: fbx.FbxScene

    :param required_type: The type name to search for
    :type required_type: str or fbx class

    :return: List of nodes of the given type
    """
    # -- Define a list to add all our matches
    # -- to
    matched = list()

    # -- Get a list of all the objects in the scene
    object_count = scene.RootProperty.GetSrcObjectCount()

    for idx in range(object_count):
        node = scene.RootProperty.GetSrcObject(idx)

        # -- If the node is valid, and the type matches
        # -- the required type then we scoop it
        if isinstance(required_type, str):
            if node and node.GetTypeName() == required_type:
                matched.append(node)

        else:
            if isinstance(node, required_type):
                matched.append(node)

    # -- Return all the matches
    return matched


# --------------------------------------------------------------------------
def children(scene, recursive=False):
    """
    Returns a list of all the children in the scene

    :param scene: The scene to look within for the child nodes
    :type scene: fbx.FbxScene

    :param recursive: If True then all the children and their
        sub-children will be returned. If False then only the
        scenes top level children will be returned.

    :return: list(fbx.FbxNode, ...)
    """
    return _node.get_children(scene.GetRootNode(), recursive=recursive)


# --------------------------------------------------------------------------
def clear_namespaces(scene, nodes=None):
    """
    Clears away the namespace from the given nodes. Where no nodes
    are passed then the namespace is removed from all fbx objects
    within the scene.

    :param scene: The scene to remove the namespace from
    :type scene : fbx.FbxScene

    :param nodes: Optional. List of nodes to remove the namespace from. If
        this is not given then the namespace will be removed from all nodes.
    :type nodes: fbx.FbxNode
    """

    # -- If we're not given any nodes then we need to get a list
    # -- of all the nodes in the scene
    nodes = nodes or get_all(scene)

    # -- Cycle over all our nodes
    for node in nodes:

        # -- Extract the name of the node so we can inspect it
        node_name = node.GetName()
        name_parts = node_name.split(":")

        # -- If we have more than one part then the node has a namespace
        # -- so we should remove it
        node.SetName(name_parts[-1])


# --------------------------------------------------------------------------
def clear(scene, excluding=None):
    """
    This will remove all the FbxNode elements from the scene apart
    from any nodes given in the excluding argument. Any children
    of any nodes given in that argument will also be preserved.

    :param scene: The scene to clear
    :type scene: fbx.FbxScene

    :param excluding: A list of fbx.FbxNode's which should be
        omitted from the scene clearing process.
    :type excluding: list(fbx.FbxNode, ...)

    :return: None
    """
    node_names = list()

    # -- Start by moving any nodes which we want to exclude from the
    # -- clearing process to the scene root
    for (
        idx,
        node,
    ) in enumerate(excluding):

        # -- Ensure we're working with Fbx objects
        if not isinstance(node, fbx.FbxObject):
            node = get(scene, node)
            excluding[idx] = node

        # -- From this point on we're going to deal with names
        # -- so lets switch to that
        node_names.append(node.GetName())

    for node in excluding:

        # -- Move the item to the highest level node which is expected
        # -- to be protected from the clearing
        all_parents = _node.get_parents(node)
        node_to_reparent = node

        for parent in all_parents:
            if parent.GetName() not in node_names:
                _node.set_parent(node_to_reparent, None)

                break

            node_to_reparent = parent

            # -- We now need to cycle over all the root nodes
    # -- in the scene
    for top_level_node in children(scene, recursive=False)[:]:

        # -- if root node in preserve list then we need to delete it
        if top_level_node.GetName() in node_names:
            continue

        # -- Find all the nodes under the current child which
        # -- we need to remove, then reverse the order so we're
        # -- deleting from the leaf level up
        all_child_nodes = _node.get_children(top_level_node, recursive=True)
        all_child_nodes.reverse()

        # -- As well as the children we need to make
        # -- sure we remove this root node too
        all_child_nodes.append(top_level_node)

        for node_to_remove in all_child_nodes:
            # -- Remove the node and then ask for it to be
            # -- destroyed.
            scene.RemoveNode(node_to_remove)
            node_to_remove.Destroy()


# --------------------------------------------------------------------------
def delete_node(scene, node=None):
    """
    This will remove a given node from the scene including its children

    :param scene: The scene to clear
    :type scene: fbx.FbxScene

    :param node: A single node
    :type node: fbx.FbxNode

    :return: None
    """
    if not node:
        return

    # -- Ensure we're working with Fbx objects
    if not isinstance(node, fbx.FbxObject):
        node = get(scene, node)

    if not node:
        return

    all_child_nodes = _node.get_children(node, recursive=True)
    all_child_nodes.reverse()

    # -- As well as the children we need to make
    # -- sure we remove this root node too
    all_child_nodes.append(node)

    for node_to_remove in all_child_nodes:
        # -- Remove the node and then ask for it to be
        # -- destroyed.
        scene.RemoveNode(node_to_remove)
        node_to_remove.Destroy()


# --------------------------------------------------------------------------------------
def get_header_property(scene, property_name):
    """
    This allows the returning on properties from the header data, including
    the harder to reach properties such as ApplicationNativeFile
    """
    scene_info = scene.GetSceneInfo()

    prop = scene_info.GetFirstProperty()
    while prop.IsValid():

        if prop.GetName() == property_name:
            return str(fbx.FbxPropertyString(prop).Get())

        prop = scene_info.GetNextProperty(prop)

    return None
