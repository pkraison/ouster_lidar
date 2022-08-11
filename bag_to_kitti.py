import rosbag
import argparse
from sensor_msgs.msg import PointCloud2, PointField
import sensor_msgs.point_cloud2 as pcl
import os
from array import array
import shutil
# Lidar Rosbag to Kitti format converter.
"""Record the rosbag with lidar and IMU and provide the directory as input and a directory
for output files in Kitti format"""

if __name__ == '__main__':
  
  parser = argparse.ArgumentParser(description='turn list of rosbags into ColoRadar dasatet format')
  parser.add_argument('-i', '--in_dir', type=str, default = '/home/ndprra/Documents/RadarTB/rrd/ColoRadar_tools-master2/python/bags/', help='directory in which input bag files are stored')
  parser.add_argument('-o', '--out_dir', default = '/home/ndprra/Documents/RadarTB/rrd/ColoRadar_tools-master2/python/li', type=str, help='base directory for output dataset')
  parser.add_argument('--lidar', type=str, default='/os_cloud_node/points')
  parser.add_argument('--imu', type=str, default='/os_cloud_node/imu')
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
    if not os.path.isdir(base_dir + 'lidar/'):
      os.mkdir(base_dir + 'lidar/')
    if not os.path.isdir(base_dir + 'lidar/pointclouds/'):
      os.mkdir(base_dir + 'lidar/pointclouds/')
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

    gen = bag.read_messages(topics=[args.lidar])
    print(gen)
    #gen = sorted(gen, key=lambda a: a[1].header.stamp.to_sec())
    lidar_t_file = open(base_dir + 'lidar/timestamps.txt', 'w')
    msg_idx = 0
    for topic, msg, t in gen:
      lidar_t_file.write('%6f\n' % (msg.header.stamp.to_sec()))

      point_gen = pcl.read_points(msg,
                                  skip_nans=True,
                                  field_names=('x','y','z','intensity'))
      cloud_file = open(base_dir + 'lidar/pointclouds/lidar_pointcloud_' + str(msg_idx) + '.bin', 'wb')
      for point in point_gen:
        arr = array('f', point)
        arr.tofile(cloud_file)
      cloud_file.close()

      msg_idx += 1

    lidar_t_file.close()
