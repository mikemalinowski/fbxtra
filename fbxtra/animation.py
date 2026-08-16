import fbx

from . import scene as _scene

try:
    _DEFAULT_INTERPOLATION = fbx.FbxAnimCurveDef.EInterpolationType.eInterpolationLinear

except AttributeError:
    _DEFAULT_INTERPOLATION = fbx.FbxAnimCurveDef.eInterpolationLinear

_AXES = ("X", "Y", "Z")


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


# ----------------------------------------------------------------------------------
def zero_start_pose(node: fbx.FbxNode) -> None:
    """
    Rebases the local animation on the given node so that at its first keyed
    frame both LclTranslation and LclRotation are (0, 0, 0).

    The rebase treats the start pose as a single rigid transform
    M_start = T_start * R_start and applies its inverse to every keyed frame:

        R_new(t) = R_start^-1 * R_current(t)
        T_new(t) = R_start^-1 * (T_current(t) - T_start)

    The translation trajectory is therefore expressed in the new (identity)
    frame rather than the original orientation, so a walk cycle originally
    facing world +Y correctly tracks local +Z after the rebase.

    Translation and rotation keys are re-baked at the union of their per-channel
    key times using linear interpolation. Static (unkeyed) values on translation
    and rotation are also zeroed. Scale is left untouched.

    Assumes XYZ Euler rotation order (Maya / FBX default). Nodes with a
    different FbxNode.RotationOrder should be normalised first.

    :param node: The node whose local animation should be rebased.
    :type node: fbx.FbxNode

    :return: None
    """
    scene = node.GetScene()
    anim_layers = layers(scene)

    if not anim_layers:
        node.LclTranslation.Set(fbx.FbxDouble3(0.0, 0.0, 0.0))
        node.LclRotation.Set(fbx.FbxDouble3(0.0, 0.0, 0.0))
        return

    for layer in anim_layers:
        _rebase_layer_to_origin(node, layer)

    node.LclTranslation.Set(fbx.FbxDouble3(0.0, 0.0, 0.0))
    node.LclRotation.Set(fbx.FbxDouble3(0.0, 0.0, 0.0))


# ----------------------------------------------------------------------------------
def _rebase_layer_to_origin(node: fbx.FbxNode, layer: fbx.FbxAnimLayer) -> None:
    """
    Applies the origin-rebase to a single animation layer of the given node.
    Computes the start pose from the earliest keyed frame across the six
    translation and rotation channels, then rewrites the layer's translation
    and rotation curves so that at that frame the local transform is identity.

    :param node: The node whose curves on this layer should be rebased.
    :type node: fbx.FbxNode

    :param layer: The animation layer to operate on.
    :type layer: fbx.FbxAnimLayer

    :return: None
    """
    trn_curves = [node.LclTranslation.GetCurve(layer, ch) for ch in _AXES]
    trn_statics = [node.LclTranslation.Get()[i] for i in range(3)]

    rot_curves = [node.LclRotation.GetCurve(layer, ch) for ch in _AXES]
    rot_statics = [node.LclRotation.Get()[i] for i in range(3)]

    start_frame = _earliest_key_frame(trn_curves + rot_curves)
    if start_frame is None:
        return

    start_t = _sample_channels_at(trn_curves, trn_statics, start_frame)
    start_r = _sample_channels_at(rot_curves, rot_statics, start_frame)

    inv_start = fbx.FbxAMatrix()
    inv_start.SetT(fbx.FbxVector4(start_t[0], start_t[1], start_t[2], 0.0))
    inv_start.SetR(fbx.FbxVector4(start_r[0], start_r[1], start_r[2], 0.0))
    inv_start = inv_start.Inverse()

    _rebuild_translation(node, layer, trn_curves, trn_statics, inv_start)
    _rebuild_rotation(node, layer, rot_curves, rot_statics, inv_start)


# ----------------------------------------------------------------------------------
def _rebuild_translation(node, layer, curves, statics, inv_start):
    """
    Rewrites the three LclTranslation channel curves on the given layer.

    For every unique key time across the three input curves, the current XYZ
    vector is sampled (falling back to the property's static value on channels
    that have no curve), transformed by inv_start as a point, and written back
    as a new key on all three channels. Existing keys are cleared first.

    :param node: The node the translation curves belong to.
    :type node: fbx.FbxNode

    :param layer: The animation layer to write into.
    :type layer: fbx.FbxAnimLayer

    :param curves: The three existing LclTranslation channel curves (X, Y, Z).
        Any entry may be None if that channel has no curve on this layer.
    :type curves: list(fbx.FbxAnimCurve or None)

    :param statics: The three static LclTranslation channel values, used when
        the corresponding curve entry is None.
    :type statics: list(float)

    :param inv_start: The inverse of the full start-pose rigid transform.
        Applied via MultT so each sampled position becomes
        R_start^-1 * (T_current - T_start).
    :type inv_start: fbx.FbxAMatrix

    :return: None
    """
    key_frames = _union_key_frames(curves)
    if not key_frames:
        return

    new_keys = []
    for frame in key_frames:
        current = _sample_channels_at(curves, statics, frame)
        transformed = inv_start.MultT(
            fbx.FbxVector4(current[0], current[1], current[2], 0.0)
        )
        new_keys.append((frame, [transformed[0], transformed[1], transformed[2]]))

    resolved = [node.LclTranslation.GetCurve(layer, ch, True) for ch in _AXES]
    _write_channel_keys(resolved, new_keys)


# ----------------------------------------------------------------------------------
def _rebuild_rotation(node, layer, curves, statics, inv_start):
    """
    Rewrites the three LclRotation channel curves on the given layer.

    For every unique key time across the three input curves, the current Euler
    XYZ triplet is sampled (falling back to the property's static value on
    channels that have no curve), composed as inv_start * R_current via
    FbxAMatrix, and the resulting Euler is written back as a new key on all
    three channels. Existing keys are cleared first.

    Only the rotation component of the composition is read out, so the
    translation portion of inv_start is harmless here.

    :param node: The node the rotation curves belong to.
    :type node: fbx.FbxNode

    :param layer: The animation layer to write into.
    :type layer: fbx.FbxAnimLayer

    :param curves: The three existing LclRotation channel curves (X, Y, Z).
        Any entry may be None if that channel has no curve on this layer.
    :type curves: list(fbx.FbxAnimCurve or None)

    :param statics: The three static LclRotation channel values, used when
        the corresponding curve entry is None.
    :type statics: list(float)

    :param inv_start: The inverse of the full start-pose rigid transform.
    :type inv_start: fbx.FbxAMatrix

    :return: None
    """
    key_frames = _union_key_frames(curves)
    if not key_frames:
        return

    new_keys = []
    for frame in key_frames:
        current = _sample_channels_at(curves, statics, frame)

        current_matrix = fbx.FbxAMatrix()
        current_matrix.SetR(fbx.FbxVector4(current[0], current[1], current[2], 0.0))

        result = inv_start * current_matrix
        r = result.GetR()
        new_keys.append((frame, [r[0], r[1], r[2]]))

    resolved = [node.LclRotation.GetCurve(layer, ch, True) for ch in _AXES]
    _write_channel_keys(resolved, new_keys)


# ----------------------------------------------------------------------------------
def _earliest_key_frame(curves):
    """
    Returns the lowest key time (as an integer frame count) across the given
    curves. Curves that are None or have no keys are skipped. If no curve
    contributes any key, None is returned.

    :param curves: The curves to inspect.
    :type curves: list(fbx.FbxAnimCurve or None)

    :return: The earliest frame number, or None if nothing is keyed.
    :rtype: int or None
    """
    earliest = None
    for curve in curves:
        if curve is None or curve.KeyGetCount() == 0:
            continue
        frame = curve.KeyGetTime(0).GetFrameCount()
        if earliest is None or frame < earliest:
            earliest = frame
    return earliest


# ----------------------------------------------------------------------------------
def _union_key_frames(curves):
    """
    Returns a sorted list of the unique key times (as integer frame counts)
    covering every key across the given curves. Curves that are None are
    skipped.

    :param curves: The curves to inspect.
    :type curves: list(fbx.FbxAnimCurve or None)

    :return: Sorted list of frame numbers, empty if no keys exist.
    :rtype: list(int)
    """
    frames = set()
    for curve in curves:
        if curve is None:
            continue
        for key_idx in range(curve.KeyGetCount()):
            frames.add(curve.KeyGetTime(key_idx).GetFrameCount())
    return sorted(frames)


# ----------------------------------------------------------------------------------
def _sample_channels_at(curves, statics, frame):
    """
    Samples a triple of parallel channel curves at the given frame. Where a
    curve is None the corresponding static value is returned unchanged;
    otherwise the curve is evaluated at that frame.

    :param curves: Three parallel channel curves. Any entry may be None.
    :type curves: list(fbx.FbxAnimCurve or None)

    :param statics: Three static channel values, used as fallbacks for None
        curves.
    :type statics: list(float)

    :param frame: The frame number at which to sample.
    :type frame: int

    :return: The three sampled channel values.
    :rtype: list(float)
    """
    fbx_time = fbx.FbxTime()
    fbx_time.SetFrame(frame)

    values = []
    for axis, curve in enumerate(curves):
        if curve is None:
            values.append(statics[axis])
        else:
            values.append(curve.Evaluate(fbx_time)[0])
    return values


# ----------------------------------------------------------------------------------
def _write_channel_keys(curves, keys):
    """
    Clears the given three channel curves and writes a new set of keys onto
    them. Each entry in ``keys`` is a (frame, [x, y, z]) pair; a key is added
    to every channel at that frame using the module's default interpolation.

    Assumes all three curves already exist (create them via
    property.GetCurve(layer, channel, True) before calling).

    :param curves: The three channel curves to overwrite.
    :type curves: list(fbx.FbxAnimCurve)

    :param keys: The key data to write, one entry per frame.
    :type keys: list(tuple(int, list(float)))

    :return: None
    """
    for curve in curves:
        curve.KeyModifyBegin()
        curve.KeyClear()

    for frame, values in keys:
        fbx_time = fbx.FbxTime()
        fbx_time.SetFrame(frame)

        for axis, curve in enumerate(curves):
            key_idx, _ = curve.KeyAdd(fbx_time)
            curve.KeySetValue(key_idx, values[axis])
            curve.KeySetInterpolation(key_idx, _DEFAULT_INTERPOLATION)

    for curve in curves:
        curve.KeyModifyEnd()


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
