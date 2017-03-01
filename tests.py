import subprocess
import os
from json import loads
from json import dumps
import yaml
from pprint import pprint as pp
import ast
import time
import sys

# This will be the inputs
volume_name = sys.argv[1]
server_name = sys.argv[2]

# functions
# function to get the latest status of the volume
def latest_volume_status():
    op = subprocess.check_output(['openstack', 'volume', 'show', volume_name, '-f', 'json'])
    op = yaml.load(op)
    return op

# variable initilization
print "volume & server" , volume_name , server_name
o_chdir = os.chdir("/opt/stack/devstack")
size_vol = 1
type_vol = 'VMAX_SILVER'
image = 'cirros-0.3.4-x86_64-uec' #Keep a function here to get the value automatically.
flavor = 'm1.tiny'
no_attach = []
replication_status = None
volume_available_string = 'available'
#
# non-bootable Volume creation
print "\n\n\n================NON-BOOTABLE VOLUME CREATION================\n\n\n"
list_checkOutput = ['openstack' ,'volume' ,'create' , '--size', str(size_vol) , '--type' , type_vol , volume_name, '-f','json']
op = subprocess.check_output(list_checkOutput)
op = loads(op)

# non-bootable non-attached volume show
volume_show_Expected_Keys = ["attachments","replication_status","size","user_id","type","status","description","source_volid","consistencygroup_id","name","bootable"]
volume_show_Expected_Values = ["[]","enabled","enabled",size_vol,"",type_vol,"available","","","",volume_name,"false"]

while (op['status'] != 'available'):
    print "\nWAITING FOR STATUS OF THE VOLUME %s TO BE AVAILABLE. CURRENTLY VOLUME STATE IS IN %s\n" % (op['name'],op['status'])
    time.sleep(10)
    op = latest_volume_status()

print "\n\n\n================NON-BOOTABLE VOLUME CHECK================\n\n\n"
o_chdir = os.chdir("/opt/stack/devstack")
# op = subprocess.check_output(['openstack' , 'volume' , 'show', volume_name , '-f', 'json'])
# op = yaml.load(op)
# print "op is" , op
# print "op status", op['status']


values = [(op['name']),op['size'],op['type'],op['attachments'],op['replication_status'],op['status']]
print "VALUES", values

inputs = [volume_name,size_vol,type_vol,no_attach,replication_status,volume_available_string]
print "INPUTS" , inputs

if values == inputs :
    print "\nVOLUME CREATED SUCCESSFULLY\n"



#
# # Instance creation
# #openstack server create --image cirros-0.3.4-x86_64-uec --flavor m1.tiny newInstance
# list_checkOutput = ['openstack' ,'server' ,'create' , '--image', image , '--flavor' , flavor , server, '-f','json']
# #op = subprocess.check_output(['openstack' ,'volume' ,'create' , '--size', size_vol , '--type' , type_vol , volume, '-f','json'])
# op = subprocess.check_output(list_checkOutput)
# op = loads(op)
#
# # instance check
# print "op is", op
# list_checkOutput = ['openstack' ,'server', 'show', server ,'-f', 'json']
# op = subprocess.check_output(list_checkOutput)
# op = loads(op)
# print "op is", op['name'],op['status']
#
# # volume addition to server or volume attach
# list_checkOutput = ['openstack' , 'server' , 'add' , 'volume' , server, volume]
# op = subprocess.check_output(list_checkOutput)
# op = loads(op)
#
# print "op is" , op
#
# # check for addition of volume to server
# op = subprocess.check_output(['openstack' , 'volume' , 'show', volume , '-f', 'json'])
# op = loads(op)
#
# print "op parameters are", op['status'], op['size']
#
