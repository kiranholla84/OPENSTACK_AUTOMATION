vol1 = {'name': 'vol1', 'size' : 40}
vol2 = {'name': 'vol2', 'size' : 41}
vol3 = {'name': 'vol3', 'size' : 42}
vol4 = {'name': 'vol4', 'size' : 43}
vol5 = {'name': 'vol5', 'size' : 44}


snap_details_input_list = []
list_of_snapshots_for_volume = []
volume_list_for_snapshots = [vol1, vol2, vol3, vol4, vol5]
length_volumes_array = len(volume_list_for_snapshots)
snapshot_name_prefix = 'snapshot_'
number_of_snapshot_per_volume = 2

for volumes_index in range(0, length_volumes_array):

    for snap_index in range(0, number_of_snapshot_per_volume):
        # Create a dictionary of values for each input snapshot  having common properties but
        # different values
        snap_details = {'name': snapshot_name_prefix +
                                (volume_list_for_snapshots[volumes_index])['name'] + "_" +
                                     str(snap_index),
                             'source_volume_name': volume_list_for_snapshots[volumes_index]['name'],
                             'snapshot_description': "THIS IS SNAPSHOT %s"
                                                     % (snapshot_name_prefix +
                                                        volume_list_for_snapshots[volumes_index]['name'] +
                                                        str(snap_index)),
                             }

        print "DEBUG1: snap_Details %s" % snap_details

        # Creating list of lists here - the inner list will be for snapshots for a single volume,
        # outer list is for tracking the list of snapshots for every volume

        snap_details_input_list.append(snap_details)
        print "DEBUG2: snap_details_input_list %s" % snap_details_input_list

    list_of_snapshots_for_volume.append(snap_details_input_list)
    snap_details_input_list = []

for volumes_index in range(0, length_volumes_array):
    for snap_index in range(0, number_of_snapshot_per_volume):
        print "\n================CREATING SNAPSHOT WITH NAME %s FOR VOLUME %s ================\n" \
              % (list_of_snapshots_for_volume[volumes_index][snap_index]['name'],
                 volume_list_for_snapshots[volumes_index]['name'])