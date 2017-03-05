import subprocess
import os
from json import loads
from json import dumps
import yaml
from pprint import pprint as pp
import ast
import time
import sys
import re

# This will be the inputs & variable initilizations
volume_name = sys.argv[1]
server_name = sys.argv[2]
volume_name_bootable = volume_name + "_" + "bootable"
print "volume & server" , volume_name , server_name
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
server_from_bootable_volume = 'server_from_bootable_volume'

# function to get the latest status of the volume
def latest_volume_status(volume_name):
    try:
        op = subprocess.check_output(['openstack', 'volume', 'show', volume_name, '-f', 'json'])
        op = yaml.load(op)
        return op
    except subprocess.CalledProcessError as e:
        print "\nTHERE IS NO VOLUME WITH THE NAME %s" %(volume_name)
        return e.returncode

# function to get the latest status of the server
def latest_server_status(server_name):
    try:
        op = subprocess.check_output(['openstack', 'server', 'show', server_name, '-f', 'json'])
        op = yaml.load(op)
        return op
    except subprocess.CalledProcessError as e:
        print "\nTHERE IS NO SERVER WITH THE NAME %s" %(server_name)
        return e.returncode

# function for general pattern matching
def check_pattern_match(pattern,input_string):
    print "pattern is", pattern
    print "string is", input_string

    match_pattern = re.search(pattern,input_string,re.I)
    if match_pattern:
        print "\nPATTERN MATCHED!!!"
        return 1
#
# print "\n\n================CREATING NON-BOOTABLE VOLUME ================\n\n"
# list_checkOutput = ['openstack' ,'volume' ,'create' , '--size', str(size_vol) , '--type' , type_vol , volume_name, '-f','json']
# op = subprocess.check_output(list_checkOutput)
# op = loads(op)
#
# # non-bootable non-attached volume show
# while (op['status'] != 'available'):
#     if (op['status'].lower == 'error'):
#         print "\nFAILURE IN CREATING VOLUME %s. EXITING" % (op['name'])
#         break
#     print "\nWAITING FOR STATUS OF THE VOLUME %s TO BE AVAILABLE. CURRENTLY VOLUME STATE IS IN %s\n" % (op['name'],op['status'])
#     time.sleep(10)
#     op = latest_volume_status(volume_name)
#
#
# print "\n\n================CHECKING FOR THE CREATION OF NON-BOOTABLE VOLUME================\n\n"
# o_chdir = os.chdir("/opt/stack/devstack")
#
# inputs = [volume_name,size_vol,type_vol,no_attach,replication_status,volume_available_string]
# print "\nINPUTS TO CREATE VOLUME" , inputs
#
# values = [(op['name']),op['size'],op['type'],op['attachments'],op['replication_status'],op['status']]
# print "\nVALUES FROM THE CREATED VOLUME", values
#
# if values == inputs :
#     print "\nVOLUME CREATED SUCCESSFULLY\n"
#
# #
# print "\n\n================DELETION OF NON-BOOTABLE VOLUME================\n\n"
# o_chdir = os.chdir("/opt/stack/devstack")
# list_checkOutput_delete = ['openstack' ,'volume' ,'delete' ,  volume_name]
# op = subprocess.check_output(list_checkOutput_delete)
#
# op = latest_volume_status(volume_name)
#
# # Enter only if the volume exists
# if op != 1:
#     while (op['status'] == 'deleting'):
#         print "\nWAITING FOR VOLUME %s TO BE DELETED. CURRENTLY VOLUME STATE IS IN %s\n" % (op['name'], op['status'])
#         time.sleep(10)
#         op = latest_volume_status(volume_name)
#         if op == 1:
#             break
#             print "CURRENT STATUS OF VOLUME IS" , op , "HENCE CONTINUING"
#
# print "\n\n================CREATION OF EMPTY INSTANCE================\n\n"
# instanceCreation_subprocess_ob = ['openstack' ,'server' ,'create' , '--image', image , '--flavor' , flavor , server_name, '-f','json']
# instanceCreated_ob = subprocess.check_output(instanceCreation_subprocess_ob)
# op = loads(instanceCreated_ob)
#
# server_id = op['id']
#
# print "\n\n================CHECKING FOR THE CREATION OF INSTANCE================\n\n"
# o_chdir = os.chdir("/opt/stack/devstack")
#
# # non-bootable non-attached volume show
# while (op['status'] != 'ACTIVE'):
#     if (op['status'].lower == 'error'):
#         print "\nFAILURE IN CREATING SERVER %s. EXITING" % (op['name'])
#         break
#     print "\nWAITING FOR STATUS OF THE SERVER %s TO BE ACTIVE. CURRENTLY STATE IS %s\n" % (op['name'],op['status'])
#     time.sleep(10)
#     op = latest_server_status(server_name)
#
# print "#op during creation is\n" , op
#
# inputs = [server_id,server_name,server_available_string]
# print "\nINPUTS TO CREATE INSTANCE" , inputs
#
# values = [op['id'],op['name'],op['status']]
# print "\nVALUES FROM THE CREATED VOLUME", values
#
# if values == inputs :
#     print "\nINSTANCE CREATED SUCCESSFULLY\n"
#
# print "\n\n================DELETION OF INSTANCE================\n\n"
# o_chdir = os.chdir("/opt/stack/devstack")
# instance_delete = ['openstack' ,'server' ,'delete', server_name]
# op = subprocess.check_output(instance_delete)
# op = latest_server_status(server_name)
#
# print "#op during deletion is and task state\n" , op , op['OS-EXT-STS:task_state']
#
# # Enter only if the instance exists
# if op['status'] == 'ACTIVE':
#     while (op['OS-EXT-STS:task_state'] == 'deleting'):
#         print "\nWAITING FOR SERVER %s TO BE DELETED. CURRENTLY SERVER STATE IS IN %s\n" % (op['name'], op['OS-EXT-STS:task_state'])
#         time.sleep(10)
#         op = latest_server_status(server_name)
#         if op == 1:
#             break
#         print "CURRENT STATUS OF SERVER IS" , op , "HENCE CONTINUING"

# print "\n\n================VOLUME ATTACH================\n\n"
# volume addition to server or volume attach
# list_check_output = ['openstack' , 'server' , 'add' , 'volume' , server_name, volume_name]
# op_attach_vol = subprocess.check_output(list_check_output)

# # check for addition of volume to server
# op = subprocess.check_output(['openstack' , 'volume' , 'show', volume_name , '-f', 'json'])
# op = yaml.load(op)
#
# print "op is" , op
# attachment_details_server_id = op['attachments'][0]['server_id']
# attachment_details_attachment_id = op['attachments'][0]['attachment_id']
# attachment_details_volume_id = op['attachments'][0]['volume_id']
# attachment_details_device = op['attachments'][0]['device']
#
# print "attachment details" , attachment_details_server_id, attachment_details_attachment_id,attachment_details_volume_id,attachment_details_device

# inputs = [volume_name,size_vol,type_vol,no_attach,replication_status,volume_available_string]
# print "\nINPUTS TO CREATE VOLUME" , inputs
#
# values = [(op['name']),op['size'],op['type'],op['attachments'],op['replication_status'],op['status']]
# print "\nVALUES FROM THE CREATED VOLUME", values

# if values == inputs :
#     print "\nVOLUME ATTACHED SUCCESSFULLY\n"
#
# print "\n\n================VOLUME DETACH================\n\n"
# # volume addition to server or volume attach
# list_check_output = ['openstack' , 'server' , 'remove' , 'volume' , server_name, volume_name]
# op_attach_vol = subprocess.check_output(list_check_output)

## check for addition of volume to server
# op = subprocess.check_output(['openstack' , 'volume' , 'show', volume_name , '-f', 'json'])
# op = yaml.load(op)
#
# print "op is" , op
# print "\n\n\n"
# try:
#     attachment_details_server_id = op['attachments'][0]['server_id']
#     attachment_details_attachment_id = op['attachments'][0]['attachment_id']
#
#     attachment_details_volume_id = op['attachments'][0]['volume_id']
#     attachment_details_device = op['attachments'][0]['device']
# except IndexError:
#     print "There does not seem to be any volume attached to server. Yes!"

# print "attachment details %s :: %s ::  %s :: %s"  %(attachment_details_server_id, attachment_details_attachment_id,attachment_details_volume_id,attachment_details_device)


# # print "\n\n================VOLUME EXTEND================\n\n"
# print "New size is" , new_volume_size
# list_check_output = ['openstack' , 'volume' , 'set' , '--size' , str(new_volume_size), volume_name]
# op_extend_vol = subprocess.check_output(list_check_output)
#
# ## check for extension of volume
# op = subprocess.check_output(['openstack' , 'volume' , 'show', volume_name , '-f', 'json'])
# op = yaml.load(op)
#
# print "NEW SIZE FROM OP" , op['size']
#
# # print "\n\n================VOLUME CLONING================\n\n"
# list_check_output = ['openstack' , 'volume' , 'create' , '--source' , volume_name, cloned_volume_name]
# op_extend_vol = subprocess.check_output(list_check_output)
#
# # Check size, new volume name, old volume name, bootable,status,replication_status
#
# # print "\n\n================VOLUME SNAPSHOT================\n\n"
# snapshot_volume_name = "snapshot" + "_" + volume_name
# list_check_output = ['openstack' , 'volume' ,'snapshot' ,'create' , "--volume" ,volume_name , snapshot_volume_name]
# op_snaps_vol_create = subprocess.check_output(list_check_output)

# # print "\n\n================VOLUME SNAPSHOT CREATION CHECK================\n\n"
# #openstack volume snapshot show snap_qe_vol_silver_99 -f  json
# list_check_output = ['openstack' , 'volume' ,'snapshot' ,'show' , snapshot_volume_name , '-f', 'json']
# op_snaps_vol_show = subprocess.check_output(list_check_output)
# print "Type of snap output is before yaml" , type(op_snaps_vol_show)
#
# op_snaps_vol_show = yaml.load(op_snaps_vol_show)
#
# print "Type of snap output is" , type(op_snaps_vol_show)
#
# # need a delay as it shows "creating" state
# print "From output ", op_snaps_vol_show['name'] , op_snaps_vol_show['volume_id'] , op_snaps_vol_show['status']
#
#
# # print "\n\n================VOLUME SNAPSHOT DELETION================\n\n"
# list_check_output = ['openstack' , 'volume' ,'delete' ,snapshot_volume_name]
#
# op_snaps_vol_show = yaml.load(op_snaps_vol_show)
# need a delay as it shows "deleting" state
## Expected ouput check is for "No snapshot with a name or ID of 'snappy2' exists."

# # Check snapshot name , volume id from which the snapshot was taken, status, size, os-extended-snapshot-attributes
#
# # print "\n\n================VOLUME CLONING FROM SNAPSHOT================\n\n"
# list_check_output = ['openstack' , 'volume' , 'create' , '--source' , snapshot_volume_name, cloned_volume_name]

print "\n\n================CREATING VOLUME FROM IMAGE================\n\n"
##openstack volume create --image cirros-0.3.4-x86_64-uec --type VMAX_SILVER --size 20 qe_neither_bootable_1

# Get the images dynamically
list_check_output = ['openstack' , 'image' , 'list' , '-f' , 'json']
op_image_list = subprocess.check_output(list_check_output)

##** This conversion to yaml is important as it gives the type of theouput in list format. From json output, by default, op_image_list will ocme out as a string :(
op_image_list = yaml.load(op_image_list)
print "\nIMAGE TO BE USED IS" , op_image_list[0]['Name']

list_check_output = ['openstack' , 'volume' , 'create' , '--image' , op_image_list[0]['Name'] , '--type' , type_vol , '--size', str(size_vol) , volume_name_bootable]
op_bootable_volume_create = subprocess.check_output(list_check_output)
op_bootable_volume_create = yaml.load(op_bootable_volume_create)

print "\n\n================CHECKING FOR THE CREATION OF BOOTABLE VOLUME================\n\n"
o_chdir = os.chdir("/opt/stack/devstack")
op_bootable_volume_show = latest_volume_status(volume_name_bootable)
# op_bootable_volume_show = yaml.load(op_bootable_volume_show)

print "\n\nop_bootable_volume_show is" , op_bootable_volume_show

# bootable non-attached volume show
while (op_bootable_volume_show['status'] != 'available'):
    if (op_bootable_volume_show['status'].lower == 'error'):
        print "\nFAILURE IN CREATING VOLUME %s. EXITING" % (op_bootable_volume_show['name'])
        break
    print "\nWAITING FOR STATUS OF THE VOLUME %s TO BE AVAILABLE. CURRENTLY VOLUME STATE IS IN %s\n" % (op_bootable_volume_show['name'],op_bootable_volume_show['status'])
    time.sleep(10)
    op_bootable_volume_show = latest_volume_status(volume_name_bootable)

inputs = [volume_name_bootable,size_vol,type_vol,no_attach,replication_status,volume_available_string, bootable_string]
print "\nINPUTS TO CREATE VOLUME" , inputs

values = [op_bootable_volume_show['name'],op_bootable_volume_show['size'],op_bootable_volume_show['type'],op_bootable_volume_show['attachments'],op_bootable_volume_show['replication_status'],op_bootable_volume_show['status'],op_bootable_volume_show['bootable']]
print "\nVALUES FROM THE CREATED VOLUME", values

if values == inputs :
    print "\nBOOTABLE VOLUME CREATED SUCCESSFULLY\n"

print "\n\n================CREATING AN INSTANCE FROM BOOTABLE VOLUME================\n\n"
# openstack server create --volume qe_vol_silver_19991_bootable --flavor m1.tiny inst_vol
list_check_output = ['openstack' , 'server' , 'create' , '--volume' , volume_name_bootable , '--flavor' , "m1.tiny", server_from_bootable_volume]
op_server_create = subprocess.check_output(list_check_output)

list_check_output = ['openstack' , 'server' , 'show',  server_from_bootable_volume, "-f", "json"]
op_server_show = subprocess.check_output(list_check_output)
op_server_show = yaml.load(op_server_show)

print "\n\nop_server_show is" , op_server_show
print "\n\nTYPE OF op_server_show" , type(op_server_show)

print "EXTRACTABLE STUFF" , op_server_show['id'], op_server_show['name'], op_server_show['status'] , op_server_show['volumes_attached']

#
#
# print "\n\n================DELETION OF BOOTABLE VOLUME================\n\n"
# o_chdir = os.chdir("/opt/stack/devstack")
# list_checkOutput_delete = ['openstack' ,'volume' ,'delete' ,  volume_name_bootable]
# op = subprocess.check_output(list_checkOutput_delete)
#
# op = latest_volume_status(volume_name_bootable)
#
# # Enter only if the volume exists
# if op != 1:
#     while (op['status'] == 'deleting'):
#         print "\nWAITING FOR VOLUME %s TO BE DELETED. CURRENTLY VOLUME STATE IS IN %s\n" % (op['name'], op['status'])
#         time.sleep(10)
#         op = latest_volume_status(volume_name_bootable)
#         if op == 1:
#             break
#             print "CURRENT STATUS OF VOLUME IS" , op , "HENCE CONTINUING"
#
