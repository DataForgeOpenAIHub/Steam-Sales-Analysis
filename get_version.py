import warnings

import versioneer

if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        version = versioneer.get_version()
        print(version)
