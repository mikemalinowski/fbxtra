import fbx

from . import scene as _scene

try:
    _DEFAULT_INTERPOLATION = fbx.FbxAnimCurveDef.EInterpolationType.eInterpolationLinear

except AttributeError:
    _DEFAULT_INTERPOLATION = fbx.FbxAnimCurveDef.eInterpolationLinear


# ----------------------------------------------------------------------------------
def get_time_range(scene: fbx.FbxScene) -> list:
    """
    This will return the time range in [int, int] format where each int
    is the frame number

    :param scene: The fbx scene to retrieve the time range for
    :type scene: fbx.FbxScene

    :return: list of start frame and end frame
    """

    anim_stack = scene.GetCurrentAnimationStack()
    time_span = anim_stack.GetLocalTimeSpan()

    start_frame = time_span.GetStart().GetFrameCount()
    end_frame = time_span.GetStop().GetFrameCount()

    return [start_frame, end_frame]


# --------------------------------------------------------------------------
def set_time_range(scene: fbx.FbxScene, start_frame: int, end_frame: int):
    """
    Sets the start and end frame of the fbx scene

    :param scene: The scene to adjust
    :type scene: fbx.FbxScene

    :param start_frame: The frame number to set as the start time
    :type start_frame: int

    :param end_frame: The frame number to set as the end time
    :type end_frame: int
    """
    time_span = fbx.FbxTimeSpan()

    start_time = fbx.FbxTime()
    start_time.SetFrame(start_frame)

    end_time = fbx.FbxTime()
    end_time.SetFrame(end_frame)

    time_span.SetStart(start_time)
    time_span.SetStop(end_time)

    anim_stack = scene.GetCurrentAnimationStack()
    anim_stack.SetLocalTimeSpan(time_span)


# --------------------------------------------------------------------------
def layers(fbx_scene):
    """
    Gives all the animation layers within the given scene.

    :param fbx_scene: The scene to list the layers from
    :type fbx_scene: fbx.FbxScene

    :return: list(fbx.FbxAnimLayer, ...)
    """
    # -- Define a list to collate our matched
    # -- layers into
    all_layers = list()

    # -- Cycle over all the obects in the scnee
    for idx in range(fbx_scene.GetSrcObjectCount()):

        # -- Check if this item is indeed an animation
        # -- layer and scoop it if it is.
        candidate = fbx_scene.GetSrcObject(
            fbx.FbxCriteria.ObjectType(
                fbx.FbxAnimLayer.ClassId,
            ),
            idx,
        )

        if candidate:
            all_layers.append(candidate)

    return all_layers


# --------------------------------------------------------------------------
def remove_tr_keys(node, zero=False):
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

    if zero:
        node.LclRotation.Set(
            fbx.FbxDouble3(
                0.0,
                0.0,
                0.0,
            )
        )
        node.LclTranslation.Set(
            fbx.FbxDouble3(
                0.0,
                0.0,
                0.0,
            )
        )


# --------------------------------------------------------------------------
def remove_trs_keys(node, zero=False):
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
        scl_curve = node.LclScaling.GetCurveNode(layer)

        if rot_curve:
            rot_curve.Destroy(True)

        if trn_curve:
            trn_curve.Destroy(True)

        if scl_curve:
            scl_curve.Destroy(True)

    if zero:
        node.LclRotation.Set(
            fbx.FbxDouble3(
                0.0,
                0.0,
                0.0,
            )
        )
        node.LclTranslation.Set(
            fbx.FbxDouble3(
                0.0,
                0.0,
                0.0,
            )
        )
        node.LclScaling.Set(
            fbx.FbxDouble3(
                1.0,
                1.0,
                1.0,
            ),
        )


# ----------------------------------------------------------------------------------
def set_all_keys_to_linear(
    scene: fbx.FbxScene, interpolation=_DEFAULT_INTERPOLATION
):

    # -- Cycle all anim curves
    for curve in _scene.of_type(scene, fbx.FbxAnimCurve):

        curve.KeyModifyBegin()

        # -- Cycle the keys for this anim curve
        for key_idx in range(curve.KeyGetCount()):

            curve.KeySetInterpolation(
                key_idx,
                interpolation,
            )
            curve.KeySetTangentMode(
                key_idx,
                fbx.FbxAnimCurveDef.eTangentAuto,
            )

        # -- Declare the curve editing complete
        curve.KeyModifyEnd()


# ----------------------------------------------------------------------------------
def shift_all_keys(scene: fbx.FbxScene, offset: int, reframe=False):
    """
    Shifts all the keys in the entire scene by the given offset value

    :param scene: The scene you want to modify
    :type scene: fbx.FbxScene

    :param offset: The amount you want to offset the animation by
    :type offset: int

    :param reframe: If true the timerange of the scene will also be shifted
        by the given value
    :type reframe: bool

    :return: None
    """
    lowest_frame = None
    highest_frame = None

    # -- Cycle all anim curves
    for curve in _scene.of_type(scene, fbx.FbxAnimCurve):

        curve.KeyModifyBegin()

        # -- Cycle the keys for this anim curve
        for key_idx in range(curve.KeyGetCount()):

            # -- Modify the key time
            key_time = curve.KeyGetTime(key_idx)
            was = key_time.GetFrameCount()
            key_time.SetFrame(key_time.GetFrameCount() + offset)

            new_frame_time = key_time.GetFrameCount()

            if lowest_frame is None or new_frame_time < lowest_frame:
                lowest_frame = new_frame_time

            if highest_frame is None or new_frame_time > highest_frame:
                highest_frame = new_frame_time

            curve.KeySetTime(key_idx, key_time)

        # -- Declare the curve editing complete
        curve.KeyModifyEnd()

    # -- Reframe the scene if required

    if reframe:
        set_time_range(
            scene,
            start_frame=lowest_frame or 0,
            end_frame=highest_frame or 0,
        )


# --------------------------------------------------------------------------------------
def extrapolate_last_key(scene):
    # -- Cycle all anim curves
    for curve in _scene.of_type(scene, fbx.FbxAnimCurve):
        last_key_on_curve_time = curve.KeyGetTime(
            curve.KeyGetCount() - 1
        ).GetFrameCount()

        fbx_end_time = fbx.FbxTime()
        fbx_end_time.SetFrame(last_key_on_curve_time, fbx.FbxTime.eFrames30)

        fbx_end_time_minus_one = fbx.FbxTime()
        fbx_end_time_minus_one.SetFrame(last_key_on_curve_time - 1)

        fbx_end_time_plus_one = fbx.FbxTime()
        fbx_end_time_plus_one.SetFrame(last_key_on_curve_time + 1)

        end_value = curve.Evaluate(fbx_end_time)[0]
        end_value_minus_one = curve.Evaluate(fbx_end_time_minus_one)[0]
        extrapolated_value = end_value + (end_value - end_value_minus_one)

        key_idx = curve.KeyAdd(fbx_end_time_plus_one)

        curve.KeySetValue(key_idx[0], extrapolated_value)


# --------------------------------------------------------------------------------------
def unroll_curves(scene: fbx.FbxScene):
    """
    Runs a euler unroll filter over all the joints in the scene to remove
    gimble flipping

    :param scene: The scene to adjust
    :type scene: fbx.FbxScene
    """
    node_list = _scene.children(scene, recursive=True)
    anim_stack = scene.GetCurrentAnimationStack()

    # get time start / stop
    time_span = anim_stack.GetLocalTimeSpan()
    start_frame = time_span.GetStart()
    end_frame = time_span.GetStop()

    for node in node_list:
        # Check if the node attribute is valid and is of type FbxSkeleton
        if isinstance(node.GetNodeAttribute(), fbx.FbxSkeleton):
            unroll_animation_curves(node, start_frame, end_frame)


# --------------------------------------------------------------------------------------
def unroll_animation_curves(
    node,
    start_frame,
    end_frame,
    test_for_path=True,
    tolerance=0.25,
    force_auto_tangents=True,
):
    """
    Runs a euler unroll filter over the given node to remove gimble flipping

    :param node: The node to adjust
    :type node: fbx.FbxNode

    :param start_frame: The frame number to set as the start time
    :type start_frame: int

    :param end_frame: The frame number to set as the end time
    :type end_frame: int

    :param test_for_path: If enabled, the filter can use the same key as reference key
        to update the following keys
        If not enabled, the filter will always use the newly updated key as reference
        to update the next key
    :type test_for_path: bool

    :param tolerance: The frame number to set as the start time
    :type tolerance: float

    :param force_auto_tangents: If enabled automatically convert the USER and BREAK
        tangents to AUTO tangents
    :type force_auto_tangents: bool
    """

    for layer in layers(node.GetScene()):
        rot_curve = node.LclRotation.GetCurveNode(layer)
        if not rot_curve:
            continue

        # Create a curve filter
        curve_filter = fbx.FbxAnimCurveFilterUnroll()

        # set filter settings
        curve_filter.SetStartTime(start_frame)
        curve_filter.SetStopTime(end_frame)
        curve_filter.SetTestForPath(test_for_path)
        curve_filter.SetQualityTolerance(tolerance)
        curve_filter.SetForceAutoTangents(force_auto_tangents)

        # Apply the filters to the scene
        if curve_filter.NeedApply(rot_curve):
            curve_filter.Apply(rot_curve)


# --------------------------------------------------------------------------------------
def get_curve_from_node_attribute(scene, node_name, attribute_name):
    """
    Find and retrieve an animation curve linked to a specific attribute on a named node.

    Args:
    scene (fbx.FbxScene): The FBX scene.
    node_name (str): The name of the node where the attribute is located.
    attribute_name (str): The name of the attribute.

    Returns:
    fbx.FbxAnimCurveNode or None: The animation curve node associated with the
        attribute if found, None otherwise.
    """

    curve = None

    # -- Find the node by name in the scene
    node = scene.FindNodeByName(node_name)

    if node:
        # -- Check if the node has the specified attribute
        attribute = node.FindProperty(attribute_name)
        if attribute.IsValid():
            # -- Get the connected anim curve node from the attribute
            connected_node = attribute.GetSrcObject()

            if connected_node:
                # -- Check if the connected node is an anim curve node
                if connected_node.GetClassId().Is(fbx.FbxAnimCurveNode.ClassId):
                    curve = connected_node

    return curve


# --------------------------------------------------------------------------------------
def clamp_unit_curve_boundary(curve_node):
    """
    Modify animation curve keys with values of 0 or 1 to have flat (constant) tangents.

    Args:
    curve_node (fbx.FbxAnimCurveNode): The animation curve node containing the
        curve to be processed.
    """

    # -- Get the associated curve from the curve node
    curve = curve_node.GetCurve(0)

    if curve:
        # -- Get the key count in the curve
        key_count = curve.KeyGetCount()

        # -- Iterate through each key
        for i in range(key_count):
            key = curve.KeyGet(i)
            value = key.GetValue()

            # -- Check if the value is 0 or 1
            if value == 0.0 or value == 1.0:
                curve.KeySetTangentMode(i, fbx.FbxAnimCurveDef.eTangentGenericClamp)


def set_current_take_name(scene: fbx.FbxScene, name: str) -> None:
    """
    This will set the current takes name to the given name
    """
    anim_stack = scene.GetCurrentAnimationStack()
    anim_stack.SetName(name)
