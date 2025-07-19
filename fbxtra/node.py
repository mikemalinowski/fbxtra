"""
Functionality for accessing information relating to FBXNodes in a scene
"""
import fbx

from . import animation as _animation
from . import transforms as _transforms


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
def get_parents(node):
    """
    Returns a list of all the parents

    Args:
        node:

    Returns:
    """
    parents = list()
    _current = node

    while True:

        if not _current:
            return parents

        _current = _current.GetParent()
        parents.append(_current)


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
    if not parent or parent.GetName() == "RootNode":
        return node

    # -- If our recursive argument is True then we keep
    # -- calling our function until we hit the ceiling.
    if recursive:
        parent = get_parent(parent, recursive=recursive)

    return parent


# --------------------------------------------------------------------------
def set_parent(node, parent, keep_worldspace=True):
    """
    Re-parents the given node to be a child of the given parent.

    :param node: The node to move hierarchically
    :type node: fbx.FbxNode

    :param parent: The node to set as the parent. If None, then the
        node will be made a child of the scene root (RootNode)
    :type parent: fbx.FbxNode

    :param keep_worldspace: If True then the worldspace transform of the node
        being reparented will be retained
    :type keep_worldspace: bool

    :return: None
    """
    if not parent:
        parent = node.GetScene().GetRootNode()

    if not keep_worldspace:
        # -- In this situation we do not need to do any math
        # -- to retain the worldspace transform. So we can just
        # -- add the child and be done
        parent.AddChild(node)
        return

    # -- To reach here we need to add the child whilst holding the relative
    # -- transform
    node_xfo = node.EvaluateGlobalTransform()
    parent_xfo = parent.EvaluateGlobalTransform()
    relative_xfo = node_xfo * parent_xfo.Inverse()

    parent.AddChild(node)

    # -- We can only set via translate, rotate and scale, so get
    # -- those out of the matrix, and we want a list of three
    # -- items
    translate = [v for v in relative_xfo.GetT()][:3]
    rotate = [v for v in relative_xfo.GetR()][:3]
    scale = [v for v in relative_xfo.GetS()][:3]

    node.LclTranslation.Set(
        fbx.FbxDouble3(*translate),
    )
    node.LclRotation.Set(
        fbx.FbxDouble3(*rotate),
    )

    node.LclScaling.Set(
        fbx.FbxDouble3(*scale),
    )


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
    node.LclScaling.Set(
        fbx.FbxDouble3(
            1.0,
            1.0,
            1.0,
        )
    )


# ----------------------------------------------------------------------------------
def set_transform(node, translation=None, rotation=None, scale=None):
    """
    Sets the local transform of the given node

    :param node: Node to adjust the transform for
    :type node: fbx.FbxNode

    :param translation: The translation vector to apply
    :type translation: list(float, float, float)

    :param rotation: The translation vector to apply
    :type rotation: list(float, float, float)

    :param scale: The translation vector to apply
    :type scale: list(float, float, float)
    """
    if translation:
        node.LclTranslation.Set(
            fbx.FbxDouble3(
                translation[0],
                translation[1],
                translation[2],
            )
        )

    if rotation:
        node.LclRotation.Set(
            fbx.FbxDouble3(
                rotation[0],
                rotation[1],
                rotation[2],
            )
        )

    if scale:
        node.LclScaling.Set(
            fbx.FbxDouble3(
                scale[0],
                scale[1],
                scale[2],
            )
        )


# ----------------------------------------------------------------------------------
def create(
    scene: fbx.FbxScene, name: str, matrix: fbx.FbxAMatrix = None
) -> fbx.FbxNode:
    """
    Creates a transform node as a child of the given scene

    :param scene: The scene in which the new node should be added
    :type scene: fbx.FbxScene

    :param name: The name to assign to the new node
    :type name: str

    :param matrix: An optional local matrix to be applied to the node on creation
    :type matrix: fbx.FbxAMatrix

    :return: The node that has been created:
    :rtype: fbx.FbxNode
    """
    new_node = fbx.FbxNode.Create(scene, name)
    scene.GetRootNode().AddChild(new_node)

    if matrix:
        _transforms.set_matrix(new_node, matrix)

    return new_node
