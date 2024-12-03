#! encoding = utf-8


try:
    import importlib.resources as resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as resources
from pathlib import Path
import re
import numpy as np
import os


# ------------------------------------------
# ------ MESSAGE CONSTANT DECLARATION ------
# ------------------------------------------
VERSION = '1.2.2'

_FILE_ERR_MSG = {0: '',  # Silent
                 1: '{:s} does not exist',  # FileNotFoundError
                 2: '{:s} format is not supported',  # Format Issue
                 }

def split_filename_dir(filename: str) -> tuple[str, str]:
    """Split the filename and directory string.

    Arguments
    ---------
    filename : str
        The full path of the file as a string.

    Returns
    -------
    dir_ : str
        Directory string. If no directory part is present, returns an empty string.
    name : str
        Filename string. If the path ends with a separator, it returns an empty string.
    """
    if not filename:
        return '', ''

    dir_, name = os.path.split(filename)
    return dir_, name


def get_abs_path(package, resource):
    """ Get the absolute path of the resource file in package.

    importlib_resources offers a convenient way to import resources just as
    importing modules, but its API returns either a context manager, or
    directly reads the resource file.

    In the case we need the actual path string of the resource file,
    we have to hack this library to use its underlying methods,
    which is based on os.path and pathlib.

    Arguments
        package: str            package name
        resource: str           resource name
    Returns
        abs_path: str           absolute path of the resource file
    """

    if hasattr(resources, '_py3'):
        # backwords compatibility for Python <=3.6
        pkg = resources._py3._get_package(package)
        if pkg.__spec__.origin == 'namespace':   # the root module
            pkg_dir_str = pkg.__path__._path[0]
        else:
            pkg_dir_str = pkg.__path__[0]
        pkg_dir = Path(pkg_dir_str).resolve()
        abs_path = str(pkg_dir.joinpath(resource))
    elif hasattr(resources, '_get_package'):
        pkg = resources._get_package(package)
        if pkg.__spec__.origin == 'namespace':   # the root module
            pkg_dir_str = pkg.__spec__.origin
            pkg_dir = Path(pkg_dir_str).resolve().parent
        else:
            pkg_dir_str = pkg.__spec__.submodule_search_locations._path[0]
            pkg_dir = Path(pkg_dir_str).resolve()
        abs_path = str(pkg_dir.joinpath(resource))
    else:
        with resources.path(package, resource) as f:
            abs_path = str(f)

    return abs_path


def load_xy_file(file_name, maxrow=10):
    """ Load single xy data file, resulting array is sorted by x
    If file is .npz, do not sort (assuming that it is already sorted)

    Arguments:
        file_name: str          input file name
        maxrow: int             maximum number of rows for pattern matching
    Returns:
        sorted_result: np.array          sorted data array
    """

    # test if the file is .npz binary. If so, skip sorting
    if file_name.endswith('.npz'):
        try:
            data = np.load(file_name)
            return data['arr_0']
        except IOError:
            raise ValueError(_err_msg_str(file_name, 2))
        except ValueError:
            raise ValueError(_err_msg_str(file_name, 3))
    # test if the file is .npy binary
    elif file_name.endswith('.npy'):
        try:
            data = np.load(file_name, mmap_mode='c', allow_pickle=False)
            sorted_indices = np.argsort(data[:, 0])
            sorted_result = data[sorted_indices]
            return sorted_result
        except IOError:
            raise ValueError(_err_msg_str(file_name, 2))
        except ValueError:
            raise ValueError(_err_msg_str(file_name, 3))
    else:
        try:
            delm, n_hd, is_eof = _txt_fmt(file_name, maxrow)
            if is_eof or isinstance(delm, type(None)):
                raise ValueError(_err_msg_str(file_name, 2))
            else:
                if delm == ' ':
                    data = np.loadtxt(file_name, skiprows=n_hd)
                else:
                    data = np.loadtxt(file_name, delimiter=delm, skiprows=n_hd)
                # sort the data
                sorted_indices = np.argsort(data[:, 0])
                sorted_result = data[sorted_indices]
                return sorted_result
        except FileNotFoundError:
            raise ValueError(_err_msg_str(file_name, 1))
        except ValueError:
            raise ValueError(_err_msg_str(file_name, 2))


def _err_msg_str(f, err_code, msg=_FILE_ERR_MSG):
    """ Generate file error message string

    Arguments:
    f        -- file name, str
    err_code -- error code, int
    msg      -- error message, dict

    Returns:
    msg_str -- formated error message, str
    """

    return (msg[err_code]).format(f)


def _txt_fmt(file_name, maxrow):
    """ Analyze the data text format: delimiter and header

    Arguments:
        file_name: str          input data file name
        maxrow: int             maximum number of rows for pattern matching

    Returns:
        delm: str           delimiter character
        n_hd: int           number of header rows
        is_eof: bool        end of file
    """

    n_hd = 0
    delm = None
    a_file = open(file_name, 'r')
    # match two numbers and a delimiter
    pattern = re.compile(r"(-?[0-9]+\.?[0-9]*([dDeE]?[-+]?[0-9]+)?)( |\t|,)+(-?[0-9]+\.?[0-9]*([dDeE]?[-+]?[0-9]+)?)")

    for a_line in a_file:
        if re.match('-?\\d+\.?\\d*(e|E)?.?\\d+ *$', a_line):
            # if the first line is a pure number
            delm = ','
            break
        else:
            try:
                delm = pattern.match(a_line.strip()).groups()[2]
                break
            except AttributeError:
                n_hd += 1
        if n_hd > maxrow:
            break

    # check if end of the file is reached
    is_eof = (a_file.read() == '')

    a_file.close()

    return delm, n_hd, is_eof

