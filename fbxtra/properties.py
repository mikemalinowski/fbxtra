import fbx


# ------------------------------------------------------------------------------
def get_value(fbx_property):
    """
    Get the value of a property, which requires casting.

    This code is taken from :
    https://gist.github.com/Meatplowz/8f408912cf554f2d11085fb68b62d3a3

    :param fbx_property: The property to request the value from
    :type fbx_property: fbx.FbxProperty

    :return: variable
    """
    unsupported_types = [
        fbx.eFbxUndefined,
        fbx.eFbxChar,
        fbx.eFbxUChar,
        fbx.eFbxShort,
        fbx.eFbxUShort,
        fbx.eFbxUInt,
        fbx.eFbxLongLong,
        fbx.eFbxHalfFloat,
        fbx.eFbxDouble4x4,
        fbx.eFbxEnum,
        fbx.eFbxTime,
        fbx.eFbxReference,
        fbx.eFbxBlob,
        fbx.eFbxDistance,
        fbx.eFbxDateTime,
        fbx.eFbxTypeCount,
    ]

    # property is not supported or mapped yet
    casted_property = None
    property_type = fbx_property.GetPropertyDataType().GetType()

    if property_type in unsupported_types:
        return None

    if property_type == fbx.eFbxBool:
        casted_property = fbx.FbxPropertyBool1(fbx_property)

    elif property_type == fbx.eFbxDouble:
        casted_property = fbx.FbxPropertyDouble1(fbx_property)

    elif property_type == fbx.eFbxDouble2:
        casted_property = fbx.FbxPropertyDouble2(fbx_property)

    elif property_type == fbx.eFbxDouble3:
        casted_property = fbx.FbxPropertyDouble3(fbx_property)

    elif property_type == fbx.eFbxDouble4:
        casted_property = fbx.FbxPropertyDouble4(fbx_property)

    elif property_type == fbx.eFbxInt:
        casted_property = fbx.FbxPropertyInteger1(fbx_property)

    elif property_type == fbx.eFbxFloat:
        casted_property = fbx.FbxPropertyFloat1(fbx_property)

    elif property_type == fbx.eFbxString:
        casted_property = fbx.FbxPropertyString(fbx_property)

    else:
        raise ValueError(
            'Unknown property type: {0} {1}'.format(
                fbx_property.GetPropertyDataType().GetName(),
                property_type,
            ),
        )

    return casted_property.Get()


# ------------------------------------------------------------------------------
def find(node, property_name):
    """
    Finds a property by comparing the GetName() to the property_name

    :param node: Node to search properties for
    :type node: fbx.FbxObject

    :param property_name: Name of property (wholesome) to match
    :type property_name: str

    :return: fbx.FbxProperty or None
    """
    matched = None
    prop = node.GetFirstProperty()
    while prop.IsValid():

        if prop.GetName() == property_name:
            matched = prop
            break

        prop = node.GetNextProperty(prop)

    return matched


# ------------------------------------------------------------------------------
def get_all(node):
    """
    Returns all the properties on a given fbx node

    :param node: Not to search properties for
    :type node: fbx.FbxNode

    :return: list(fbx.FbxProperty, ...)
    """

    results = list()
    prop = node.GetFirstProperty()
    while prop.IsValid():
        results.append(prop)
        prop = node.GetNextProperty(prop)

    return results


# ------------------------------------------------------------------------------
def all_of_type(node, property_type):
    """
    Returns all the properies of a given type

    :param node: Not to search properties for
    :type node: fbx.FbxNode

    :param property_type: fbx Type

    :return: list(FbxProperty, FbxProperty, ...)
    """
    results = list()
    prop = node.GetFirstProperty()
    while prop.IsValid():

        if prop.GetPropertyDataType() == property_type:
            results.append(prop)

        prop = node.GetNextProperty(prop)

    return results


# --------------------------------------------------------------------------------------
def add_property(node, name, property_type, default_value, flags=None):
    """
    Adds a property to a node
    
    :param node: The node to add a property to
    :type node: fbx.FbxNode
    
    :param name: The name/label to assign to the property
    :type name: str
    
    :param property_type: The FbxProperty type to assign (such as fbx.FbxDoubleDT)
    :type property_type: FbxDataType
    
    :param default_value: The value to assign to the property on creation
    :type default_value: Variable
    
    :param flags: Any flags you want to assign
    :type flags: dict
    
    :return: FbxProperty
    """

    property_ = fbx.FbxProperty.Create(
        node, 
        property_type, 
        name,
        name,
    )
    
    flags_to_apply = {
        fbx.FbxPropertyFlags.eUserDefined: True,
        fbx.FbxPropertyFlags.eHidden: False,
        fbx.FbxPropertyFlags.eUIHidden: False,
        fbx.FbxPropertyFlags.eAnimatable: True,
    }
    flags_to_apply.update(flags or dict())
    
    for flag, value in flags_to_apply.items():
        property_.ModifyFlag(
            flag,
            value,
        )
        
    property_.Set(default_value)
    property_.ConnectSrcObject(node)
    
    return property_
