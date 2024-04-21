'''
@pkraison (Prashant Kumar Rai)'''
import rosbag
import argparse
import os
from array import array
import shutil
# Lidar Rosbag to Kitti format converter.
"""Record the rosbag with IMU and provide the directory as input and a directory
for output files in Kitti format
Run: python3 rosbag2imu.py -in '/path to bag files/' --out '/path to output/' --imu 'imu topic name' """

if __name__ == '__main__':
  
  parser = argparse.ArgumentParser(description='turn list of rosbags into Kitti dasatet format')
  parser.add_argument('-i', '--in_dir', type=str, default = '', help='directory in which input bag files are stored')
  parser.add_argument('-o', '--out_dir', default = '', type=str, help='base directory for output dataset')
  parser.add_argument('--imu', type=str, default='/os_cloud_node/imu', help='IMU message topic')
  args = parser.parse_args()

  if args.in_dir[-1] != '/':
    args.in_dir = args.in_dir + '/'
  if not os.path.isdir(args.in_dir):
    print('Input rosbag directory (' + args.in_dir + ') does not exist.')
    exit()

  if args.out_dir[-1] != '/':
    args.out_dir = args.out_dir + '/'
  if not os.path.isdir(args.out_dir):
    print('Output dataset directory (' + args.out_dir + ') does not exist.')
    exit()

  # get list of rosbags to convert
  bag_list = []
  for root, dirs, files in os.walk(args.in_dir):
    date = root.split('/')[-1]
    for file in files:
      if file.endswith('.bag'):
        bag_list.append((file,date))

  for bag_filename, date in bag_list:
    bag_name = bag_filename.split('.')[0]
    base_dir = args.out_dir + date + '_' + bag_name + '/'

    # check if directory structure already exists, create it if not
    if not os.path.isdir(base_dir + 'imu/'):
      os.mkdir(base_dir + 'imu/')
      
    bag = rosbag.Bag(args.in_dir + date + '/' + bag_filename)
    print(bag)
    # read imu data from bag and write to output files
    gen = bag.read_messages(topics=[args.imu])
    #gen = sorted(gen, key=lambda a: a[1].header.stamp.to_sec())
    imu_t_file = open(base_dir + 'imu/timestamps.txt', 'w')
    imu_data_file = open(base_dir + 'imu/imu_data.txt', 'w')
    for topic, msg, t in gen:
      imu_t_file.write('%6f\n' % (msg.header.stamp.to_sec()))
      a_x = msg.linear_acceleration.x
      a_y = msg.linear_acceleration.y
      a_z = msg.linear_acceleration.z
      alpha_x = msg.angular_velocity.x
      alpha_y = msg.angular_velocity.y
      alpha_z = msg.angular_velocity.z
      imu_data_file.write(str(a_x) + ' ' + str(a_y) + ' ' + str(a_z) + ' ' + 
                          str(alpha_x) + ' ' + str(alpha_y) + ' ' + str(alpha_z) + '\n')
    imu_t_file.close()
    imu_data_file.close()
