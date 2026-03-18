import fbx


def get_properties(scene: fbx.FbxScene) -> dict:
    """
    This will return a dictionary of all the document properties
    """
    # -- Declare the output variable
    output = dict()

    # -- Get the document info
    document_info = scene.GetDocumentInfo()

    # -- Get the first property
    document_property = document_info.GetFirstProperty()

    while document_property.IsValid():

        # -- Get the property as a string propery and cast it to
        # -- a python string
        string_property = fbx.FbxPropertyString(document_property)
        output[str(document_property.GetName())] = str(string_property.Get())

        # -- Now move onto the next property
        document_property = document_info.GetNextProperty(document_property)

    return output


def get_property(scene: fbx.FbxScene, property_name: str) -> str:
    """
    This will return the scene info property. Valid strings are:
        DocumentUrl
        SrcDocumentUrl
        Original
        ApplicationVendor
        ApplicationName
        ApplicationVersion
        DateTime_GMT
        FileName
        LastSaved
        ApplicationVendor
        ApplicationName
        ApplicationVersion
        DateTime_GMT
        DocumentEmbeddedUrl
        SceneThumbnail
        ApplicationActiveProject
        ApplicationNativeFile

    :return: native python string value
    """
    # -- Get the document info
    document_info = scene.GetDocumentInfo()

    # -- Get the first property
    document_property = document_info.GetFirstProperty()

    while document_property.IsValid():
        if document_property.GetName() == property_name:
            return str(fbx.FbxPropertyString(document_property).Get())

        # -- This was not the property we needed to find, so
        # -- lets move onto the next one
        document_property = document_info.GetNextProperty(document_property)

    # -- If we could not find the property then we
    # -- return an empty string
    return ""


def set_property(scene: fbx.FbxScene, property_name: str, value: str):
    """
    This will set the value of the document property. Valid properties are:
        DocumentUrl
        SrcDocumentUrl
        Original
        ApplicationVendor
        ApplicationName
        ApplicationVersion
        DateTime_GMT
        FileName
        LastSaved
        ApplicationVendor
        ApplicationName
        ApplicationVersion
        DateTime_GMT
        DocumentEmbeddedUrl
        SceneThumbnail
        ApplicationActiveProject
        ApplicationNativeFile
    """
    # -- Get the document info
    document_info = scene.GetDocumentInfo()

    # -- Get the first property
    document_property = document_info.GetFirstProperty()

    while document_property.IsValid():
        if document_property.GetName() == property_name:
            # return str(fbx.FbxPropertyString(document_property).Get())
            fbx.FbxPropertyString(document_property).Set(value)
            return
        # -- This was not the property we needed to find, so
        # -- lets move onto the next one
        document_property = document_info.GetNextProperty(document_property)

    # -- If we could not find the property then we
    # -- return an empty string
    return


def set_properties(scene: fbx.FbxScene, properties: dict):
    """
    This will set the properties of the document using a value of key
    value pairs
    """
    # -- Get the document info
    document_info = scene.GetDocumentInfo()

    # -- Get the first property
    document_property = document_info.GetFirstProperty()

    while document_property.IsValid():

        # -- Get the name of the property and if its in the dictionary
        # -- then lets set it
        property_name = str(document_property.GetName())
        if property_name in properties:
            fbx.FbxPropertyString(document_property).Set(properties[property_name])

        # -- Now we can move onto the next one
        document_property = document_info.GetNextProperty(document_property)

