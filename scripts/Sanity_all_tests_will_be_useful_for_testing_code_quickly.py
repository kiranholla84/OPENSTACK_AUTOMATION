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
size_vol = 65
type_vol = 'VMAX_SILVER'
image = 'cirros-0.3.4-x86_64-uec' #Keep a function here to get the value automatically.
flavor = 'm1.tiny'
no_attach = []
replication_status = None
volume_available_string = 'available'
server_available_string = 'ACTIVE'
bootable_string = 'true'
non_rep_vol_type = 'VMAX_SILVER'
# number_of_snapshot_per_volume = 3
# volume_name = 'qe_' + non_rep_vol_type + '_' + str(time.time()) # ACTION : Should be combination of testname, qe, volume,  timestamp of creation

server_name =  'qe' + '_server_' + str(time.time())# ACTION : Should be combination of testname, qe, server, timestamp of creation
number_of_snapshots = 1

# Object instatiation [May be modularized]
os_objects_handle_volume = VolumeOperations(bootable_factor = 'nonbootable', volumes_name_prefix = 'INDAA990_l99', number_of_volumes=2)

# MULTIPLE VOLUME CREATION
print "\nMAIN SCRIPT : VOLUME CREATE..."
non_bootable_volume_list = os_objects_handle_volume.volumes_create()
print "\nMAIN SCRIPT : NONBOOTABLE VOLUME LIST IS %s" %non_bootable_volume_list

# Object Instantiation
os_objects_handle_snapshots = SnapshotOperations()

# os_objects_handle_volume = VolumeOperations(bootable_factor = 'bootable', volumes_name_prefix = 'INDAA96', number_of_volumes=2)
# bootable_volume_list = os_objects_handle_volume.volumes_create()
# print "\nMAIN SCRIPT : NONBOOTABLE VOLUME LIST IS %s" %bootable_volume_list

# # MULTIPLE VOLUME CREATION
# print "\nMAIN SCRIPT : VOLUME CREATE..."
# bootable_volume_list = os_objects_handle_volume.volumes_create()
# print "\nMAIN SCRIPT : BOOTABLE VOLUME LIST IS %s" %bootable_volume_list
#
# # # EXTEND VOLUME
# # extend_val = os_objects_handle_volume.volumes_extend(bootable_volume_list, extension_factor = 10)
# extend_val = os_objects_handle_volume.volumes_extend(bootable_volume_list, extension_factor = 20)
# print "\nMAIN SCRIPT : VOLUME EXTEND...%s" %(extend_val)
# #

# SNAPSHOT CREATION OF UNATTACHED VOLUMES
print "\nMAIN SCRIPT : SNAPSHOT CREATE..."
snapshot_name_dict = os_objects_handle_snapshots.snapshots_create(non_bootable_volume_list, number_of_snapshot_per_volume=3)

# print the list of volume:snapshot pairs
for volumes, snapshots in snapshot_name_dict.iteritems():
    print "\nVOLUME %s" % volumes
    print "\nSNAPSHOTS %s" % snapshots

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
# DELETE SNAPSHOTS
print "\nMAIN SCRIPT : VOLUME SNAPSHOT DELETION"
snapshot_delete = os_objects_handle_snapshots.snapshots_delete(non_bootable_volume_list, snapshot_name_dict, number_of_snapshot_per_volume=3)
print "DEBUG: snapshot delete is %s" %snapshot_delete
# snapshot_delete = os_objects_handle_volume.volume_snapshot_delete(snapshot_name_1)
# snapshot_delete = os_objects_handle_volume.volume_snapshot_delete(snapshot_name_2)

# DELETE VOLUMES
print "\nMAIN SCRIPT : VOLUME DELETION"
volume_delete = os_objects_handle_volume.volumes_delete(non_bootable_volume_list)
print "DEBUG: volume_delete is %s" %volume_delete
# volume_delete = os_objects_handle_volume.volume_delete(volume_from_snapshot)
# volume_delete = os_objects_handle_volume.volume_delete(volume_from_volume)

# # DELETE SERVER
# "\nMAIN SCRIPT : SERVER DELETION"
# server_delete = os_objects_handle_server.server_delete(server_name)



