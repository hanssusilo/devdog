#!/usr/bin/env python

import roslib
roslib.load_manifest('DevDog')
import rospy    
import tf
import math
import time
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
from collections import deque
from numpy import *

# autonmatically adapts to the number of kinects that are feeding in information

# take a simple average
def average(numList):
    sum = 0
    for i in numList:
        sum += i
    if len(numList) > 0:
        return sum/len(numList)
    else:
        return 0

# add each element of a 3-element array to a specified deque
# assumes all deques are of the same size
def addToMovingWindow(elements, windowSize, *deque):
    if len(deque[0][0]) > windowSize-1:         # remove oldest element from the deques if bigger than a certain windowSize
        for i in deque[0]:
            i.popleft()

    for i in range(len(deque[0])):
#        print i, "elements length:", len(elements), "deque length:", len(deque[0])
        deque[0][i].append(elements[i])

    return deque

# find the distance between two points
def distBtwnPoints(point1, point2):
    if len(point1) != len(point2):
        print "ERROR: point dimensions don't match"
        return 0        # incompatiable points
    else:
        dist = 0
        for i in range(len(point1)):
            dist = dist + (point1[i]-point2[i])*(point1[i]-point2[i])
        dist = math.sqrt(dist)
        return dist

# find the number label of each person the kinect(s) see, along with which kinect saw it
# takes the output of listener.getFrameStrings(), a list of frames as strings
def getSkeletonList(tfFrames):
    skeletonList = []
    for frame in tfFrames:
        # find every frame with the label "torso" and return the skeleton identifier in the form of kinectNumber_skeletonNumber
        if (frame.find("torso") != -1):
            frame = frame[6:]                                           # remove the substring "/torso" to get the skeleton identifier
            splitStr = frame.split("_")
            if splitStr[0] == "":                                       # turn the identifier into a tuple
                skeletonList.append((1,int(splitStr[1])))               # append the tuple (kinectNumber, skeletonNumber) to skeletonList
            else:
                skeletonList.append((int(splitStr[0]),int(splitStr[1])))
#    if (len(skeletonList) == 1):
#        print "Found", str(len(skeletonList)), "person"                 # because grammar is important
#   else:
#        print "Found", str(len(skeletonList)), "people"
#    print "skeletonList", skeletonList, "\n"
    return skeletonList   

# filter the data and do cross products to get the pose and velocity of a skeleton
def handleTracking(listener, skelID, currentlyFollowing):
#    print "tracking skeleton", skelID, "with index", sIndex                    

    kinectTf = '/kinect'+str(skelID[0])+'_depth_frame'

    frameNameModifier = ""                      # modify appropriately to match joint naming convention
    if skelID[0] != 1:
        frameNameModifier = str(skelID[0])
    
    (transTorso,rotTorso) = listener.lookupTransform(kinectTf, '/torso'+frameNameModifier+'_'+str(skelID[1]), rospy.Time(0))
    # smooth out the position data
    addToMovingWindow(transTorso, windowSize, currentTorsoPosDeques[sIndex])
    posSmooth = [average(currentTorsoPosDeques[sIndex][0]), average(currentTorsoPosDeques[sIndex][1]), average(currentTorsoPosDeques[sIndex][2])]
  	
  	# calculate the velocity
    velSmooth = [posSmooth[0]-prevTorsoPos[sIndex][0], posSmooth[1]-prevTorsoPos[sIndex][1], posSmooth[2]-prevTorsoPos[sIndex][2]]

    # average the orientations of the shoulders and the hips
    (transNeck,rotNeck) = listener.lookupTransform(kinectTf, '/neck'+frameNameModifier+'_'+str(skelID[1]), rospy.Time(0))                                 # neck
    (transLeftShoulder,rotLeftShoulder) = listener.lookupTransform(kinectTf, '/left_shoulder'+frameNameModifier+'_'+str(skelID[1]), rospy.Time(0))        # left shoulder
    (transRightShoulder,rotRightShoulder) = listener.lookupTransform(kinectTf, '/right_shoulder'+frameNameModifier+'_'+str(skelID[1]), rospy.Time(0))     # right shoulder
    (transLeftHip,rotLeftHip) = listener.lookupTransform(kinectTf, '/left_hip'+frameNameModifier+'_'+str(skelID[1]), rospy.Time(0))                       # left hip
    (transRightHip,rotRightHip) = listener.lookupTransform(kinectTf, '/right_hip'+frameNameModifier+'_'+str(skelID[1]), rospy.Time(0))                    # right hip
    
    (transRightHand,rotRightHand) = listener.lookupTransform(kinectTf, '/left_hand'+frameNameModifier+'_'+str(skelID[1]), rospy.Time(0))          # right hand (this is actually flipped on the Kinect's POV)
    (transLeftHand,rotLeftHand) = listener.lookupTransform(kinectTf, '/right_hand'+frameNameModifier+'_'+str(skelID[1]), rospy.Time(0))          # right hand (this is actually flipped on the Kinect's POV)
    (transHead,rotHead) = listener.lookupTransform(kinectTf, '/head'+frameNameModifier+'_'+str(skelID[1]), rospy.Time(0))                    # head

    tVec = matrix(transNeck)-matrix(transTorso)                     # torso vector (torso to neck)
    sVec = matrix(transRightShoulder)-matrix(transLeftShoulder)     # shoulder vector (left to right)
    hVec = matrix(transRightHip)-matrix(transLeftHip)               # hip vector (left to right)
    
    oVec = (cross(tVec,sVec)+cross(tVec,hVec))                      # sum of (tVec cross sVec) and (tVec cross hVec)
    oVec = oVec/linalg.norm(oVec)                                   # divide by the norm to get the unit vector (orientation is always a unit vector)
    oVec = oVec[0]                                                  # change from matrix to vector

    ############### visualization section ######################
    # broadcast transforms for visualization (can comment out later for speed)
    
    oVecScaled = [x*5 for x in oVec]                         # scale the orientation so it's easier to see on rviz
    velSmoothScaled = [x*10 for x in velSmooth]              # scale the velocity vector so it's easier to see in rviz
    
    velocityTfBroadcasters[sIndex].sendTransform([velSmoothScaled[1], velSmoothScaled[2], velSmoothScaled[0]], tf.transformations.quaternion_from_euler(0, 0, 0), rospy.Time.now(), "velocity"+frameNameModifier+"_"+str(skelID[1]), "torso"+frameNameModifier+"_"+str(skelID[1]))
    
    orientationTfBroadcasters[sIndex].sendTransform([0,0,-1], tf.transformations.quaternion_from_euler(oVecScaled[0],oVecScaled[1],oVecScaled[2]), rospy.Time.now(), "orientation"+frameNameModifier+"_"+str(skelID[1]), "torso"+frameNameModifier+"_"+str(skelID[1]))

    ############################################################

    # smooth out the orientation data
    addToMovingWindow(oVec, windowSize, currentOrientationDeques[sIndex])
    oVecSmooth = [average(currentOrientationDeques[sIndex][0]), average(currentOrientationDeques[sIndex][1]), average(currentOrientationDeques[sIndex][2])]
    
    # debug prints                
#    print "Skeleton ID:", s
#    print "position", posSmooth
#    print "velocity", velSmooth
#                print "orientation", oVec
    print "----------------------------- \n"
        
    prevTorsoPos[sIndex] = posSmooth
    if velSmooth == [0.0, 0.0, 0.0]:
        removalCounters[sIndex] = removalCounters[sIndex] + 1
    else:
        removalCounters[sIndex] = 0

    # gestures section
    surrender = (transRightHand[2] > transHead[2] and transLeftHand[2] > transHead[2])
    overlappingHands = (distBtwnPoints(transRightHand, transLeftHand) < 0.25)
    rightHandUp = (transRightHand[2] > transHead[2] and transLeftHand[2] < transHead[2])
    leftHandUp = (transRightHand[2] < transHead[2] and transLeftHand[2] > transHead[2])
    handsAtShoulders = (distBtwnPoints(transRightHand, transRightShoulder) < 0.35) and (distBtwnPoints(transLeftHand, transLeftShoulder) < 0.35)

    currentGestures = ()

    if currentlyFollowing != -1:
    
        if surrender:
            print "SURRENDER"
            currentGestures = currentGestures + ("SURRENDER",)
        if overlappingHands:
            print "OVERLAPPING HANDS"
            currentGestures = currentGestures + ("OVERLAPPING HANDS",)
        if rightHandUp:
            print "RIGHT HAND UP"
            currentGestures = currentGestures + ("RIGHT HAND UP",)
        if leftHandUp:
            print "LEFT HAND UP"
            currentGestures = currentGestures + ("LEFT HAND UP",)
        if handsAtShoulders:
            print "HANDS AT SHOULDERS"
            currentGestures = currentGestures + ("HANDS AT SHOULDERS",)
    
    prevGestures[sIndex] = currentGestures 

    # publish the torso position of the skeleton we are following 
    if currentlyFollowing == sIndex:
#        dataLog = str(s), str(posSmooth[0]), str(posSmooth[1]), str(posSmooth[2]), str(velSmooth[0]), str(velSmooth[1]), str(velSmooth[2]), str(oVecSmooth[0]), str(oVecSmooth[1]), str(oVecSmooth[2])

        if surrender:
            currentlyFollowing = -1
            positionError = Vector3()
            positionError.x = 0
            positionError.y = 0
            positionError.z = 0
#            rospy.loginfo(positionError)
            trackingError.publish(positionError)
            
            
        else:
            print "TRYING TO FOLLOW"
            standoffDist = 2.5
            if overlappingHands:
                standoffDist = 1.5
        
            pGain = 50.0
            positionError = Vector3()
            positionError.x = (posSmooth[0]-standoffDist)*pGain
            positionError.y = posSmooth[1]*pGain*2
            positionError.z = posSmooth[2]*pGain
#            rospy.loginfo(positionError)
            trackingError.publish(positionError)

def findUserToFollow():                          # find a present and moving user to follow
    for s in skeletonList:
        sIndex = skeletonList.index(s)
#        print "sIndex", sIndex, "counter length:", len(removalCounters)
        while len(removalCounters) <= sIndex:
            removalCounters.append(0)

        if removalCounters[sIndex] < 30:
#            print "removalCounters", removalCounters[sIndex]
            return sIndex
    return -1                                   # returns -1 if none is found

if __name__ == '__main__':

    currentlyFollowing = -1
    prevGestures = []

    rospy.init_node('movement_tracker')		            # start the node
    trackingError = rospy.Publisher('set_vel', Vector3)     # start the rostopic to be published to
        
    listener = tf.TransformListener()                   # start the transform listener

    velocityTfBroadcasters = []                         # vector of transforms that represent users' velocities
    orientationTfBroadcasters = []                      # vector of transforms that represent users' orientations

    # tracks users that are entering/leaving frame to create position and rotation arrays appropriately
    prevSkeletonList = []
    
    # stores 3-element vectors of previous positions for instantaneous velocity calculations
    prevTorsoPos = []
    
    # stores 3-element tuples (each element is a deque of up to [windowSize] elements) of positions for smoothed positions (arrays of x, y and z)
    currentTorsoPosDeques = []
    
    # stores 3-element tuples (each element is a deque of up to [windowSize] elements) of rotations for smoothed positions (arrays of r, p, y)
    currentOrientationDeques = []
    
    # stores and array of ints, keeping track of how long each skeleton has been stationary (missing from frame)
    removalCounters = []

    framesPerSecond = 10
    timeWindow = 1                                      # seconds
    windowSize = timeWindow*framesPerSecond             # window size for moving averages
    
    time.sleep(3)                                       # wait for connections to devices to start up

    while not rospy.is_shutdown():
        try:
            skeletonList = getSkeletonList(listener.getFrameStrings())
            
            # assumes that the skeletonList never loses members, only gains them (seems to be a valid assumption from the OpenNI behavior)
            # don't remove any skeletons, but OpenNI seems to be able to "remember" skeletons pretty well
            
            for s in skeletonList:
                # add additional slots for pose and velocity information for additional skeletons
                if s not in prevSkeletonList:
                    prevTorsoPos.append([0,0,0])
                    currentTorsoPosDeques.append((deque([]), deque([]), deque([])))                         # tuple of 3 deques for x, y, and z positions
                    currentOrientationDeques.append((deque([]), deque([]), deque([])))                      # tuple of 3 deques for rpy rotations
                    velocityTfBroadcasters.append(tf.TransformBroadcaster())                                # add a new broadcaster for representing velocities
                    orientationTfBroadcasters.append(tf.TransformBroadcaster())                             # add a new broadcaster for representing orientations
                    removalCounters.append(0)
                    prevGestures.append(())
                    print "added a removal counter"

                sIndex = skeletonList.index(s)          # position in the list does not correspond to the skeleton number

                handleTracking(listener, s, currentlyFollowing)
                
                #print "removal counter", removalCounters[sIndex]
                if removalCounters[sIndex] > 30:
                    currentlyFollowing = -1
                              
                if currentlyFollowing == -1:
                    # send a stop command
                    positionError = Vector3()
                    positionError.x = 0
                    positionError.y = 0
                    positionError.z = 0
                    rospy.loginfo(positionError)
                    trackingError.publish(positionError)

                    currentlyFollowing = findUserToFollow()

                print "currently following", currentlyFollowing

            # put any new skeletons into the old skeleton list
            prevSkeletonList = skeletonList

            rospy.Rate(30.0).sleep()            # checking at 30 hz

        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            print "ERORR: something is wrong with the transform."
            rospy.Rate(1.0).sleep()             # checks every second to see if the data is coming through
            continue
