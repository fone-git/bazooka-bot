import yaml
from opylib.files_folders import mkdir

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def export(fn: str, data):
    """
    Saves the key value pairs from data to a yaml file with name fn
    :param fn: Name of the file to export the values to
    :param data: The dict like object to get the keys from
    """
    exp_dict = {}
    for key in data.keys():
        exp_dict[key] = data[key]
    with open(fn, 'w') as f:
        f.write(yaml.dump(exp_dict, Dumper=Dumper))


def debug_dump(folder_name: str, data, ext: str = '.yml'):
    """
    Saves the data to the folder specified with each key going to separate file
    :param folder_name: The folder to store the file for each key in
    :param data: The dictionary like object to save
    :param ext: The extension to put of the exported files
    """
    mkdir(folder_name)
    for key in data.keys():
        with open(f'{folder_name}{key}{ext}', 'w') as f:
            f.write(str(data[key]))


def is_power_of_2(value):
    """
    Checks if value is a power of the 2
    :param value: To be checked
    :return: True if value is a power of 2 else false
    """
    return (value & (value - 1)) == 0
    # Taken from
    # https://www.ritambhara.in/check-if-number-is-a-power-of-2/#:~:text
    # =Method%2D2%3A%20Keep%20dividing%20by,is%20a%20power%20of%202.
    #
    # This uses two facts:
    # 1 - If the number is a power of two, then only 1 bit will be set in its
    #   binary representation.
    # 2 - If we subtract 1 from a number which is power of 2,
    #   then all the bits after the set-bit (there is only one set bit as per
    #   point-1) will become set and the set bit will be unset. i.e:


def discord_make_bold(value) -> str:
    return f'**{value}**'
