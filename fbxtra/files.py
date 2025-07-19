"""
This holds convenience functionality for loading and saving fbx files, trying
to lower the overhead for repetitive tasks. 
"""
import fbx

from . import constants
from . import manager as _manager

try:
    _DEFAULT_FRAMERATE = fbx.FbxTime.eFrames30
   
except AttributeError:
    _DEFAULT_FRAMERATE = fbx.FbxTime.EMode.eFrames30
    

# ------------------------------------------------------------------------------
def load(fbx_path, framerate=_DEFAULT_FRAMERATE):
    """
    Convenience function for the loading of Fbx scenes.

    :param fbx_path: The absolute path to the fbx file to be loaded
    :type fbx_path: str

    :param framerate: This ensures that no default fbx settings will override
        the given framerate if its defined
    :type framerate: FbxTime.eFrames

    :return: fbx.FbxScene
    """

    # -- Get the manager class, as this is used a lot
    # -- during this process
    fbx_manager = _manager.get()

    # -- Conform the incoming path to a standard
    # -- we can work with
    fbx_path = fbx_path.replace("\\", "/").strip()

    # -- When we load in an Fbx file we need to define the settings,
    # -- which we will use the defaults.
    ios = fbx.FbxIOSettings.Create(
        fbx_manager,
        fbx.IOSROOT,
    )
    fbx_manager.SetIOSettings(ios)

    # -- Create an empty scene class to which we will load hte
    # -- file into
    scene = fbx.FbxScene.Create(fbx_manager, "")

    # -- Ensure we're always generating at the expected framerate
    scene.GetGlobalSettings().SetTimeMode(framerate)

    # -- To load a file we need to instance the importer object
    # -- which handles the actual scene initialisation
    importer = fbx.FbxImporter.Create(fbx_manager, "")

    # -- We can now initialise the fbx scene using the given
    # -- importer
    result = importer.Initialize(
        fbx_path,
        -1,
        fbx_manager.GetIOSettings(),
    )

    # -- If anything went wrong with the initialisation we
    # -- skip out and return a False value
    if not result:
        return False

    # -- We want to import everything by default!
    if importer.IsFBX():
        for setting in constants.FBX_IMPORT_SETTINGS:
            fbx_manager.GetIOSettings().SetBoolProp(setting, True)

    # -- Again, ensure we're saving at the right framerate
    scene.GetGlobalSettings().SetTimeMode(framerate)

    # -- Import the scene and clean up the importer
    # -- instance
    importer.Import(scene)
    importer.Destroy()

    return scene


# --------------------------------------------------------------------------
def save(scene, fbx_path):
    """
    Takes in an fbx.FbxScene instance and writes that scene out
    to the given fbx path.

    :param scene: The scene to write out to a file
    :type  scene: fbx.FbxScene

    :param fbx_path: The location to write out the scene
    :type fbx_path: str

    :return: The location the scene was saved.
    :rtype: str
    """

    # -- Get the manager instance
    fbx_manager = _manager.get()

    # -- Instance an exporter class
    scene_exporter = fbx.FbxExporter.Create(fbx_manager, "")

    # -- Create the export settings, using the defaults
    ios = fbx.FbxIOSettings.Create(
        _manager.get(),
        fbx.IOSROOT,
    )

    # -- Initialise the exporter. Note that fbxtra always writes
    # -- in the ascii format
    scene_exporter.Initialize(
        fbx_path,
        ascii_format_index(),
        ios,
    )

    # -- Initiate the scene export
    scene_exporter.Export(scene)

    return fbx_path


# --------------------------------------------------------------------------
def ascii_format_index():
    """
    Returns the ascii format index

    :return: int designator for ascii format
    """

    # -- Get access to teh fbx manager
    fbx_manager = _manager.get()

    # -- We need cycle all the write formats to find the right
    # -- one.
    format_count = fbx_manager.GetIOPluginRegistry().GetWriterFormatCount()

    # -- Get the fbx registry, this is where we look for
    # -- formats
    registry = fbx_manager.GetIOPluginRegistry()

    # -- Cycle all the formats
    for idx in range(format_count):

        # -- If the format description containts ascii we know
        # -- its safe to use
        if registry.WriterIsFBX(idx):
            if "ascii" in registry.GetWriterFormatDescription(idx):
                return idx

    # -- Fall back to the default if all else fails
    return -1
