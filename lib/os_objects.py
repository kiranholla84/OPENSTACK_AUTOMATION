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
        self.available_string = 'available'

    def volume_or_snapshot_status_call(self, type_of_object, name_of_object):

        self.type_of_object = type_of_object
        self.name_of_object = name_of_object

        if self.type_of_object == "volume":
            self.op_state = self.any_volume_status(name_of_object)
        elif self.type_of_object == "snapshot":
            self.op_state = self.any_snapshot_status(name_of_object)

        return self.op_state

    def async_task_wait_process_for_volume_and_snapshot(self, type_of_object , name_of_object, final_async_state):

        # Get the initial volume or snapshot status
        self.op_state = self.volume_or_snapshot_status_call(type_of_object, name_of_object)

        # Now wait for the state of the volume or snapshot to change to "Available"
        while (self.op_state['status'] != final_async_state):

            # Sometimes the status may go to error. If that is the case return the message to the yser
            if (self.op_state['status'].lower == 'error'):
                print "\nFAILURE IN VOLUME/SNAPSHOT %s ASYNC OPERATION. EXITING" % name_of_object
                break
            print "\nWAITING FOR STATUS OF THE VOLUME/SNAPSHOT %s TO BE IN %s STATE..\nCURRENTLY VOLUME STATE IS IN %s STATE\n" % (
                name_of_object, final_async_state, self.op_state['status'])
            time.sleep(10)

            # This is to get the latest status dynamically
            self.op_state = self.volume_or_snapshot_status_call(type_of_object, name_of_object)

        return self.op_state

    def async_task_delete_wait_process_for_volume_and_snapshot(self, type_of_object, name_of_object):

        self.type_of_object = type_of_object
        self.name_of_object = name_of_object

        # Get the initial volume or snapshot status
        self.op_state = self.volume_or_snapshot_status_call(type_of_object, name_of_object)

        # Now wait till the volume is getting deleted
        while (self.op_state['status'] == 'deleting'):
            time.sleep(5)
            print "\nWAITING FOR VOLUME/SNAPSHOT %s TO BE DELETED. CURRENTLY VOLUME STATE IS IN %s\n" % (
                self.op_state['name'], self.op_state['status'])

            # This is the get the latest status dynamically
            self.op_snaps_vol_show = self.async_task_delete_wait_process_for_volume_and_snapshot(type_of_object, name_of_object)

            if self.op_snaps_vol_show == 1:
                print "%s WITH NAME %s SUCCESSFULLY DELETED" % (type_of_object , name_of_object)
                print "%sDEBUG: op_snaps_vol_show is %s" %self.op_snaps_vol_show
                return 0
            else:
                return 1

    def any_snapshot_status(self,snapshot_name):
        try:
            op = subprocess.check_output(['openstack', 'volume', 'snapshot' ,'show', snapshot_name, '-f', 'json'])
            op = yaml.load(op)
            return op
        except subprocess.CalledProcessError as e:
            print "\nTHERE IS NO SNAPSHOT WITH THE NAME %s" % (snapshot_name)
            print "\nERROR CODE" , e.returncode
            return e.returncode

    def any_volume_status(self, volume_name):
        try:
            op = subprocess.check_output(['openstack', 'volume', 'show', volume_name, '-f', 'json'])
            op = yaml.load(op)
            return op
        except subprocess.CalledProcessError as e:
            print "\nTHERE IS NO VOLUME WITH THE NAME %s" % (volume_name)
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
        if (self.bootable_factor == "bootable"):
            print "\n================CREATING BOOTABLE VOLUME ================\n"
            bootable_string = 'true'

            # Get the images dynamically
            list_check_output = ['openstack', 'image', 'list', '-f', 'json']
            op_image_list = subprocess.check_output(list_check_output)
            op_image_list = yaml.load(op_image_list)
            print "\n==>IMAGE WHICH WILL BE USED FOR BOOTABLE VOLUME CREATION IS", op_image_list[0]['Name'], "...\n"
            list_checkOutput = ['openstack', 'volume', 'create', '--image', op_image_list[0]['Name'], '--type',
                                self.type_vol, '--size', str(self.size_vol), self.volume_name, '-f', 'json']
        else:
            bootable_string = 'false'
            print "\n================CREATING NON-BOOTABLE VOLUME ================\n"
            list_checkOutput = ['openstack', 'volume', 'create', '--size', str(self.size_vol), '--type', self.type_vol,
                                self.volume_name, '-f', 'json']

        op = subprocess.check_output(list_checkOutput)
        op = loads(op)

        # ACTION : MODULARIZE THIS ACROSS FOR ALL ASYNC ITEMS
        # non-bootable non-attached volume show
        op = self.async_task_wait_process_for_volume_and_snapshot("volume" , self.volume_name, self.available_string)

        # ACTION : MODULARIZE THIS AS VOLUME CHECK /SERVER CREATION CHECK/VOLUME VALUES CHECK/ SERVER VALUES CHECK
        # check for creation of the volume

        inputs = [self.volume_name, self.size_vol, self.type_vol, self.available_string , bootable_string]
        values = [(op['name']), op['size'], op['type'], op['status'], op['bootable']]

        print "VALUES", self.volume_name, self.size_vol, self.type_vol, self.available_string , bootable_string
        print "INPUTS", op['name'], op['size'], op['type'], op['status'] , op['bootable']

        if values == inputs:
            print "\nVOLUME CREATED SUCCESSFULLY\n"

    def volumes_clone(self, type_of_source , input_snap_or_clone_source , name_of_target):

        self.input_source = input_snap_or_clone_source
        # ACTION : Remove the full block below
        print "Requested stuff are %s %s %s %s %s " % (
            self.bootable_factor, self.replication_factor, self.size_vol, self.type_vol, self.volume_name)
        os.chdir("/opt/stack/devstack")
        print "Debug : CWD", os.getcwd()
        # auth_perm = ['source', 'openrc', 'admin', 'admin']
        # op_auth_perm = subprocess.check_output(auth_perm)

        # ACTION :Modularize : Below should be modularized
        if (type_of_source == "snapshot"):
            print "\n================CREATING VOLUME FROM SNAPSHOT AS THE SOURCE================\n"

            list_checkOutput = ['openstack', 'volume', 'create', '--snapshot', self.input_source, '--type',
                                self.type_vol, name_of_target, '-f', 'json']

            source_status = self.any_snapshot_status()

        else:
            print "\n================CREATING VOLUME FROM ANOTHER VOLUME AS THE SOURCE ================\n"
            list_checkOutput = ['openstack', 'volume', 'create', '--source', self.input_source, '--type', self.type_vol,
                                name_of_target, '-f', 'json']
            source_status = self.any_volume_status(self.input_source)


        op = subprocess.check_output(list_checkOutput)
        op = loads(op)

        # ACTION : MODULARIZE THIS ACROSS FOR ALL ASYNC ITEMS
        # non-bootable non-attached volume show
        op = self.async_task_wait_process_for_volume_and_snapshot("volume", op['name'], self.available_string)

        # ACTION : MODULARIZE THIS AS VOLUME CHECK /SERVER CREATION CHECK/VOLUME VALUES CHECK/ SERVER VALUES CHECK
        # check for creation of the volume
        inputs = [name_of_target, source_status['size'], self.type_vol, self.available_string]
        values = [(op['name']), op['size'], op['type'], op['status']]

        print "VALUES", values
        print "INPUTS", inputs

        if values == inputs:
            print "\nVOLUME CREATED SUCCESSFULLY FROM SOURCE\n"

    def volume_extend(self, volume_name, new_volume_size):

        # print "\n================VOLUME EXTEND================\n"
        print "New size is" , new_volume_size
        list_check_output = ['openstack' , 'volume' , 'set' , '--size' , str(new_volume_size), self.volume_name]
        op_extend_vol = subprocess.check_output(list_check_output)

        ## check for extension of volume
        op = subprocess.check_output(['openstack' , 'volume' , 'show', volume_name , '-f', 'json'])
        op = yaml.load(op)

        op = self.async_task_wait_process_for_volume_and_snapshot("volume", self.volume_name, self.available_string)

        print "NEW EXTENDED SIZE OF VOLUME %s IS %s" %(self.volume_name, op['size'])

        inputs = [self.volume_name, new_volume_size , self.type_vol, self.available_string]
        values = [(op['name']), op['size'], op['type'], op['status']]

        if values == inputs:
            print "\nVOLUME EXTENDED SUCCESSFULLY\n"
        else:
            print "VALUES" ,values
            print "INPUTS", inputs

    def volume_snapshot_create(self,volume_name,number_of_snapshots):

        # print "\n================CREATION OF VOLUME SNAPSHOT================\n"
        snapshot_name = "snapshot" + "_" + volume_name
        self.snapshot_description = "THIS IS THE DESCRIPTION OF SNAPSHOT %s" % (snapshot_name)
        list_check_output = ['openstack' , 'volume' ,'snapshot' ,'create' , "--volume" ,volume_name , "--description", self.snapshot_description , snapshot_name]
        op_snaps_vol_create = subprocess.check_output(list_check_output)
        create_snapshot_operation = self.volume_snapshot_check(snapshot_name)
        print "CREATE SNAPSHOT OPERATION RESULTED IN ", create_snapshot_operation
        return create_snapshot_operation

    def volume_snapshot_delete(self, snapshot_name):

        print "\n================DELETION OF VOLUME SNAPSHOT %s ================\n" % (snapshot_name)
        list_check_output = ['openstack', 'volume', 'snapshot', 'delete', str(snapshot_name), '--force']
        op_snaps_vol_create = subprocess.check_output(list_check_output)
        delete_snapshot_operation = self.volume_snapshot_check(snapshot_name)

        print "DELETE SNAPSHOT OPERATION RESULTED IN " , delete_snapshot_operation

    def volume_snapshot_check(self,snapshot_name):

        # Get the volume status to get all the volume parameters
        volume_status = self.any_volume_status()

        # print "\n================VOLUME SNAPSHOT CREATION CHECK================\n"
        list_check_output = ['openstack' , 'volume' ,'snapshot' ,'show' , snapshot_name , '-f', 'json']
        self.op_snaps_vol_show = subprocess.check_output(list_check_output)
        # print "Type of snap output is before yaml" , type(op_snaps_vol_show)

        self.op_snaps_vol_show = yaml.load(self.op_snaps_vol_show)

        # this code will be entered if the delete is called
        while(self.op_snaps_vol_show['status'] == 'deleting'):
            time.sleep(5)
            print "\nWAITING FOR VOLUME SNAPSHOT %s TO BE DELETED. CURRENTLY VOLUME STATE IS IN %s\n" % (
            self.op_snaps_vol_show['name'], self.op_snaps_vol_show['status'])
            self.op_snaps_vol_show = self.any_snapshot_status(snapshot_name)
            if self.op_snaps_vol_show == 1:
                print "op_snaps_vol_show IS", self.op_snaps_vol_show
                print "SNAPSHOT %s OF VOLUME %s SUCCESSFULLY DELETED" %(snapshot_name, volume_status['name'])
                break

        # this will be entered when create is called
        if self.op_snaps_vol_show == 1:
            # Do nothing as the above variable belongs to delete call
            pass
        else:
            while(self.op_snaps_vol_show['status'] != 'available'):
                print "\nWAITING FOR VOLUME SNAPSHOT %s TO BE AVAILABLE. CURRENTLY VOLUME STATE IS IN %s\n" % (self.op_snaps_vol_show['name'], self.op_snaps_vol_show['status'])
                time.sleep(10)
                self.op_snaps_vol_show = self.any_snapshot_status(snapshot_name)

            inputs = [volume_status['id'] , snapshot_name, self.available_string , self.size_vol, self.snapshot_description]
            values = [self.op_snaps_vol_show['volume_id'],self.op_snaps_vol_show['name'], self.op_snaps_vol_show['status'], self.op_snaps_vol_show['size'], self.op_snaps_vol_show['description']]

            # ACTION REQUIRED : THIS CAN BE MODULARIZED
            if values == inputs:
                print "\nVOLUME SNAPSHOTTED SUCCESSFULLY\n"
                return snapshot_name
            else:
                print "VALUES", values
                print "INPUTS", inputs

    def volume_delete(self,volume_name):

        print "\n================DELETION OF VOLUME================\n"
        o_chdir = os.chdir("/opt/stack/devstack")
        list_checkOutput_delete = ['openstack' ,'volume' ,'delete' ,  volume_name]
        op = subprocess.check_output(list_checkOutput_delete)

        op_status = self.async_task_delete_wait_process_for_volume_and_snapshot("volume", volume_name)

        # Enter only if the volume exists
        if op_status == 0:
            print "\nVOLUME %s SUCCESSFULLY DELETED" %volume_name
        else:
            print "\nVOLUME %s COULD NOT BE DELETED" %volume_name
            return 1

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
                                          self.flavour, self.server_name, '--nic', 'net-id=' , 'private']
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

        # check for detach of volume to server
        volume_detach_subprocess_output_yaml = subprocess.check_output(['openstack' , 'volume' , 'show', volume_name , '-f', 'json'])
        volume_detach_subprocess_output_yaml = yaml.load(volume_detach_subprocess_output_yaml)

        # ACTION : Modularize, combine with volume waiting. Pass the required status , error status as function variables
        while (volume_detach_subprocess_output_yaml['status'] != 'available'):
            if (volume_detach_subprocess_output_yaml['status'].lower == 'error'):
                print "\nFAILURE IN DETACHING VOLUME %s. EXITING" % (volume_detach_subprocess_output_yaml['name'])
                break
            print "\nWAITING FOR STATUS OF THE VOLUME %s TO BE AVAILABLE. CURRENTLY VOLUME STATE IS IN %s\n" % (
            volume_detach_subprocess_output_yaml['name'], volume_detach_subprocess_output_yaml['status'])
            time.sleep(10)
            volume_detach_subprocess_output_yaml = subprocess.check_output(['openstack', 'volume', 'show', volume_name, '-f', 'json'])
            volume_detach_subprocess_output_yaml = yaml.load(volume_detach_subprocess_output_yaml)

        print "volume_detach_subprocess_output_yaml is" , volume_detach_subprocess_output_yaml
        print "\n\n"
        try:
            attachment_details_server_id = volume_detach_subprocess_output_yaml['attachments'][0]['server_id']
            attachment_details_attachment_id = volume_detach_subprocess_output_yaml['attachments'][0]['attachment_id']

            attachment_details_volume_id = volume_detach_subprocess_output_yaml['attachments'][0]['volume_id']
            attachment_details_device = volume_detach_subprocess_output_yaml['attachments'][0]['device']
        except IndexError:
            if volume_detach_subprocess_output_yaml['status'] == 'available':
                print "There does not seem to be any volume attached to server. Yes it is detached!. Now check the status of the volume"
            else :
                print "Some how the status of the volume is not available"

    def server_delete(self,server_name):
        print "\n================DELETION OF INSTANCE================\n"
        o_chdir = os.chdir("/opt/stack/devstack")
        instance_delete = ['openstack' ,'server' ,'delete', server_name]
        op = subprocess.check_output(instance_delete)
        op = self.latest_server_status()

        print "#op during deletion is and task state\n" , op , op['OS-EXT-STS:task_state']

        # Enter only if the instance exists
        if op['status'] == 'ACTIVE':
            while (op['OS-EXT-STS:task_state'] == 'deleting'):
                print "\nWAITING FOR SERVER %s TO BE DELETED. CURRENTLY SERVER STATE IS IN %s\n" % (op['name'], op['OS-EXT-STS:task_state'])
                time.sleep(10)
                op = self.latest_server_status()
                if op == 1:
                    break
                print "CURRENT STATUS OF SERVER IS" , op , "HENCE CONTINUING"
