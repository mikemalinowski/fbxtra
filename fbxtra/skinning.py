"""
Functionality for reading and transferring skin (FbxSkin) deformers between
meshes, including spatial (vertex-order-independent) weight transfer.
"""
import fbx

# -- Enum access differs across fbx sdk versions, so resolve once here
try:
    _SKIN_TYPE = fbx.FbxDeformer.EDeformerType.eSkin

except AttributeError:
    _SKIN_TYPE = fbx.FbxDeformer.eSkin


# --------------------------------------------------------------------------------------
def get_skin(mesh_node):
    """
    Returns the first FbxSkin deformer on the given mesh node, or None.

    :param mesh_node: The mesh transform node to query
    :type mesh_node: fbx.FbxNode

    :return: fbx.FbxSkin or None
    """
    mesh = mesh_node.GetMesh()
    if not mesh:
        return None

    if mesh.GetDeformerCount(_SKIN_TYPE):
        return mesh.GetDeformer(0, _SKIN_TYPE)

    return None


# --------------------------------------------------------------------------------------
def world_control_points(mesh_node):
    """
    Returns the mesh control points transformed into world space.

    :param mesh_node: The mesh transform node to query
    :type mesh_node: fbx.FbxNode

    :return: list((x, y, z), ...)
    """
    mesh = mesh_node.GetMesh()
    matrix = mesh_node.EvaluateGlobalTransform()

    points = list()
    for idx in range(mesh.GetControlPointsCount()):
        world = matrix.MultT(mesh.GetControlPointAt(idx))
        points.append((world[0], world[1], world[2]))

    return points


# --------------------------------------------------------------------------------------
def get_weights(mesh_node):
    """
    Returns the per-control-point weighting of the mesh's skin deformer.

    :param mesh_node: The skinned mesh transform node to query
    :type mesh_node: fbx.FbxNode

    :return: dict mapping control point index -> dict(link_node -> weight)
    """
    weights = dict()

    skin = get_skin(mesh_node)
    if not skin:
        return weights

    for cluster_idx in range(skin.GetClusterCount()):
        cluster = skin.GetCluster(cluster_idx)

        # -- The link is the joint this cluster drives. If it has none then
        # -- there is nothing meaningful to transfer
        link = cluster.GetLink()
        if not link:
            continue

        # -- Key by joint name: the fbx node wrappers are not hashable, and
        # -- joint names are unique within a skeleton
        link_name = link.GetName()

        # -- These arrays must be bounded by the explicit count; the fbx python
        # -- bindings do not length-guard them, so iterating past the count
        # -- reads off the end of the buffer (access violation)
        index_count = cluster.GetControlPointIndicesCount()
        indices = cluster.GetControlPointIndices()
        values = cluster.GetControlPointWeights()

        for i in range(index_count):
            control_point = indices[i]
            per_point = weights.setdefault(control_point, dict())
            per_point[link_name] = per_point.get(link_name, 0.0) + values[i]

    return weights


# --------------------------------------------------------------------------------------
def _nearest(points, target, count):
    """
    Returns the (index, distance) of the `count` nearest points to target.

    :param points: The pool of points to search within
    :type points: list((x, y, z), ...)

    :param target: The point to measure distances from
    :type target: (x, y, z)

    :param count: How many nearest points to return
    :type count: int

    :return: list((index, distance), ...)
    """
    tx, ty, tz = target

    distances = list()
    for idx, (px, py, pz) in enumerate(points):
        squared = (px - tx) ** 2 + (py - ty) ** 2 + (pz - tz) ** 2
        distances.append((squared, idx))

    distances.sort(key=lambda item: item[0])

    return [(idx, squared ** 0.5) for squared, idx in distances[:count]]


# --------------------------------------------------------------------------------------
def copy_skin(source_mesh_node, target_mesh_node, search_count=3, max_influences=4):
    """
    Builds a new skin deformer on the target mesh by spatially transferring
    the source mesh's skin weights. Vertex orders do not need to match; each
    target control point is matched to its nearest source control point(s) in
    world space. The new clusters re-link to the same skeleton joints used by
    the source.

    :param source_mesh_node: The skinned mesh to copy weights from
    :type source_mesh_node: fbx.FbxNode

    :param target_mesh_node: The mesh to build the new skin on
    :type target_mesh_node: fbx.FbxNode

    :param search_count: How many nearest source points to blend per target
        point (inverse-distance weighted). 1 == a pure closest-point copy.
    :type search_count: int

    :param max_influences: The maximum number of joints allowed to influence a
        single target vertex. Vertices with more are trimmed to the strongest
        `max_influences` weights and renormalised.
    :type max_influences: int

    :return: The new fbx.FbxSkin
    """
    source_skin = get_skin(source_mesh_node)
    if not source_skin:
        raise ValueError(
            "Source mesh '{}' has no skin deformer".format(
                source_mesh_node.GetName(),
            ),
        )

    # -- Gather the source data we will be matching against
    source_points = world_control_points(source_mesh_node)
    source_weights = get_weights(source_mesh_node)

    target_mesh = target_mesh_node.GetMesh()
    target_points = world_control_points(target_mesh_node)

    scene = target_mesh_node.GetScene()
    mesh_matrix = target_mesh_node.EvaluateGlobalTransform()

    # -- Create the new skin, mirroring the source's skinning type
    skin = fbx.FbxSkin.Create(scene, target_mesh_node.GetName() + "_Skin")
    skin.SetSkinningType(source_skin.GetSkinningType())

    # -- Create one cluster per source joint, re-linking to the same joint and
    # -- reusing the source's bind matrices. The joints are shared, so the link
    # -- matrices are identical; the mesh matrix is the target's bind pose
    clusters = dict()
    for cluster_idx in range(source_skin.GetClusterCount()):
        source_cluster = source_skin.GetCluster(cluster_idx)

        link = source_cluster.GetLink()
        if not link:
            continue

        # -- Key clusters by joint name (fbx nodes are not hashable)
        link_name = link.GetName()
        if link_name in clusters:
            continue

        cluster = fbx.FbxCluster.Create(scene, link_name)
        cluster.SetLink(link)
        cluster.SetLinkMode(source_cluster.GetLinkMode())

        link_matrix = fbx.FbxAMatrix()
        source_cluster.GetTransformLinkMatrix(link_matrix)
        cluster.SetTransformLinkMatrix(link_matrix)
        cluster.SetTransformMatrix(mesh_matrix)

        clusters[link_name] = cluster

    # -- Transfer weights, one target control point at a time
    for target_idx, target_point in enumerate(target_points):

        blended = dict()
        total_influence = 0.0

        # -- Blend the weights of the nearest source point(s) by inverse
        # -- distance. A single nearest point collapses to a straight copy
        for source_idx, distance in _nearest(source_points, target_point, search_count):
            influence = 1.0 / (distance + 1e-9) if search_count > 1 else 1.0
            total_influence += influence

            for link_name, weight in source_weights.get(source_idx, dict()).items():
                blended[link_name] = blended.get(link_name, 0.0) + (weight * influence)

        # -- Cap the number of influences per vertex: keep the strongest
        # -- `max_influences` weights and drop the rest, then renormalise the
        # -- retained weights so they sum to one
        ranked = sorted(blended.items(), key=lambda item: item[1], reverse=True)
        ranked = ranked[:max_influences]

        weight_sum = sum(weight for _, weight in ranked)
        if not weight_sum:
            continue

        for link_name, weight in ranked:
            normalised = weight / weight_sum
            if normalised > 0.0:
                clusters[link_name].AddControlPointIndex(target_idx, normalised)

    # -- Attach the populated clusters and deformer to the target mesh
    for cluster in clusters.values():
        skin.AddCluster(cluster)

    target_mesh.AddDeformer(skin)

    return skin
