import fbx


# --------------------------------------------------------------------------------------
def set_matrix(node: fbx.FbxNode, matrix: fbx.FbxAMatrix):
    """
    Sets the local matrix of a node.

    TODO: Global matrix applying.

    :param node: The node to apply the relative matrix to
    :type node: fbx.FbxNode

    :param matrix: The matrix to apply to the node
    :type matrix: fbx.FbxAMatrix

    :return None
    """
    # -- We can only set via translate, rotate and scale, so get
    # -- those out of the matrix, and we want a list of three
    # -- items
    translate = [v for v in matrix.GetT()][:3]
    rotate = [v for v in matrix.GetR()][:3]
    scale = [v for v in matrix.GetS()][:3]

    node.LclTranslation.Set(
        fbx.FbxDouble3(*translate),
    )
    node.LclRotation.Set(
        fbx.FbxDouble3(*rotate),
    )

    node.LclScaling.Set(
        fbx.FbxDouble3(*scale),
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
