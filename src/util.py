#!/user/bin/env python3

import os


#------------------------------------------------------------------------------------
# Create a new directory at the location
#------------------------------------------------------------------------------------
def create_dir(dirpath):
    try:
        os.makedirs(dirpath, exist_ok=False)
    except OSError:
        pass
