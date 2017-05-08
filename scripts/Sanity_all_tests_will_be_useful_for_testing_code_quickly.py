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


number_of_volumes_to_create = 3
extension_factor_input = 30
number_of_snapshot_per_volume = 3

server_name =  'qe' + '_server_' + str(time.time())# ACTION : Should be combination of testname, qe, server, timestamp of creation

# Object Instantiation for volumes
os_objects_handle_volume = VolumeOperations()

# MULTIPLE NON BOOTABLE VOLUME CREATION
non_bootable_volume_list = os_objects_handle_volume.volumes_create(volumes_name_prefix = 'BNG123',
                                                                   number_of_volumes=number_of_volumes_to_create)
#
# # MULTIPLE BOOTABLE VOLUME CREATION
# bootable_volume_list = os_objects_handle_volume.volumes_create(bootable_factor = 'bootable',
#                                                                volumes_name_prefix = 'BNG123',
#                                                                number_of_volumes=number_of_volumes_to_create)
# # EXTEND VOLUME
# non_bootable_volume_list = os_objects_handle_volume.volumes_extend(non_bootable_volume_list,
#                                                      extension_factor = extension_factor_input)
# bootable_volume_list = os_objects_handle_volume.volumes_extend(bootable_volume_list,
#                                                                   extension_factor = extension_factor_input)

# Object Instantiation for snapshots
os_objects_handle_snapshots = SnapshotOperations()

# SNAPSHOT CREATION OF UNATTACHED VOLUMES
print "\nMAIN SCRIPT : SNAPSHOT CREATE..."
(input_volume_list, created_snapshot_list, volume_snapshot_mapping) = os_objects_handle_snapshots.snapshots_create(
                                                                                   non_bootable_volume_list,
                                                                                   number_of_snapshot_per_volume=
                                                                                   number_of_snapshot_per_volume)

# CREATE VOLUMES FROM SOURCE=SNAPSHOT
print "\nMAIN SCRIPT : VOLUME CREATE FROM SNAPSHOT"
volume_cloned_from_snapshot_prefix = 'cloned_from_'
cloned_from_snapshot_list = os_objects_handle_volume.volumes_clone("snapshot",
                                                                   non_bootable_volume_list,
                                                                   created_snapshot_list,
                                                                   volume_cloned_from_snapshot_prefix)

# # CREATE VOLUMES FROM SOURCE=BOOTABLE VOLUME
# print "\nMAIN SCRIPT : VOLUME CREATE FROM BOOTABLE VOLUME"
# volume_cloned_from_volume_prefix = 'cloned_from_bootable_'
# cloned_from_bootable_volume_list = os_objects_handle_volume.volumes_clone("volume",
#                                                                                bootable_volume_list,
#                                                                                volume_cloned_from_volume_prefix)
#
# # CREATE VOLUMES FROM SOURCE=NON BOOTABLE VOLUME
# print "\nMAIN SCRIPT : VOLUME CREATE FROM NON BOOTABLE VOLUME"
# volume_cloned_from_volume_prefix = 'cloned_from_bootable_'
# cloned_from_non_bootable_volume_list = os_objects_handle_volume.volumes_clone("volume",
#                                                                                non_bootable_volume_list,
#                                                                                volume_cloned_from_volume_prefix)

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

#
# DELETE ALL SNAPSHOTS
print "\nMAIN SCRIPT : VOLUME SNAPSHOT DELETION"
snapshot_delete = os_objects_handle_snapshots.snapshots_delete(non_bootable_volume_list,
                                                               dict_of_volume_snapshot_association,
                                                               number_of_snapshot_per_volume=
                                                               number_of_snapshot_per_volume)

# DELETE ALL VOLUMES
print "\nMAIN SCRIPT : VOLUME DELETION"
volume_delete_non_bootable = os_objects_handle_volume.volumes_delete(non_bootable_volume_list)
volume_delete_bootable = os_objects_handle_volume.volumes_delete(bootable_volume_list)

