import pcbnew  # type: ignore
import os
import json

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

def get_user_options_file_path():
    boardFilePath = pcbnew.GetBoard().GetFileName()
    return os.path.join(os.path.dirname(boardFilePath), 'jlc-plugin-options.json')

def load_user_options(default_options):
    try:
        with open(get_user_options_file_path(), 'r') as f:
            user_options = json.load(f)
    except:
        user_options = default_options

    # merge the user options with the default options
    options = default_options.copy()
    options.update(user_options)
    return options

def save_user_options(options):
    with open(get_user_options_file_path(), 'w') as f:
        json.dump(options, f)