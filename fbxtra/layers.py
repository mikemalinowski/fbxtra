"""
This module contains a series of functions that make it easier
to interact with display layers within the fbx sdk
"""
import fbx

from . import scene as _scene


def get_all(scene: fbx.FbxScene) -> list[fbx.FbxDisplayLayer]:
    """
    This will return all the FbxDisplayLayer's in the fbx scene.

    :param scene: The FbxScene to query
    :return: List of FbxDisplayLayer's
    """
    layers = []
    criteria = fbx.FbxCriteria.ObjectType(fbx.FbxDisplayLayer.ClassId)

    for i in range(scene.GetSrcObjectCount(criteria)):
        layer = scene.GetSrcObject(criteria, i)
        layers.append(layer)

    return layers


def get(scene: fbx.FbxScene, layer_name: str) -> fbx.FbxDisplayLayer:
    """
    This will get the FbxDisplayLayer with the given name
    from the fbx scene.

    :param scene: The FbxScene to query
    :param layer_name: The name of the FbxDisplayLayer
    :return: FbxDisplayLayer
    """
    for layer in get_all(scene):
        if layer_name == layer.GetName():
            return layer
    return None


def members(layer: fbx.FbxDisplayLayer) -> list[fbx.FbxNode]:
    """
    This will return a list of FbxNode objects which belong to the given
    layer.

    :param layer: The FbxDisplayLayer
    :return: List of FbxNode objects
    """
    nodes = []

    member_count = layer.GetMemberCount()
    for i in range(member_count):
        nodes.append(layer.GetMember(i))

    return nodes


def add_members(layer: fbx.FbxDisplayLayer, nodes: list[fbx.FbxNode], exclusive=False):
    """
    This will add the given FbxNode objects to the given FbxDisplayLayer.

    :param layer: The FbxDisplayLayer to add to
    :param nodes: List of FbxNode objects to add
    :param exclusive: If true then the nodes will be removed from any other
        layer they belong to.
    """
    scene = _scene.get_from_node(nodes[0])

    if exclusive:
        for node in nodes:
            for assigned_layer in assigned_layers(scene, node):
                remove_members(assigned_layer, [node])

    for node in nodes:
        layer.AddMember(node)


def remove_members(layer: fbx.FbxDisplayLayer, nodes: list[fbx.FbxNode]):
    """
    This will remove the given FbxNode objects from the given FbxDisplayLayer.

    :param layer: The FbxDisplayLayer to remove from
    :param nodes: List of FbxNode objects to remove
    """
    for node in nodes:
        layer.RemoveMember(node)


def empty_layer(layer: fbx.FbxDisplayLayer):
    """
    This will remove all members of a given layer

    :param layer: The FbxDisplayLayer
    """
    remove_members(layer, members(layer))


def remove_layer(scene: fbx.FbxScene, layer: fbx.FbxDisplayLayer):
    """
    This will remove the given FbxDisplayLayer from the scene

    :param scene: The FbxScene
    :param layer: The FbxDisplayLayer
    """
    scene.DisconnectSrcObject(layer)
    layer.Destroy()


def exists(scene: fbx.FbxScene, layer_name: str) -> bool:
    """
    This will return True if there is a display layer with the given
    name in the scene.

    :param scene: The FbxScene
    :param layer_name: The name of the FbxDisplayLayer
    :return: True if there is a display layer with the given
    """
    return get(scene, layer_name) is not None


def assigned_layers(scene: fbx.FbxScene, node: fbx.FbxNode) -> list[fbx.FbxDisplayLayer]:
    """
    This will return a list of layers which the node is assigned
    to.

    :param scene: The FbxScene
    :param node: The FbxNode
    :return: List of FbxNode objects
    """
    layers = []
    for layer in get_all(scene):
        for member in members(layer):
            if member == node:
                layers.append(layer)
                break
    return layers
