from . import scene


def remove_node_name(blendshape):
    """
    This will rename channels such that they will be split by a "." and the channel
    will be named with the last part.

    This is particularly because maya exports its fbx files with the blendshape node
    as the channel name.

    :param blendshape:
    :return:
    """
    channel_count = blendshape.GetBlendShapeChannelCount()

    for channel_idx in range(channel_count):
        channel = blendshape.GetBlendShapeChannel(channel_idx)
        current_name = channel.GetName()

        if "." not in current_name:
            continue

        channel.SetName(channel.GetName().split(".")[-1])


def remove_node_name_from_all(fbx_scene):
    for blendshape in scene.of_type(fbx_scene, "BlendShape"):
        remove_node_name(blendshape)
