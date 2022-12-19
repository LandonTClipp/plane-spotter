import pathlib

import plane_spotter


def package_path() -> pathlib.Path:
    return pathlib.Path(plane_spotter.__file__).parent


def data_path() -> pathlib.Path:
    """
    Returns the path of this package's data directory
    """
    return package_path().joinpath("data")


def airport_code_path() -> pathlib.Path:
    return data_path().joinpath("airport-codes.csv")
