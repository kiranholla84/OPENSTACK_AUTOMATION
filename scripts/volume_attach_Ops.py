import subprocess
import os
from json import loads
from json import dumps
from pprint import pprint as pp
import ast
import time
import sys
import re

sys.path.insert(0,"../lib")
from os_objects import *

non_rep_vol_type = 'VMAX_SILVER'
volume_name = 'qe_' + non_rep_vol_type + '_' + str(time.time())

os_objects_handle = VolumeOperations("nonBootable", "nonReplicated", 5 , non_rep_vol_type, volume_name)
non_bootable_volume_list = os_objects_handle.volumes_create()




