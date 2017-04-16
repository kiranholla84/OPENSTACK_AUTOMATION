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
type_vol = 'VMAX_SILVER'
image = 'cirros-0.3.4-x86_64-uec' #Keep a function here to get the value automatically.
flavor = 'm1.tiny'
no_attach = []
replication_status = None
volume_available_string = 'available'
server_available_string = 'ACTIVE'
bootable_string = 'true'
new_volume_size = size_vol +  10
non_rep_vol_type = 'VMAX_SILVER'
volume_name = 'qe_' + non_rep_vol_type + '_' + str(time.time()) # ACTION : Should be combination of testname, qe, volume,  timestamp of creation
volume_from_volume = 'cloned_from_' + volume_name

server_name =  'qe' + '_server_' + str(time.time())# ACTION : Should be combination of testname, qe, server, timestamp of creation
server_from_bootable_volume = 'qe_server_From_bootable_volume'+ "_" + str(time.time())
volume_name_bootable = 'qe_volume_bootable' + "_" + str(time.time())
number_of_snapshots = 1

# #PRESETUP : Volume Creation Action
os_objects_handle_volume = VolumeOperations("nonBootable", "nonReplicated", 5 , non_rep_vol_type, volume_name)
non_bootable_volume_list = os_objects_handle_volume.volumes_create()
print "non_bootable_volume_list is", non_bootable_volume_list

#PRESET TEST : SNAPSHOT CREATION
print "\nVOLUME SNAPSHOT CREATION"
snapshot_name_1 = os_objects_handle_volume.volume_snapshot_create(volume_name, number_of_snapshots)
volume_from_snapshot = 'cloned_from_snapshot_' + snapshot_name_1

# ACTUAL TEST : CREATE VOLUMES FROM SOURCE=SNAPSHOT
result_snapshot_os_objects_handle_volume = os_objects_handle_volume.volumes_clone("snapshot", snapshot_name_1, volume_from_snapshot)

# ACTUAL TEST : CREATE VOLUMES FROM SOURCE=VOLUME
result_clone_os_objects_handle_volume = os_objects_handle_volume.volumes_clone("volume",volume_name, volume_from_volume)

# TEARDOWN
os_objects_handle_volume.volume_snapshot_delete(snapshot_name_1)
volume_delete = os_objects_handle_volume.volume_delete(volume_name)
volume_delete = os_objects_handle_volume.volume_delete(volume_from_volume)







