import subprocess
import os
from json import loads
from pprint import pprint as pp
import ast
import time
from sys import argv

volume,server = argv
o_chdir = os.chdir("/opt/stack/devstack")
size_vol = "100"
type_vol = 'VMAX_OPTIMIZED'

list_checkOutput = ['openstack' ,'volume' ,'create' , '--size', size_vol , '--type' , type_vol , volume, '-f','json']
op = subprocess.check_output(list_checkOutput)
op = loads(op)


o_chdir = os.chdir("/opt/stack/devstack")
op = subprocess.check_output(['openstack' , 'volume' , 'show', volume , '-f', 'json'])
op = loads(op)

print "op parameters are", op['name'], op['size']


o_chdir = os.chdir("/opt/stack/devstack")
size_vol = "100"
type_vol = 'VMAX_OPTIMIZED'
cmd = 'openstack volume create'
image = 'cirros-0.3.4-x86_64-uec' #Keep a function here to get the value automatically.
flavor = 'm1.tiny'


#openstack server create --image cirros-0.3.4-x86_64-uec --flavor m1.tiny newInstance
list_checkOutput = ['openstack' ,'server' ,'create' , '--image', image , '--flavor' , flavor , server, '-f','json']
#op = subprocess.check_output(['openstack' ,'volume' ,'create' , '--size', size_vol , '--type' , type_vol , volume, '-f','json'])
op = subprocess.check_output(list_checkOutput)
op = loads(op)

print "op is", op

list_checkOutput = ['openstack' ,'server', 'show', server ,'-f', 'json']
op = subprocess.check_output(list_checkOutput)
op = loads(op)

print "op is", op['name'],op['status']

list_checkOutput = ['openstack' , 'server' , 'add' , 'volume' , server, volume]
op = subprocess.check_output(list_checkOutput)
op = loads(op)

print "op is" , op

list_checkOutput = ['openstack' , 'server' , 'add' , 'volume' , server, volume]
op = subprocess.check_output(list_checkOutput)
op = loads(op)

print "op is" , op


op = subprocess.check_output(['openstack' , 'volume' , 'show', volume , '-f', 'json'])
op = loads(op)

print "op parameters are", op['status'], op['size']

