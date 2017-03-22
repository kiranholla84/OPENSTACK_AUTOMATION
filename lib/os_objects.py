import subprocess
import os
from json import loads
from json import dumps
from pprint import pprint as pp
import ast
import time
import sys
import re
import yaml

class VolumeOperations(object):
    def __init__(self, bootable_factor, replication_factor, size_vol, type_vol , volume_name, **kwargs):
        self.bootable_factor = bootable_factor
        self.replication_factor = replication_factor
        self.size_vol = size_vol
        self.type_vol = type_vol
        self.volume_name = volume_name

    def latest_volume_status(self):
        try:
            op = subprocess.check_output(['openstack', 'volume', 'show', self.volume_name, '-f', 'json'])
            op = yaml.load(op)
            return op
        except subprocess.CalledProcessError as e:
            print "\nTHERE IS NO VOLUME WITH THE NAME %s" % (self.volume_name)
            return e.returncode

    def volumes_create(self):
        # def __init__(bootable_factor, replication_factor, size):

            print "Requested stuff are %s %s %s %s %s " %(self.bootable_factor,self.replication_factor,self.size_vol , self.type_vol , self.volume_name)
            print "\n================CREATING NON-BOOTABLE VOLUME ================\n"
            os.chdir("/opt/stack/devstack")
            auth_perm = ['source', 'openrc', 'admin', 'admin']
            op_auth_perm = subprocess.check_output(auth_perm)
            list_checkOutput = ['openstack' ,'volume' ,'create' , '--size', str(self.size_vol) , '--type' , self.type_vol , self.volume_name, '-f','json']
            op = subprocess.check_output(list_checkOutput)
            op = loads(op)

            # non-bootable non-attached volume show
            while (op['status'] != 'available'):
                if (op['status'].lower == 'error'):
                    print "\nFAILURE IN CREATING VOLUME %s. EXITING" % (op['name'])
                    break
                print "\nWAITING FOR STATUS OF THE VOLUME %s TO BE AVAILABLE. CURRENTLY VOLUME STATE IS IN %s\n" % (op['name'],op['status'])
                time.sleep(10)
                op = self.latest_volume_status(self.volume_name)

