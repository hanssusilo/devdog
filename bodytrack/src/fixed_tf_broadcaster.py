#!/usr/bin/env python
import roslib
roslib.load_manifest('DevDog')
import rospy    
import tf

if __name__ == '__main__':
    rospy.init_node('fixed_tf_broadcaster')
    tracker1_tf = tf.TransformBroadcaster()
    tracker2_tf = tf.TransformBroadcaster()
    rate = rospy.Rate(10.0)
    while not rospy.is_shutdown():
        # pass in parameters to define number and pose of kinects
        numKinects = rospy.get_param('numKinects')
    
        if numKinects > 0:
            # the first kinect is 0.5m ahead of the origin
            position1 = rospy.get_param('position1')
            rotation1 = rospy.get_param('rotation1')
            tracker1_tf.sendTransform(tuple(position1),
                             tf.transformations.quaternion_from_euler(rotation1[0], rotation1[1], rotation1[2]),
                             rospy.Time.now(),
                             "kinect1_depth_frame",
                             "origin")
        if numKinects > 1:
            # the second kinect is 0.5m behind the origin and yawed 90 degrees
            position2 = rospy.get_param('position2')
            rotation2 = rospy.get_param('rotation2')
            tracker2_tf.sendTransform(tuple(position2),
                             tf.transformations.quaternion_from_euler(rotation2[0], rotation2[1], rotation2[2]),
                             rospy.Time.now(),
                             "kinect2_depth_frame",
                             "origin")
        rate.sleep()
