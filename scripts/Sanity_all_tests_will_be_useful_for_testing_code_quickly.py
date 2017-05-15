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

number_of_volumes_to_create = 2
extension_factor_input = 30
number_of_snapshots_per_volume = 2
volumes_name_prefix = str(sys.argv[1])

server_name =  'qe' + '_server_' + str(time.time())# ACTION : Should be combination of testname, qe, server, timestamp of creation

# Object Instantiation for volumes
os_objects_handle_volume = VolumeOperations()

# MULTIPLE NON BOOTABLE VOLUME CREATION
non_bootable_volume_list = os_objects_handle_volume.volumes_create(volumes_name_prefix = volumes_name_prefix,
                                                                   number_of_volumes=number_of_volumes_to_create)

# EXTEND VOLUME
non_bootable_volume_list = os_objects_handle_volume.volumes_extend(volume_input_list =
                                                                            non_bootable_volume_list,
                                                                            extension_factor = extension_factor_input)
# Object Instantiation for snapshots
os_objects_handle_snapshots = SnapshotOperations()

# SNAPSHOT CREATION OF UNATTACHED VOLUMES
print "\nMAIN SCRIPT : SNAPSHOT CREATE..."
(input_volume_list, created_snapshot_list, volume_snapshot_mapping, snapshot_matrix) = \
                                                                        os_objects_handle_snapshots.snapshots_create(
                                                                        snapshot_prefix = "QE_",
                                                                        volume_list = non_bootable_volume_list,
                                                                        number_of_snapshots_per_volume=
                                                                        number_of_snapshots_per_volume)
# CREATE VOLUMES FROM SOURCE=SNAPSHOT
print "\nMAIN SCRIPT : VOLUME CREATE FROM SNAPSHOT"
volume_cloned_from_snapshot_prefix = 'cloned_from_snapshot'
cloned_from_snapshot_list = os_objects_handle_volume.volumes_clone(type_of_source = "snapshot",
                                                                   input_volume_list = non_bootable_volume_list,
                                                                   created_snapshot_list = snapshot_matrix,
                                                                   name_prefix_of_target =
                                                                   volume_cloned_from_snapshot_prefix,
                                                                   number_of_snapshots_per_volume=
                                                                   number_of_snapshots_per_volume)

# CREATE VOLUMES FROM SOURCE=NON BOOTABLE VOLUME
print "\nMAIN SCRIPT : VOLUME CREATE FROM NON BOOTABLE VOLUME"
volume_cloned_from_volume_prefix = 'cloned_from_vol'
cloned_from_non_bootable_volume_list = os_objects_handle_volume.volumes_clone(type_of_source = "volume",
                                                                              input_volume_list =
                                                                              non_bootable_volume_list,
                                                                              name_prefix_of_target =
                                                                              volume_cloned_from_volume_prefix)
# DELETE ALL SNAPSHOTS
print "\nMAIN SCRIPT : VOLUME SNAPSHOT DELETION"
snapshot_delete = os_objects_handle_snapshots.snapshots_delete(volume_list_for_snapshots = non_bootable_volume_list,
                                                               volume_snapshot_names_dict = volume_snapshot_mapping,
                                                               number_of_snapshots_per_volume=
                                                               number_of_snapshots_per_volume)

# # INSTANCE CREATION
# os_objects_handle_server = InstanceOperations(server_name,image,flavor)
# print "\nMAIN SCRIPT : INSTANCE CREATION..." , os_objects_handle_server.server_create()
#
# # ATTACH VOLUME
# print "\nMAIN SCRIPT : VOLUME ATTACH...",os_objects_handle_server.volume_attach(volume_name)
#

# # DETACH VOLUMES
# print "\nMAIN SCRIPT : DETACH VOLUME..."
# volume_detach = os_objects_handle_server.volume_detach(volume_name)
#

# DELETE ALL VOLUMES
print "\nMAIN SCRIPT : VOLUME DELETION"
volume_delete_non_bootable = os_objects_handle_volume.volumes_delete(volume_delete_list = non_bootable_volume_list)
volume_delete_cloned_from_snapshot = os_objects_handle_volume.volumes_delete(volume_delete_list = cloned_from_snapshot_list)
volume_delete_cloned_from_volume = os_objects_handle_volume.volumes_delete(volume_delete_list = cloned_from_non_bootable_volume_list)