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
from random import randint
import random

class VolumeOperations(object):
    bootable_true_string = 'true'
    bootable_false_string = 'false'
    # Define the init with default arguments. Mostly
    def __init__(self, bootable_factor = 'nonbootable', size_vol = 1, type_vol = 'VMAX_DIAMOND', volumes_name_prefix = 'test_qe', replication_factor=None, number_of_volumes=5):
        self.bootable_factor = bootable_factor
        self.replication_type = replication_factor
        self.size_vol = size_vol
        self.type_vol = type_vol
        self.volumes_name_prefix = volumes_name_prefix
        self.available_string = 'available'
        self.number_of_volumes = number_of_volumes

        # Initialize
        self.list_checkOutput = dict()
        self.op = []
        self.volumes_name = []
        self.type_vol = []
        self.size_vol = []
        self.volume_details_input_list = []
        self.final_volumes_array_objects = []
        self.volumes_array_objects = []
        self.volumes_check_array_objects = []

    def volumes_or_snapshot_status_call(self, type_of_object, name_of_object):

        self.type_of_object = type_of_object
        self.name_of_object = name_of_object

        try:
            if self.type_of_object == "volume":
                op = subprocess.check_output(['openstack', 'volume', 'show', self.name_of_object, '-f', 'json'])
            elif self.type_of_object == "snapshot":
                op = subprocess.check_output(['openstack', 'snapshot', 'show', self.name_of_object['name'], '-f',
                                               'json'])

            else:
                print "INVALID OBJECT TYPE, EXITING"

            self.op = yaml.load(op)
            return self.op

        except subprocess.CalledProcessError as e:
            print "\nTHERE IS NO %s WITH THE NAME %s" % (self.type_of_object, self.name_of_object['name'])
            print "\nERROR CODE", e.returncode
            return e.returncode

    def volumes_type_return(self, replication_type = 'non-replicated'):
        # Command to list all volume types
        self.list_checkOutput = ['openstack', 'volume', 'type', 'list', '-f', 'json']
        self.op = subprocess.check_output(self.list_checkOutput)
        self.op = loads(self.op)
        self.new_list = []
        self.split_list = {}
        self.replication_type = replication_type
        self.replication_list = []
        self.non_replication_list = []

        for self.value in self.op:
            self.value_got = self.value['Name']
            self.new_list.append(self.value_got)

        print "\nHERE ARE THE VOLUME TYPES AVAILABLE", self.new_list

        for self.volumes_type_in_new_list in self.new_list:
            self.show_check_output = ['openstack', 'volume', 'type', 'show', self.volumes_type_in_new_list, '-f', 'json']
            self.op_snaps_vol_show = subprocess.check_output(self.show_check_output)
            self.op1 = yaml.load(self.op_snaps_vol_show)
            # print "%s" % self.op1['properties']

            # The output of the volume show command contains properties which show if the volume type is replicated or not. Sadly it is in text format
            # So regular expression matching is needed
            self.pattern = "replication_enabled='<is> True'"
            self.input_string = self.op1['properties']
            # print "DEBUG: pattern is", self.pattern
            # print "DEBUG: string is", self.input_string
            # print "DEBUG: volume type is", self.volumes_type_in_new_list

            self.match_pattern = re.search(self.pattern, self.input_string, re.I)
            if self.match_pattern:
                self.replication_list.append(self.volumes_type_in_new_list)
            else:
                self.non_replication_list.append(self.volumes_type_in_new_list)

        if replication_type == 'replicated':
            print "DEBUG:%s" % random.choice(self.replication_list)
            return random.choice(self.replication_list)
        else:
            # print "\nDEBUG : RETURNING VOLUME TYPE:%s" %random.choice(self.non_replication_list)
            return random.choice(self.non_replication_list)

    def async_task_wait_process(self, type_of_object, name_of_object, final_async_state):

        self.type_of_object = type_of_object
        self.name_of_object = name_of_object
        self.final_async_state = final_async_state

        print "DEBUG : name_of_object type_of_object final_async_state %s %s %s" \
              %(name_of_object, type_of_object, final_async_state)

        # Get the initial volume or snapshot status
        self.op_state = self.volumes_or_snapshot_status_call(str.lower(self.type_of_object), self.name_of_object)

        # Check if the volume is already deleted OR does not exist
        if self.op_state == 1:
            print "%s WITH NAME %s SUCCESSFULLY DELETED/DOES NOT EXIST" % (self.type_of_object, self.name_of_object)
            return 0

        # This is if the state is already as per the final intended state
        if (self.op_state['status'] == self.final_async_state):
            print "\nSTATUS OF THE %s IS ALREADY %s STATE" %(self.type_of_object,self.final_async_state)
            return self.op_state
        else:
            # Now wait for the state of the volume or snapshot to change to "Available"
            while (self.op_state['status'] != self.final_async_state):

                # Sometimes the status may go to error. If that is the case return the message to the yser
                if self.op_state['status'].lower == 'error' or self.op_state['status'].lower == 'error_deleting':
                    print "\nFAILURE IN VOLUME/SNAPSHOT %s ASYNC OPERATION. EXITING" % self.name_of_object
                    break
                elif (self.op_state['status'].lower == 'deleting'):
                    print "\nWAITING FOR VOLUME/SNAPSHOT %s TO BE DELETED. CURRENTLY VOLUME/SNAPSHOT STATE IS IN %s\n" \
                          % (self.op_state['name'], self.op_state['status'])
                else:
                    # This is for extending, attaching, snapshot creation
                    print "\nWAITING FOR STATUS OF THE VOLUME/SNAPSHOT %s TO BE IN %s STATE..\nCURRENTLY VOLUME/SNAPSHOT " \
                          "STATE IS IN %s STATE\n" % (
                    self.name_of_object, self.final_async_state, self.op_state['status'])

                time.sleep(15)

                # This is to get the latest status dynamically from CLI
                self.op_state = self.volumes_or_snapshot_status_call(str.lower(self.type_of_object),
                                                                     self.name_of_object)

                # This will be entered if delete volume is the async operation
                if self.op_state == 1:
                    print "%s WITH NAME %s SUCCESSFULLY DELETED" % (self.type_of_object, self.name_of_object)
                    return 0
                # This is for the remaining states
                elif self.op_state['status'] == self.final_async_state:
                    print "\nSTATUS OF THE %s %s NOW IS IN %s STATE..\n" % (self.type_of_object, self.name_of_object,
                                                                            self.op_state['status'])
                    return self.op_state
                else:
                    pass

    def dynamic_image_get(self):

        # Get the first image dynamically
        list_check_output = ['openstack', 'image', 'list', '-f', 'json']
        op_image_list = subprocess.check_output(list_check_output)
        op_image_list = yaml.load(op_image_list)
        return op_image_list[0]['Name']

    def select_volumes_size(self):

        # If volume size is not given at the time of calling the class then select random number between 100 to 200GB
        self.val =  randint(20, 25)
        # print "DEBUG: RETURNING SIZE %s" %self.val
        return self.val

    def volumes_create(self):

        # Execute creation of all volumes in parallel. This is not a multi-threaded way of calling though
        for self.volumes_index in range(0, self.number_of_volumes):

            # Create a dictionary of values for each input volume  having common volume properties
            self.volume_details = {'name': self.volumes_name_prefix + str(self.volumes_index),
                                   'size': self.select_volumes_size() ,'volume_type' : self.volumes_type_return(),
                                   'bootable_factor': self.bootable_factor}

            # Append the latest volume name dictionary entry to the volume name list. This  list of dictionaries
            # will be used later for comparison
            self.volume_details_input_list.append(self.volume_details)

            print "\n================CREATING %s VOLUME %s ================\n" \
            % (self.volume_details_input_list[self.volumes_index]['bootable_factor'],
            (self.volume_details_input_list[self.volumes_index]['name']))

            # This is only to input to the command below , or else the command would look too long!
            self.input_volume_name = self.volume_details_input_list[self.volumes_index]['name']
            self.input_volume_size = self.volume_details_input_list[self.volumes_index]['size']
            self.input_volume_type = self.volume_details_input_list[self.volumes_index]['volume_type']

            print "DEBUG1 %s %s %s " % (self.input_volume_name, self.input_volume_size, self.input_volume_type)

            # Check for bootable volumes as command is different.
            if (self.bootable_factor == "bootable"):

                # Get the OS image dynamically from CLI
                self.os_image = self.dynamic_image_get()
                print "\n==>IMAGE WHICH WILL BE USED FOR BOOTABLE VOLUME CREATION IS", self.os_image, "...\n"

                # Set this class variable as it will be same across instances
                VolumeOperations.bootable_string = VolumeOperations.bootable_true_string

                # Volume Create Command to be input
                self.list_checkOutput[self.volumes_index] = ['openstack', 'volume', 'create', '--image',
                                                             self.os_image, '--type', self.input_volume_type ,
                                                             '--size', str(self.input_volume_size),
                                                             self.input_volume_name, '-f', 'json']
            else:
                # Set this class variable as it will be same across instances
                VolumeOperations.bootable_string = VolumeOperations.bootable_false_string

                # Volume Create Command to be input
                self.list_checkOutput[self.volumes_index]= ['openstack', 'volume', 'create', '--size',
                                                            str(self.input_volume_size), '--type',
                                                            self.input_volume_type, self.input_volume_name,
                                                            '-f', 'json']

            # Set the bootable string in the input volume list to True or False
            self.volume_details['bootable_factor'] = VolumeOperations.bootable_string

            # Execute the Openstack CLI Command which creates volume
            self.temp = subprocess.check_output(self.list_checkOutput[self.volumes_index])
            self.temp2 = loads(self.temp)
            self.op.append(self.temp2)

        # Check the volume creation one by one
        for self.volumes_index in range(0, self.number_of_volumes):

            self.comparison_check_parameter = self.volumes_check(self.volume_details_input_list, self.volumes_index, 'create')

            # the tuple returned has the volume object in the first
            self.final_volumes_array_objects.append(self.comparison_check_parameter[0])

            # Check for volume creation
            if self.comparison_check_parameter[1] == 0:
                print "VOLUME %s SUCCESSFULLY CREATED" % (self.volume_details_input_list[self.volumes_index]['name'])
            else:
                print "VOLUME NOT CREATED"

        print "\nDEBUG: FINAL VOLUME ARRAY IS %s" %self.final_volumes_array_objects

        # Clear out the array self.volumes_check_array_objects used in volumes_check
        self.volumes_check_array_objects = []

        return self.final_volumes_array_objects

    def volumes_check(self, user_input_list, index_of_list, type_of_operation, final_state_of_volume='available', *args):

        # self.volumes_check(self.volume_extend_list, self.volumes_index, "extend", "available", self.extension_factor)

        self.volume_details_input_list = user_input_list
        self.volumes_index = index_of_list
        self.type_of_operation = type_of_operation
        self.final_state_of_volume = final_state_of_volume

        # Wait due to async operation. Wait for the particular volume to be in available state
        # This array will affect create, clone, extend etc.
        # So after the particular operation, this list should be cleared!
        self.volumes_check_array_objects.append(self.async_task_wait_process("volume",
                                          self.volume_details_input_list[self.volumes_index]['name'],
                                          self.final_state_of_volume))

        if self.type_of_operation == 'create':

            print "DEBUG1: volume_details_input_list %s"  %self.volume_details_input_list
            print "DEBUG2: volumes_check_array_objects %s" % self.volumes_check_array_objects
            print "DEBUG3 : Index %s" %self.volumes_index
            print "DEBUG4 : %s" %(self.volumes_check_array_objects[self.volumes_index])

            self.inputs = [self.volume_details_input_list[self.volumes_index]['name'],
                           self.volume_details_input_list[self.volumes_index]['size'],
                           self.volume_details_input_list[self.volumes_index]['volume_type'],
                           self.volume_details_input_list[self.volumes_index]['bootable_factor']]

            # Outputs are from the object details of the newly created volume. Both will be compared
            self.values = [self.volumes_check_array_objects[self.volumes_index]['name'],
                           self.volumes_check_array_objects[self.volumes_index]['size'],
                           self.volumes_check_array_objects[self.volumes_index]['type'],
                           self.volumes_check_array_objects[self.volumes_index]['bootable']]

        # Clone
        if (self.type_of_operation == 'clone'):
            self.inputs = [self.name_of_target, self.source_status['size'], self.type_vol, self.available_string]
            self.values = [(object_value['name']), object_value['size'], object_value['type'], object_value['status']]

        # extend
        if (self.type_of_operation == 'extend'):
            self.extension_factor = args[0]
            print "DEBUG1: volume_details_input_list %s" % self.volume_details_input_list
            print "DEBUG2: volumes_check_array_objects %s" % self.volumes_check_array_objects
            print "DEBUG3 : Index , extension factor %s %s" % (self.volumes_index , self.extension_factor)
            print "DEBUG4 : %s" % (self.volumes_check_array_objects[self.volumes_index])

            self.intended_extended_size = (self.volume_details_input_list[self.volumes_index]['size'] + self.extension_factor)
            print "DEBUG4 : is %s" %self.intended_extended_size
            self.inputs = [self.volume_details_input_list[self.volumes_index]['name'] , self.intended_extended_size]
            self.values = [self.volumes_check_array_objects[self.volumes_index]['name'],
                           self.volumes_check_array_objects[self.volumes_index]['size']]

        # delete
        if(self.type_of_operation == 'delete'):
            if self.volumes_check_array_objects[self.volumes_index] == 0:
                return 0

        if self.values == self.inputs:
            print "\nVOLUME CHECK COMPLETED SUCCESSFULLY\n"

            # Return only the array pertaining to the volume index. Later it will be appended
            return (self.volumes_check_array_objects[self.volumes_index],0)
        else:
            print "\nVOLUME CHECK FAILED\n"
            print "DEBUG: INPUTS", self.inputs
            print "DEBUG: VALUES", self.values
            return 1

    def volumes_clone(self, type_of_source , input_snap_or_clone_source , name_of_target):

        self.type_of_source = type_of_source
        self.input_source = input_snap_or_clone_source
        self.name_of_target = name_of_target


        # Modularize
        if (self.type_of_source == "snapshot"):
            print "\n================CREATING VOLUME FROM SNAPSHOT AS THE SOURCE================\n"

            list_checkOutput = ['openstack', 'volume', 'create', '--snapshot', self.input_source, '--type',
                                self.type_vol, name_of_target, '-f', 'json']

            self.source_status = self.any_snapshot_status()

        else:
            # Modularize
            print "\n================CREATING VOLUME FROM ANOTHER VOLUME AS THE SOURCE ================\n"
            list_checkOutput = ['openstack', 'volume', 'create', '--source', self.input_source, '--type', self.type_vol,
                                name_of_target, '-f', 'json']
            self.source_status = self.any_volumes_status(self.input_source)

        # Execute the Openstack CLI Command
        op = subprocess.check_output(list_checkOutput)
        op = loads(op)

        # WAIT FOR ASYNC OPERATION TO COMPLETE
        op = self.async_task_wait_process("volume", op['name'], self.available_string)

        # Check for the volume creation
        self.comparison_check_parameter = self.volumes_check(self.op)
        if self.comparison_check_parameter == 0:
            print "\n%s %s SUCCESSFULLY CLONED TO NEW VOLUME %s" %(self.type_of_source, self.input_source ,self.name_of_target)
        else:
            print "\n%s %s VOLUME %s NOT CLONED" %(self.type_of_source, self.input_source)

    def volumes_extend(self, volume_extend_list , extension_factor = 100):

        self.volume_extend_list = volume_extend_list
        self.length_volumes_array = len(self.volume_extend_list)

        self.extension_factor = extension_factor
        self.extended_volumes_details = list()
        self.extended_volumes_object_index_dict = dict()
        self.comparison_check_parameter_extend = []
        self.final_extended_volumes_array_objects = []

        print "\nDEBUG: LENGTH OF THE VOLUME ARRAY %s" %self.length_volumes_array

        for self.volumes_index in range(0, self.length_volumes_array):

            # print "\n================VOLUME EXTEND================\n"
            self.intended_extended_size = (self.volume_extend_list[self.volumes_index])['size']  + self.extension_factor

            self.list_check_output = ['openstack' , 'volume' , 'set' , '--size' , str(self.intended_extended_size),
                                      self.volume_extend_list[self.volumes_index]['name']]
            self.op = subprocess.check_output(self.list_check_output)

            self.comparison_check_parameter_extend = self.volumes_check(self.volume_extend_list, self.volumes_index,
                                                                        "extend", "available", self.extension_factor)


            # the tuple returned has the volume object in the first
            self.final_extended_volumes_array_objects.append(self.comparison_check_parameter_extend[0])

            print "NEW EXTENDED SIZE OF VOLUME %s IS %s" \
                  %(self.final_extended_volumes_array_objects[self.volumes_index]['name'],
                    self.final_extended_volumes_array_objects[self.volumes_index]['size'])

            # Check for the return value in the tuple
            if self.comparison_check_parameter_extend[1] == 0:
                print "VOLUME %s SUCCESSFULLY EXTENDED" \
                      % (self.final_extended_volumes_array_objects[self.volumes_index]['name'])
            else:
                print "VOLUME NOT EXTENDED"

        print "\nDEBUG: FINAL EXTENDED VOLUME ARRAY IS %s" % self.final_extended_volumes_array_objects

    def volumes_delete(self, volume_delete_list):

        self.volume_delete_list = volume_delete_list
        self.length_volumes_array = len(self.volume_delete_list)
        self.delete_number = 0

        print "DEBUG1: Type of volume list" , type(volume_delete_list)
        print "DEBUG2 : volume list" , self.volume_delete_list

        for self.volumes_index in range(0, self.length_volumes_array):

            print "DEBUG3 : %s" % self.volume_delete_list[self.volumes_index]
            print "DEBUG4 : %s" % self.volumes_index

            print "\n==========DELETION OF VOLUME %s==========\n" % (self.volume_delete_list[self.volumes_index])['name']

            self.list_checkOutput_delete = ['openstack' ,'volume' ,'delete' , (self.volume_delete_list[self.volumes_index])['name']]
            self.op = subprocess.check_output(self.list_checkOutput_delete)

            self.op_status = self.volumes_check(self.volume_delete_list, self.volumes_index , "delete", "NA")

            # Enter only if the volume exists
            if self.op_status == 0:
                print "\nVOLUME %s SUCCESSFULLY DELETED" %(self.volume_delete_list[self.volumes_index])['name']
                self.delete_number = self.delete_number + 1
            else:
                print "\nVOLUME %s COULD NOT BE DELETED" %(self.volume_delete_list[self.volumes_index])['name']

        return self.delete_number

class SnapshotOperations(object):
        def __init__(self):
            self.VolumeOperationsClass = VolumeOperations()
            self.available_string = "available"

        def snapshots_check(self, snapshot_names_object_list, volume_names_object_list, type_of_operation="create"):

            self.snapshot_names = snapshot_names_object_list
            self.volume_names = volume_names_object_list
            self.type_of_operation = type_of_operation

            if self.type_of_operation == "create":
                self.final_async_state = "available"
            else:
                self.final_async_state = "NR"

            # print "\n================VOLUME SNAPSHOT CREATION CHECK================\n"
            # Use the composition concept here, call the function async_task_wait_process within
            # VolumeOperations class
            self.snapshot_state_check = self.VolumeOperationsClass.async_task_wait_process("SNAPSHOT",
                                                                                           self.snapshot_names,
                                                                                      self.final_async_state)

            # else part will be entered when create is called, this is for delete call
            if self.snapshot_state_check == 0:
                # Do nothing as the above variable belongs to delete call
                print "DEBUG: DELETE SUCCESSFUL"
                return 0
            else:
                self.values = [ self.snapshot_state_check['name'],
                               self.snapshot_state_check['status'],
                               self.snapshot_state_check['size'],
                                self.snapshot_state_check['volume_id'],
                               self.snapshot_state_check['description']]
                self.inputs = [self.snapshot_names['name'],
                               self.available_string,
                               self.volume_names['size'],
                               self.volume_names['id'],
                               self.snapshot_names['snapshot_description']]

            # Compare the inputs to the created snapshot
            if self.values == self.inputs:
                print "\nVOLUME %s SNAPSHOTTED SUCCESSFULLY" %self.volume_names['name']
                return self.snapshot_state_check
            else:
                print "\nFAILED IN SNAPSHOT CHECK"
                print "\nVALUES", self.values
                print "\nINPUTS", self.inputs
                return 1

        def snapshots_create(self, volume_list_for_snapshots, number_of_snapshot_per_volume = 2):

            self.volume_list_for_snapshots = volume_list_for_snapshots
            self.length_volumes_array = len(self.volume_list_for_snapshots)
            self.snapshot_name_prefix = 'snapshot_'
            self.number_of_snapshot_per_volume = number_of_snapshot_per_volume
            self.list_of_snapshots_for_volume = []
            self.snap_details_input_list = []
            self.created_snapshots_list_for_one_volume_per_volume_index = []
            self.created_snapshots_list_for_all_volumes_per_volume_index = []
            self.volume_snapshot_mapping_dict = dict()


            # Creating list of lists, each inner list having dictionaries of snapshot infromation
            for self.volumes_index in range(0, self.length_volumes_array):

                for self.snap_index in range(0, self.number_of_snapshot_per_volume):

                    # Create a dictionary of values for each input snapshot  having common properties but
                    # different values
                    self.snap_details = {'name': self.snapshot_name_prefix +
                                                   self.volume_list_for_snapshots[self.volumes_index]['name'] + "_" +
                                                   str(self.snap_index),
                                           'source_volume_name': self.volume_list_for_snapshots[self.volumes_index]
                                           ['name'],
                                           'snapshot_description': "THIS IS SNAPSHOT %s"
                                                                   %(self.snapshot_name_prefix +
                                                                     self.volume_list_for_snapshots[self.volumes_index]
                                                                     ['name'] +
                                                                     str(self.snap_index)),
                                           }
                    print "DEBUG1 : snap_Details %s" %self.snap_details

                    # Creating list of lists here - the inner list will be for snapshots for a single volume,
                    self.snap_details_input_list.append(self.snap_details)

                # Appending inner list to outer list for list of lists
                self.list_of_snapshots_for_volume.append(self.snap_details_input_list)

                # Inner list needs to be initialized for every new volume as it holds snapshot dictionaries of every new
                # volume
                self.snap_details_input_list = []

            print "DEBUG2 :list_of_snapshots_for_volume is %s" %self.list_of_snapshots_for_volume


            for self.volumes_index in range(0, self.length_volumes_array):
                for self.snap_index in range(0, self.number_of_snapshot_per_volume):
                    print "DEBUG3 : %s %s" %(self.volumes_index , self.snap_index)
                    print "\n================CREATING SNAPSHOT WITH NAME %s FOR VOLUME %s ================\n" \
                          %(self.list_of_snapshots_for_volume[self.volumes_index][self.snap_index]['name'],
                            self.volume_list_for_snapshots[self.volumes_index]['name'])

                    # Snapshot command [First one is for Newton release
                    self.list_check_output_snap_create = ['openstack','snapshot', 'create', '--name',
                                                          (self.list_of_snapshots_for_volume[self.volumes_index]
                                                           [self.snap_index]['name']),
                                                          '--description',
                                                          self.list_of_snapshots_for_volume[self.volumes_index]
                                                          [self.snap_index]['snapshot_description'], '--force',
                                                          self.volume_list_for_snapshots[self.volumes_index]['name']
                                                          ]
                    # this is for Ocata release
                    # self.list_check_output_snap_create = ['openstack', 'volume', 'snapshot', 'create', "--volume",
                    #                      self.volume_list_for_snapshots[self.volumes_index]['name'], "--description",
                    #                      self.list_of_snapshots_for_volume[self.volumes_index][self.snap_index]
                    #                                       ['snapshot_description'],
                    #                      self.list_of_snapshots_for_volume[self.volumes_index][self.snap_index]['name'],
                    #                                       '--force' ]

                    self.snap_create = subprocess.check_output(self.list_check_output_snap_create)

            # This whole code is to check if snapshot creation happened
            for self.volumes_index in range(0, self.length_volumes_array):
                for self.snap_index in range(0, self.number_of_snapshot_per_volume):
                    # Sending the snapshot object & volume object for checking if snapshot is created
                    self.create_snapshot_operation = self.snapshots_check\
                        (self.list_of_snapshots_for_volume[self.volumes_index][self.snap_index],
                        (self.volume_list_for_snapshots[self.volumes_index]))

                    self.created_snapshots_list_for_one_volume_per_volume_index.append(self.create_snapshot_operation)
                    print "CREATE SNAPSHOT OPERATION FOR SNAPSHOT %s RESULTED IN %s" %(self.list_of_snapshots_for_volume[self.volumes_index][self.snap_index]['name'], self.created_snapshots_list_for_one_volume_per_volume_index)

                # Is this required? If not , remove this. This contains snapshots of each volume bunched together
                self.created_snapshots_list_for_all_volumes_per_volume_index.append(self.created_snapshots_list_for_one_volume_per_volume_index)

                # Create a dictionary mapping each volume object to its list of snapshots
                self.volume_snapshot_mapping_dict[(self.volume_list_for_snapshots[self.volumes_index])['name']] = self.created_snapshots_list_for_one_volume_per_volume_index
                self.created_snapshots_list_for_one_volume_per_volume_index = []

            # print the list of volume:snapshot pairs
            for volumes,snapshots in self.volume_snapshot_mapping_dict.iteritems():
                print "\nVOLUME %s" %volumes
                print "\nSNAPSHOTS %s" %snapshots

            return self.volume_snapshot_mapping_dict

        def snapshots_delete(self, volume_list_for_snapshots, volume_snapshot_names_dict, number_of_snapshot_per_volume = 2):

            self.number_of_snapshot_per_volume = number_of_snapshot_per_volume
            self.volume_snapshot_names_dict = volume_snapshot_names_dict

            for self.volumes_delete, self.snapshots_to_be_deleted in self.volume_snapshot_mapping_dict.iteritems():
                for self.snap_index in range(0, self.number_of_snapshot_per_volume):
                    print "\n================DELETING SNAPSHOT WITH NAME %s FOR VOLUME %s ================\n" \
                          %(self.snapshots_to_be_deleted[self.snap_index]['name'], self.volumes_delete)

                    self.list_check_output_delete = ['openstack', 'snapshot', 'delete',
                                                     self.snapshots_to_be_deleted[self.snap_index]['name']]

                    self.op_snaps_vol_delete = subprocess.check_output(self.list_check_output_delete)

            for self.volumes_delete, self.snapshots_to_be_deleted in self.volume_snapshot_mapping_dict.iteritems():
                for self.snap_index in range(0, self.number_of_snapshot_per_volume):
                    self.delete_snapshot_operation = self.snapshots_check \
                        (self.snapshots_to_be_deleted[self.snap_index], self.volumes_delete, "delete")

            print "DELETE SNAPSHOT OPERATION RESULTED IN ", self.delete_snapshot_operation
            return self.delete_snapshot_operation


class InstanceOperations(object):
    def __init__(self, server_name, image_name, flavour, **kwargs):
        self.image_name = image_name
        self.server_name = server_name
        self.flavour = flavour
        self.server_available_string = 'available'
        self.server_active_string = 'ACTIVE'
        self.no_attach = []
        self.volumes_inuse_string = 'in-use'

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

    def volumes_attach(self, volumes_name):
        print "================VOLUME ATTACH================"

        # Action: Modularize
        # check for volume status
        volumes_before_attach_subprocess_output_json = subprocess.check_output(['openstack', 'volume', 'show', volumes_name, '-f', 'json'])
        volumes_before_attach_subprocess_output_yaml = yaml.load(volumes_before_attach_subprocess_output_json)

        # volume addition to server or volume attach
        volumes_attach_subprocess_input = ['openstack', 'server', 'add', 'volume', self.server_name, volumes_name]
        volumes_attach_subprocess_output = subprocess.check_output(volumes_attach_subprocess_input)

        # Action: Modularize
        # check for addition of volume to server
        volumes_attach_subprocess_output_json = subprocess.check_output(['openstack', 'volume', 'show', volumes_name, '-f', 'json'])
        volumes_attach_subprocess_output_yaml = yaml.load(volumes_attach_subprocess_output_json)

       # ACTION : Modularize, combine with volume waiting. Pass the required status , error status as function variables
        while (volumes_attach_subprocess_output_yaml['status'] != 'in-use'):
            if (volumes_attach_subprocess_output_yaml['status'].lower == 'error'):
                print "\nFAILURE IN CREATING VOLUME %s. EXITING" % (volumes_attach_subprocess_output_yaml['name'])
                break
            print "\nWAITING FOR STATUS OF THE VOLUME %s TO BE IN-USE. CURRENTLY VOLUME STATE IS IN %s\n" % (volumes_attach_subprocess_output_yaml['name'],volumes_attach_subprocess_output_yaml['status'])
            time.sleep(10)
            volumes_attach_subprocess_output_json = subprocess.check_output(['openstack', 'volume', 'show', volumes_name, '-f', 'json'])
            volumes_attach_subprocess_output_yaml = yaml.load(volumes_attach_subprocess_output_json)

        print "\n volumes_attach_subprocess_output_yaml is", volumes_attach_subprocess_output_yaml

        attachment_details_server_id = volumes_attach_subprocess_output_yaml['attachments'][0]['server_id']
        attachment_details_attachment_id = volumes_attach_subprocess_output_yaml['attachments'][0]['attachment_id']
        attachment_details_volumes_id = volumes_attach_subprocess_output_yaml['attachments'][0]['volumes_id']
        attachment_details_device = volumes_attach_subprocess_output_yaml['attachments'][0]['device']

        print "\n attachment details", attachment_details_server_id, attachment_details_attachment_id, attachment_details_volumes_id, attachment_details_device

        inputs = [volumes_name, self.server_id , volumes_before_attach_subprocess_output_yaml['size'], volumes_before_attach_subprocess_output_yaml['type'],self.volumes_inuse_string ]
        print "\nINPUTS TO CREATE VOLUME", inputs

        values = [(volumes_attach_subprocess_output_yaml['name']), attachment_details_server_id, volumes_attach_subprocess_output_yaml['size'],
                  volumes_attach_subprocess_output_yaml['type'], volumes_attach_subprocess_output_yaml['status']]

        print "\nVALUES FROM THE CREATED VOLUME", values

        if values == inputs:
            print "\nVOLUME ATTACHED SUCCESSFULLY\n"

    def volumes_detach(self, volumes_name):
        print "\n================VOLUME DETACH================\n"
        # volume addition to server or volume attach
        list_check_output = ['openstack' , 'server' , 'remove' , 'volume' , self.server_name, volumes_name]
        op_attach_vol = subprocess.check_output(list_check_output)

        # check for detach of volume to server
        volumes_detach_subprocess_output_yaml = subprocess.check_output(['openstack' , 'volume' , 'show', volumes_name , '-f', 'json'])
        volumes_detach_subprocess_output_yaml = yaml.load(volumes_detach_subprocess_output_yaml)

        # ACTION : Modularize, combine with volume waiting. Pass the required status , error status as function variables
        while (volumes_detach_subprocess_output_yaml['status'] != 'available'):
            if (volumes_detach_subprocess_output_yaml['status'].lower == 'error'):
                print "\nFAILURE IN DETACHING VOLUME %s. EXITING" % (volumes_detach_subprocess_output_yaml['name'])
                break
            print "\nWAITING FOR STATUS OF THE VOLUME %s TO BE AVAILABLE. CURRENTLY VOLUME STATE IS IN %s\n" % (
            volumes_detach_subprocess_output_yaml['name'], volumes_detach_subprocess_output_yaml['status'])
            time.sleep(10)
            volumes_detach_subprocess_output_yaml = subprocess.check_output(['openstack', 'volume', 'show', volumes_name, '-f', 'json'])
            volumes_detach_subprocess_output_yaml = yaml.load(volumes_detach_subprocess_output_yaml)

            print "volumes_detach_subprocess_output_yaml is" , volumes_detach_subprocess_output_yaml
            print "\n\n"
            try:
                attachment_details_server_id = volumes_detach_subprocess_output_yaml['attachments'][0]['server_id']
                attachment_details_attachment_id = volumes_detach_subprocess_output_yaml['attachments'][0]['attachment_id']

                attachment_details_volumes_id = volumes_detach_subprocess_output_yaml['attachments'][0]['volumes_id']
                attachment_details_device = volumes_detach_subprocess_output_yaml['attachments'][0]['device']

            except IndexError:
                if volumes_detach_subprocess_output_yaml['status'] == 'available':
                    print "There does not seem to be any volume attached to server. Yes it is detached!. Now check the status of the volume"
                else:
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
