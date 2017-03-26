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

# ACTION : YOU NEED TO GET THESE DATA FROM JSON , USE A FUNCTION CALL AS PART OF PRESETUP
o_chdir = os.chdir("/opt/stack/devstack")
size_vol = 5
new_volume_size = size_vol +  10
type_vol = 'VMAX_SILVER'
image = 'cirros-0.3.4-x86_64-uec' #Keep a function here to get the value automatically.
flavor = 'm1.tiny'
no_attach = []
replication_status = None
volume_available_string = 'available'
server_available_string = 'ACTIVE'
bootable_string = 'true'
new_volume_size = size_vol +  10
non_rep_vol_type = 'VMAX_MPS_SILVER_NONE'
volume_name = 'qe_' + non_rep_vol_type + '_' + str(time.time()) # ACTION : Should be combination of testname, qe, volume,  timestamp of creation
server_name =  'qe' + '_server_' + str(time.time())# ACTION : Should be combination of testname, qe, server, timestamp of creation
server_from_bootable_volume = 'qe_server_From_bootable_volume'+ "_" + str(time.time())
volume_name_bootable = 'qe_volume_bootable' + "_" + str(time.time())

# #PRESETUP : Volume Creation Action
os_objects_handle_volume = VolumeOperations("nonBootable", "nonReplicated", 5 , non_rep_vol_type, volume_name)
non_bootable_volume_list = os_objects_handle_volume.volumes_create()

# ACTUAL TEST  : EXTEND VOLUMES
print "\nVOLUME EXTEND...",os_objects_handle_volume.volume_extend(volume_name, new_volume_size)

# TEARDOWN
volume_delete = os_objects_handle_volume.volume_delete(volume_name)







