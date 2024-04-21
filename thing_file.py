"""
Source code written by Kartik Bulusu
==== Description:
======== Creating a Universally Unique ID (uuid) for IoT demonstration in CS4907   
==== Testing:
==== 1. Developed on 02/22/2024 using Python 3.10.11 on Macbook Pro using Thonny IDE
====
"""

import os
import sys
import logging
from uuid import uuid1

# Initialize Logging
logging.basicConfig(level=logging.WARNING)  # Global logging configuration
logger = logging.getLogger('main')  # Logger for this module
logger.setLevel(logging.INFO)  # Debugging for this file. 

def resolve_thing_name(thing_file):
    """Get existing, or create a new thing name"""
    if os.path.exists(thing_file):                                                 # (3)
        with open(thing_file, 'r') as file_handle:
            name = file_handle.read()
            logger.info('Thing name ' + name + ' loaded from ' + thing_file)
            return name.strip()
    else:
        name = str(uuid1())[:8]  # UUID object to string.                          # (4)
        logger.info('Created new thing name ' + name)

        with open(thing_file, 'w') as f:                                           # (5)
            f.write(name)

    return name

THING_NAME_FILE = 'thing_name.txt'  # The name of our "thing" is persisted into this file
thing_name = resolve_thing_name(THING_NAME_FILE)