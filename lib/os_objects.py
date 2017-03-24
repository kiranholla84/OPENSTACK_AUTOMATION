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
    def __init__(self, bootable_factor, replication_factor, size_vol, type_vol, volume_name, **kwargs):
        self.bootable_factor = bootable_factor
        self.replication_factor = replication_factor
        self.size_vol = size_vol
        self.type_vol = type_vol
        self.volume_name = volume_name
        self.volume_available_string = 'available'

    def latest_volume_status(self):
        try:
            op = subprocess.check_output(['openstack', 'volume', 'show', self.volume_name, '-f', 'json'])
            op = yaml.load(op)
            return op
        except subprocess.CalledProcessError as e:
            print "\nTHERE IS NO VOLUME WITH THE NAME %s" % (self.volume_name)
            return e.returncode

    def volumes_create(self):

        # ACTION : Remove the full block below
        print "Requested stuff are %s %s %s %s %s " % (
        self.bootable_factor, self.replication_factor, self.size_vol, self.type_vol, self.volume_name)
        os.chdir("/opt/stack/devstack")
        print "Debug : CWD", os.getcwd()
        # auth_perm = ['source', 'openrc', 'admin', 'admin']
        # op_auth_perm = subprocess.check_output(auth_perm)

        # ACTION :Modularize : Below should be modularized
        print "\n================CREATING NON-BOOTABLE VOLUME ================\n"
        list_checkOutput = ['openstack', 'volume', 'create', '--size', str(self.size_vol), '--type', self.type_vol,
                            self.volume_name, '-f', 'json']
        op = subprocess.check_output(list_checkOutput)
        op = loads(op)

        # ACTION : MODULARIZE THIS ACROSS FOR ALL ASYNC ITEMS
        # non-bootable non-attached volume show
        while (op['status'] != 'available'):
            if (op['status'].lower == 'error'):
                print "\nFAILURE IN CREATING VOLUME %s. EXITING" % (op['name'])
                break
            print "\nWAITING FOR STATUS OF THE VOLUME %s TO BE AVAILABLE. CURRENTLY VOLUME STATE IS IN %s\n" % (
            op['name'], op['status'])
            time.sleep(10)
            op = self.latest_volume_status()

        # ACTION : MODULARIZE THIS AS VOLUME CHECK /SERVER CREATION CHECK/VOLUME VALUES CHECK/ SERVER VALUES CHECK
        # check for creation of the volume
        inputs = [self.volume_name, self.size_vol, self.type_vol, self.volume_available_string]
        values = [(op['name']), op['size'], op['type'], op['status']]
        print "VALUES", self.volume_name, self.size_vol, self.type_vol, self.volume_available_string
        print "INPUTS", op['name'], op['size'], op['type'], op['status']
        if values == inputs:
            print "\nVOLUME CREATED SUCCESSFULLY\n"

    def volume_delete(self,volume_name):

        print "\n================DELETION OF NON-BOOTABLE VOLUME================\n"
        o_chdir = os.chdir("/opt/stack/devstack")
        list_checkOutput_delete = ['openstack' ,'volume' ,'delete' ,  volume_name]
        op = subprocess.check_output(list_checkOutput_delete)

        op = latest_volume_status(volume_name)

        # Enter only if the volume exists
        if op != 1:
            while (op['status'] == 'deleting'):
                print "\nWAITING FOR VOLUME %s TO BE DELETED. CURRENTLY VOLUME STATE IS IN %s\n" % (op['name'], op['status'])
                time.sleep(10)
                op = latest_volume_status(volume_name)
                if op == 1:
                    break
                    print "CURRENT STATUS OF VOLUME IS" , op , "HENCE CONTINUING"


class InstanceOperations(object):
    def __init__(self, server_name, image_name, flavour, **kwargs):
        self.image_name = image_name
        self.server_name = server_name
        self.flavour = flavour
        self.server_available_string = 'available'
        self.server_active_string = 'ACTIVE'
        self.no_attach = []
        self.volume_inuse_string = 'in-use'

    # ACTION : Modularize this with VOLUME SHOW
    # function to get the latest status of the server

    def latest_server_status(self):
        try:
            op = subprocess.check_output(['openstack', 'server', 'show', self.server_name, '-f', 'json'])
            op = yaml.load(op)
            return op
        except subprocess.CalledProcessError as e:
            print "\nTHERE IS NO SERVER WITH THE NAME %s" % (self.server_name)
            return e.returncode

    def server_create(self):
        print "\n================CREATION OF EMPTY INSTANCE================\n"
        print "Requested stuff SERVER ARE are %s %s %s" % (self.image_name, self.server_name, self.flavour)
        instanceCreation_subprocess_ob = ['openstack', 'server', 'create', '--image', self.image_name, '--flavor',
                                          self.flavour, self.server_name, '-f', 'json']
        instanceCreated_ob = subprocess.check_output(instanceCreation_subprocess_ob)
        op = loads(instanceCreated_ob)
        self.server_id = op['id']

        # ACTION : MODULARIZE
        print "\n================CHECKING FOR THE CREATION OF INSTANCE================\n"
        o_chdir = os.chdir("/opt/stack/devstack")

        # ACTION : MODULARIZE
        # non-bootable non-attached volume show
        while (op['status'] != 'ACTIVE'):
            if (op['status'].lower == 'error'):
                print "\nFAILURE IN CREATING SERVER %s. EXITING" % (op['name'])
                break
            print "\nWAITING FOR STATUS OF THE SERVER %s TO BE ACTIVE. CURRENTLY STATE IS %s\n" % (
            op['name'], op['status'])
            time.sleep(10)
            op = self.latest_server_status()

        print "#op during server creation is\n", op

        inputs = [self.server_id, self.server_name, self.server_active_string]
        print "\nINPUTS TO CREATE INSTANCE", inputs

        values = [op['id'], op['name'], op['status']]
        print "\nVALUES FROM THE CREATED VOLUME", values

        if values == inputs:
            print "\nINSTANCE CREATED SUCCESSFULLY\n"

    def volume_attach(self, volume_name):
        print "================VOLUME ATTACH================"

        # Action: Modularize
        # check for volume status
        volume_before_attach_subprocess_output_json = subprocess.check_output(['openstack', 'volume', 'show', volume_name, '-f', 'json'])
        volume_before_attach_subprocess_output_yaml = yaml.load(volume_before_attach_subprocess_output_json)

        # volume addition to server or volume attach
        volume_attach_subprocess_input = ['openstack', 'server', 'add', 'volume', self.server_name, volume_name]
        volume_attach_subprocess_output = subprocess.check_output(volume_attach_subprocess_input)

        # Action: Modularize
        # check for addition of volume to server
        volume_attach_subprocess_output_json = subprocess.check_output(['openstack', 'volume', 'show', volume_name, '-f', 'json'])
        volume_attach_subprocess_output_yaml = yaml.load(volume_attach_subprocess_output_json)

       # ACTION : Modularize, combine with volume waiting. Pass the required status , error status as function variables
        while (volume_attach_subprocess_output_yaml['status'] != 'in-use'):
            if (volume_attach_subprocess_output_yaml['status'].lower == 'error'):
                print "\nFAILURE IN CREATING VOLUME %s. EXITING" % (volume_attach_subprocess_output_yaml['name'])
                break
            print "\nWAITING FOR STATUS OF THE VOLUME %s TO BE IN-USE. CURRENTLY VOLUME STATE IS IN %s\n" % (volume_attach_subprocess_output_yaml['name'],volume_attach_subprocess_output_yaml['status'])
            time.sleep(10)
            volume_attach_subprocess_output_json = subprocess.check_output(['openstack', 'volume', 'show', volume_name, '-f', 'json'])
            volume_attach_subprocess_output_yaml = yaml.load(volume_attach_subprocess_output_json)

        print "\n volume_attach_subprocess_output_yaml is", volume_attach_subprocess_output_yaml

        attachment_details_server_id = volume_attach_subprocess_output_yaml['attachments'][0]['server_id']
        attachment_details_attachment_id = volume_attach_subprocess_output_yaml['attachments'][0]['attachment_id']
        attachment_details_volume_id = volume_attach_subprocess_output_yaml['attachments'][0]['volume_id']
        attachment_details_device = volume_attach_subprocess_output_yaml['attachments'][0]['device']

        print "\n attachment details", attachment_details_server_id, attachment_details_attachment_id, attachment_details_volume_id, attachment_details_device

        inputs = [volume_name, self.server_id , volume_before_attach_subprocess_output_yaml['size'], volume_before_attach_subprocess_output_yaml['type'],self.volume_inuse_string ]
        print "\nINPUTS TO CREATE VOLUME", inputs

        values = [(volume_attach_subprocess_output_yaml['name']), attachment_details_server_id, volume_attach_subprocess_output_yaml['size'],
                  volume_attach_subprocess_output_yaml['type'], volume_attach_subprocess_output_yaml['status']]

        print "\nVALUES FROM THE CREATED VOLUME", values

        if values == inputs:
            print "\nVOLUME ATTACHED SUCCESSFULLY\n"

    def volume_detach(self, volume_name):
        print "\n================VOLUME DETACH================\n"
        # volume addition to server or volume attach
        list_check_output = ['openstack' , 'server' , 'remove' , 'volume' , self.server_name, volume_name]
        op_attach_vol = subprocess.check_output(list_check_output)

        # check for addition of volume to server
        op = subprocess.check_output(['openstack' , 'volume' , 'show', volume_name , '-f', 'json'])
        op = yaml.load(op)

        print "op is" , op
        print "\n\n"
        try:
            attachment_details_server_id = op['attachments'][0]['server_id']
            attachment_details_attachment_id = op['attachments'][0]['attachment_id']

            attachment_details_volume_id = op['attachments'][0]['volume_id']
            attachment_details_device = op['attachments'][0]['device']
        except IndexError:
            if op['status'] == 'available':
                print "There does not seem to be any volume attached to server. Yes it is detached!. Now check the status of the volume"
            else :
                print "Some how the status of the volume is not available"

        print "attachment details %s :: %s ::  %s :: %s"  %(attachment_details_server_id, attachment_details_attachment_id,attachment_details_volume_id,attachment_details_device)

    def server_delete(self,server_name):
        print "\n================DELETION OF INSTANCE================\n"
        o_chdir = os.chdir("/opt/stack/devstack")
        instance_delete = ['openstack' ,'server' ,'delete', server_name]
        op = subprocess.check_output(instance_delete)
        op = self.latest_server_status(server_name)

        print "#op during deletion is and task state\n" , op , op['OS-EXT-STS:task_state']

        # Enter only if the instance exists
        if op['status'] == 'ACTIVE':
            while (op['OS-EXT-STS:task_state'] == 'deleting'):
                print "\nWAITING FOR SERVER %s TO BE DELETED. CURRENTLY SERVER STATE IS IN %s\n" % (op['name'], op['OS-EXT-STS:task_state'])
                time.sleep(10)
                op = self.latest_server_status(server_name)
                if op == 1:
                    break
                print "CURRENT STATUS OF SERVER IS" , op , "HENCE CONTINUING"
