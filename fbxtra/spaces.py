

class Space:

    def __init__(self, fbx_scene, transient_space):
        self._fbx_scene = fbx_scene
        self._transient_space = transient_space
        self._existing_space = fbx_scene.GetGlobalSettings().GetSystemUnit()

    def __enter__(self):
        print("in space")
        self._transient_space.ConvertScene(self._fbx_scene)
        self._fbx_scene.GetAnimationEvaluator().Reset()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._existing_space.ConvertScene(self._fbx_scene)
        self._fbx_scene.GetAnimationEvaluator().Reset()
