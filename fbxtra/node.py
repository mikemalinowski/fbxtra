"""
Functionality for accessing information relating to FBXNodes in a scene
"""
import fbx

from . import animation as _animation


# --------------------------------------------------------------------------
# noinspection PyMethodMayBeStatic
def get_children(node, recursive=False):
    """
    Returns all the children of the given node. 
    
    :param node: The node to start searching for children from.
    :type node: fbx.FbxNode

    :param recursive: If True then the search will return not only the
        immediate children of the node, but also all the sub-children
        too.
    :type recursive: Bool

    :return: List of children
    """
    # -- Define the list to which we will collate
    # -- all the child nodes we find.
    children = list()

    for idx in range(node.GetChildCount()):

        # -- Get the child and store it
        child = node.GetChild(idx)
        children.append(child)

        # -- If our recursive argument is set as true
        # -- then we re-call the function
        if recursive:
            children.extend(get_children(child, recursive=recursive))

    # -- Return what we have found
    return children


# --------------------------------------------------------------------------
def get_parent(node, recursive=False):
    """
    Gets the parent of the given node. If recurse is True then
    the highest level node (excluding the RootNode) is returned.

    :param node: The node to search from
    :type node: fbx.FbxNode

    :param recursive: If True, this option will mean you're given the 
        highest level parent of the node rather than the direct
        parent.
    :type recursive: bool

    :return: fbx.FbxNode
    """
    # -- Get the immediate parent
    parent = node.GetParent()

    # -- If we have hit the scene root (RootNode), then we return
    # -- the node as that has no other parent
    if not parent or parent.GetName() == 'RootNode':
        return node

    # -- If our recursive argument is True then we keep
    # -- calling our function until we hit the ceiling.
    if recursive:
        parent = get_parent(parent, recursive=recursive)

    return parent


# --------------------------------------------------------------------------
def set_parent(node, parent):
    """
    Re-parents the given node to be a child of the given parent.

    :param node: The node to move hierarchically
    :type node: fbx.FbxNode

    :param parent: The node to set as the parent. If None, then the 
        node will be made a child of the scene root (RootNode)
    :type parent: fbx.FbxNode

    :return: None
    """
    if not parent:
        parent = node.GetScene().GetRootNode()

    parent.AddChild(node)


# --------------------------------------------------------------------------
def zero(node):
    """
    This will zero the translation and rotation of the given node. Any keys 
        assigned to this nodes translation or rotation will also be removed.

    :param node: The node to zero
    :type node: fbx.FbxNode

    :return: None
    """

    # -- Remove keys first
    _animation.remove_tr_keys(node)

    # -- Define the zero vector which we will apply to the node
    zero_vector = fbx.FbxDouble3(
        0.0,
        0.0,
        0.0,
    )

    # -- Apply the zero'ing
    node.LclTranslation.Set(zero_vector)
    node.LclRotation.Set(zero_vector)
