import fbx


# --------------------------------------------------------------------------
def layers(scene):
    """
    Gives all the animation layers within the given scene.
    
    :param scene: The scene to list the layers from
    :type scene: fbx.FbxScene

    :return: list(fbx.FbxAnimLayer, ...)
    """
    # -- Define a list to collate our matched
    # -- layers into
    all_layers = list()

    # -- Cycle over all the obects in the scnee
    for idx in range(scene.GetSrcObjectCount()):

        # -- Check if this item is indeed an animation
        # -- layer and scoop it if it is.
        candidate = scene.GetSrcObject(
            fbx.FbxCriteria.ObjectType(
                fbx.FbxAnimLayer.ClassId,
            ),
            idx,
        )

        if candidate:
            all_layers.append(candidate)

    return all_layers


# --------------------------------------------------------------------------
def remove_tr_keys(node):
    """
    This removes any keys (fcurves) driving the translation or rotation
    of the given node.

    :param node: The node to remove the translation and rotation from
    :type node: fbx.FbxNode

    :return: None
    """
    for layer in layers(node.GetScene()):

        rot_curve = node.LclRotation.GetCurveNode(layer)
        trn_curve = node.LclTranslation.GetCurveNode(layer)

        if rot_curve:
            rot_curve.Destroy(True)

        if trn_curve:
            trn_curve.Destroy(True)
