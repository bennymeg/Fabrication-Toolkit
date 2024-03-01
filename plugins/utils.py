import pcbnew  # type: ignore

def get_version():
    return float('.'.join(pcbnew.GetBuildVersion().split(".")[0:2]))  # e.g GetBuildVersion(): e.g. '7.99.0-3969-gc5ac2337e4'

def is_v9(version = get_version()):
    return version >= 8.99 and version < 9.99

def is_v8(version = get_version()):
    return version >= 7.99 and version < 8.99

def is_v7(version = get_version()):
    return version >= 6.99 and version < 7.99

def is_v6(version = get_version()):
    return version >= 5.99 and version < 6.99
                 
def footprint_has_field(footprint, field_name):
    version = get_version()
    
    if is_v8(version) or is_v9(version):
        return footprint.HasFieldByName(field_name)
    else:
        return footprint.HasProperty(field_name)

def footprint_get_field(footprint, field_name):
    version = get_version()
    
    if is_v8(version) or is_v9(version):
        return footprint.GetFieldByName(field_name).GetText()
    else:
        return footprint.GetProperty(field_name)
