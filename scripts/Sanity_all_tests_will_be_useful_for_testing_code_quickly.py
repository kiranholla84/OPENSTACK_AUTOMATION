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
# volume_name = 'qe_' + non_rep_vol_type + '_' + str(time.time()) # ACTION : Should be combination of testname, qe, volume,  timestamp of creation
volume_name = 'test_volume_qe'
server_name =  'qe' + '_server_' + str(time.time())# ACTION : Should be combination of testname, qe, server, timestamp of creation
number_of_snapshots = 1

# VOLUME CREATION
print "\nMAIN SCRIPT : VOLUME CREATE..."
os_objects_handle_volume = VolumeOperations("nonBootable", "nonReplicated", 2 , non_rep_vol_type, volume_name)
non_bootable_volume_list = os_objects_handle_volume.volumes_create()
#
# # EXTEND VOLUME
# print "\nMAIN SCRIPT : VOLUME EXTEND...",os_objects_handle_volume.volume_extend(volume_name, new_volume_size)
#
# # SNAPSHOT CREATION OF UNATTACHED VOLUME
# print "\nMAIN SCRIPT : SNAPSHOT CREATE..."
# snapshot_name = os_objects_handle_volume.volume_snapshot_create(volume_name, number_of_snapshots)
#
# # INSTANCE CREATION
# os_objects_handle_server = InstanceOperations(server_name,image,flavor)
# print "\nMAIN SCRIPT : INSTANCE CREATION..." , os_objects_handle_server.server_create()
#
# # ATTACH VOLUME
# print "\nMAIN SCRIPT : VOLUME ATTACH...",os_objects_handle_server.volume_attach(volume_name)
#
# # SNAPSHOT CREATION OF ATTACHED VOLUME
# print "\nMAIN SCRIPT : SNAPSHOT CREATE..."
# snapshot_name_1 = os_objects_handle_volume.volume_snapshot_create(volume_name, number_of_snapshots)
#
# # DETACH VOLUMES
# print "\nMAIN SCRIPT : DETACH VOLUME..."
# volume_detach = os_objects_handle_server.volume_detach(volume_name)
#
# # SNAPSHOT CREATION OF NORMAL VOLUME AFTER DETACH
# print "\nMAIN SCRIPT : SNAPSHOT CREATE..."
# snapshot_name_2 = os_objects_handle_volume.volume_snapshot_create(volume_name, number_of_snapshots)
#
# # CREATE VOLUMES FROM SOURCE=SNAPSHOT
# print "\nMAIN SCRIPT : VOLUME CREATE FROM SNAPSHOT"
# volume_from_snapshot = 'cloned_from_' + snapshot_name
# result_snapshot_os_objects_handle_volume = os_objects_handle_volume.volumes_clone("snapshot", snapshot_name, volume_from_snapshot)
#
# # CREATE VOLUMES FROM SOURCE=VOLUME
# print "\nMAIN SCRIPT : VOLUME CREATE FROM VOLUME"
# volume_from_volume = 'cloned_from_' + volume_name
# result_clone_os_objects_handle_volume = os_objects_handle_volume.volumes_clone("volume",volume_name, volume_from_volume)
#
# # DELETE SNAPSHOTS
# print "\nMAIN SCRIPT : VOLUME SNAPSHOT DELETION"
# snapshot_delete = os_objects_handle_volume.volume_snapshot_delete(snapshot_name)
# snapshot_delete = os_objects_handle_volume.volume_snapshot_delete(snapshot_name_1)
# snapshot_delete = os_objects_handle_volume.volume_snapshot_delete(snapshot_name_2)

# DELETE VOLUMES
"\nMAIN SCRIPT : VOLUME DELETION"
volume_delete = os_objects_handle_volume.volume_delete(volume_name)
print "volume_delete is %s" %volume_delete
# volume_delete = os_objects_handle_volume.volume_delete(volume_from_snapshot)
# volume_delete = os_objects_handle_volume.volume_delete(volume_from_volume)

# # DELETE SERVER
# "\nMAIN SCRIPT : SERVER DELETION"
# server_delete = os_objects_handle_server.server_delete(server_name)



