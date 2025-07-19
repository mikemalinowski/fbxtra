import gc
import fbx


# ------------------------------------------------------------------------------
# noinspection PyArgumentList
def get():
    """
    Returns the FbxManager. If a manager instance already exists
    then that instance will be returned otherwise a new manager
    will be generated.

    :return: fbx.FbxManager
    """
    for candidate in gc.get_objects():
        try:
            if isinstance(candidate, fbx.FbxManager):
                return candidate
        except ReferenceError:
            continue

    return fbx.FbxManager.Create()
