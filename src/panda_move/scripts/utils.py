#-*- encoding: utf-8 -*-
import tf
import numpy as np
from geometry_msgs.msg import Pose, Quaternion
from moveit_commander.conversions import pose_to_list, list_to_pose

def position_list(pose):
    pos_list = [pose.position.x, pose.position.y, pose.position.z]
    return pos_list


def orientation_list(pose):
    ori_list = [pose.orientation.x, pose.orientation.y,
                pose.orientation.z, pose.orientation.w]
    return ori_list


def quaternion_to_rpy(pose):
    ori_rpy = tf.transformations.euler_from_quaternion(
        [pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w])
    return ori_rpy

def rpy_to_quaternion(rpy):
    quat = tf.transformations.quaternion_from_euler(rpy[0], rpy[1], rpy[2])
    orientation = Quaternion(quat[0], quat[1], quat[2], quat[3])

    return orientation

def rpy_to_quaternion_list(rpy):
    quat = tf.transformations.quaternion_from_euler(rpy[0], rpy[1], rpy[2])
    return quat.tolist()


def tf_to_mat(translation, rotation):
    trans_mat = tf.transformations.translation_matrix(translation)
    rot_mat = tf.transformations.quaternion_matrix(rotation)
    pose_mat = tf.transformations.concatenate_matrices(trans_mat, rot_mat)
    return pose_mat


def pose_to_mat(pose):
    pos_list = position_list(pose)
    ori_list = orientation_list(pose)
    pose_mat = tf_to_mat(pos_list, ori_list)
    return pose_mat

#list의 원소들을 trasnformation matrix형태로 변환
def pose_list_to_mat(pose_list):
    trans_mat = tf.transformations.translation_matrix(pose_list[:3])
    rot_mat = tf.transformations.quaternion_matrix(pose_list[3:])
    pose_mat = tf.transformations.concatenate_matrices(trans_mat, rot_mat)
    return pose_mat


def mat_to_pose(pose_mat):
    trans_list = list(tf.transformations.translation_from_matrix(pose_mat))
    rot_list = list(tf.transformations.quaternion_from_matrix(pose_mat))
    pose_list = trans_list + rot_list
    pose = list_to_pose(pose_list)
    return pose


def mat_to_pose_list(pose_mat):
    trans_list = list(tf.transformations.translation_from_matrix(pose_mat))
    rot_list = list(tf.transformations.quaternion_from_matrix(pose_mat))
    pose_list = trans_list + rot_list
    return pose_list

############
def inv_trans_mat(transformation):
    if isinstance(transformation, Pose):
        transformation_mat = pose_to_mat(transformation)
    elif isinstance(transformation, list):
        transformation_mat = pose_list_to_mat(transformation)
    elif isinstance(transformation, np.ndarray):
        transformation_mat = transformation
    inv_rot = tf.transformations.identity_matrix()
    inv_rot[:3, :3] = (transformation_mat[:3, :3]).T #rotation matrix만 trasnpose
    inv_trans = tf.transformations.translation_matrix(-transformation_mat[:, 3])
    inv_mat = tf.transformations.concatenate_matrices(inv_rot, inv_trans)
    return inv_mat


def concatenate_to_pose(*args):
    pose_mats = tuple()
    for pose in args: # transformation matrix로 변경
        #ex) isinstance(1,int) => true
        print(pose,type(pose),3)
        if isinstance(pose, Pose):
            print(pose,5555)
            pose_mat = pose_to_mat(pose) 
        elif isinstance(pose, list):
            print(pose,4555)
            pose_mat = pose_list_to_mat(pose)
            #print(pose_mat,777)
        elif isinstance(pose, np.ndarray):
            print(pose,3555)
            pose_mat = pose
        pose_mats += (pose_mat, ) #array[1,2,3] + array[4,5,6] = array[[1,2,3],[4,5,6]]
        print(pose_mats,4)

    # result_mat = tf.transformations.concatenate_matrices(pose_mats)
    result_mat = tf.transformations.identity_matrix()
    for M in pose_mats:
        result_mat = np.dot(result_mat, M)
    result_pose = mat_to_pose(result_mat) #trasnformation matrix => pose
    
    return result_pose


def concatenate_to_pose_list(*args):
    pose_mats = tuple()

    for pose in args: #=>(0,0,0,0,0,0,0)형태로 변경
        print(pose,3)
        if isinstance(pose, Pose):
            pose_mat = pose_to_mat(pose)
            #print(pose,5555)
        elif isinstance(pose, list):
            pose_mat = pose_list_to_mat(pose)
            #print(pose,4555)
        elif isinstance(pose, np.ndarray):
            pose_mat = pose
            #print(pose,35555)
        pose_mats += (pose_mat, )
        
    result_mat = tf.transformations.identity_matrix()
    for M in pose_mats:
        result_mat = np.dot(result_mat, M)
    result_pose = mat_to_pose_list(result_mat)
    
    return result_pose


def add(list1, list2):
    result = np.add(list1,list2)
    return result.tolist()