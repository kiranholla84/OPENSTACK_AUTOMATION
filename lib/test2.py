input_volume_list = [1,2,3,4,5]
input_snapshot_list = [['0_0','0_1'],['1_0','1_1'],['2_0','2_1']]

for volume_index in range(len(input_volume_list)):
    for snapshot_index in range(len(input_snapshot_list)):
        print "\n volume index snapshot_index FINALVALUE %s %s %s" %(volume_index, snapshot_index , input_snapshot_list[volume_index][snapshot_index])

        