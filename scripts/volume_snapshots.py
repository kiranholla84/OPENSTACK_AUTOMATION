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
non_rep_vol_type = 'volume_snapshots.py'
volume_name = 'qe_' + non_rep_vol_type + '_' + str(time.time()) # ACTION : Should be combination of testname, qe, volume,  timestamp of creation
server_name =  'qe' + '_server_' + str(time.time())# ACTION : Should be combination of testname, qe, server, timestamp of creation
server_from_bootable_volume = 'qe_server_From_bootable_volume'+ "_" + str(time.time())
volume_name_bootable = 'qe_volume_bootable' + "_" + str(time.time())
number_of_snapshots = 1

# #PRESETUP : Volume Creation Action
os_objects_handle_volume = VolumeOperations("nonBootable", "nonReplicated", 5 , non_rep_vol_type, volume_name)
non_bootable_volume_list = os_objects_handle_volume.volumes_create()

# # #PRESETUP : Bootable Volume Creation Action
# os_objects_handle_volume_bootable = VolumeOperations("bootable", "nonReplicated", 5 , non_rep_vol_type, volume_name_bootable)
# bootable_volume_list = os_objects_handle_volume_bootable.volumes_create()

# # #PRESETUP : Instance Creation Action
# os_objects_handle_server = InstanceOperations(server_name,image,flavor)
# print "\nINSTANCE CREATION..." , os_objects_handle_server.server_create()
#
# # PRESETUP TEST  : ATTACH VOLUMES
# print "\nVOLUME ATTACH...",os_objects_handle_server.volume_attach(volume_name)
# print "\nVOLUME ATTACH...",os_objects_handle_server.volume_attach(volume_name_bootable)

#ACTUAL TEST : SNAPSHOT CREATION
print "\nVOLUME SNAPSHOT CREATION"
snapshot_name = os_objects_handle_volume.volume_snapshot_create(volume_name, number_of_snapshots)
print "\nVOLUME SNAPSHOT DELETION" , os_objects_handle_volume.volume_snapshot_delete(snapshot_name)

# TEARDOWN
# volume_detach = os_objects_handle_server.volume_detach(volume_name)
volume_delete = os_objects_handle_volume.volume_delete(volume_name)
# volume_detach = os_objects_handle_volume_bootable.volume_detach(volume_name_bootable)
# volume_delete = os_objects_handle_volume_bootable.volume_delete(volume_name_bootable)
# server_delete = os_objects_handle_server.server_delete(server_name)



