#! /usr/bin/env python
#-*- encoding: utf-8 -*-
from numpy.lib.function_base import place
from pose_level_motion import *
import tf
import sys
import os
import copy
import rospy #rospy is a pure Python client library for ROS => ros log
import yaml
import numpy as np
import math as m
import random
import pyautogui #마우스 제어?
from os.path import dirname
from collections import defaultdict #처음 key를 지정할 때 값을 주지 않으면 값을 default로 지정
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from std_msgs.msg import String
from visualization_msgs.msg import Marker
from moveit_commander.conversions import pose_to_list, list_to_pose
from geometry_msgs.msg import Quaternion
import threading
import time
#sample들 import 
import utils #여러가지 함수들 들어있는 모듈
import sample.club_sandwich
import sample.tuna_sandwich
import sample.greek_salad
import sample.shrimp_salad
import sample.carrot_salad
#request와 response할 객체 이름을 정해서 가져옴
from panda_move.srv import Init, InitRequest, InitResponse  
from panda_move.srv import Sync, SyncRequest, SyncResponse
from panda_move.srv import Plan, PlanRequest, PlanResponse
from panda_move.srv import Hand, HandRequest, HandResponse
from panda_move.srv import MotionCheck, MotionCheckRequest, MotionCheckResponse
from panda_move.msg import ExecutionCheck

# Set Path
## dirname(__FILE__) echo __FILE__; // 파일명을 포함한 경로
## echo dirname(__FILE__); //파일명을 제외한 경로
YAML_PATH = dirname(dirname(__file__)) + '/config/' #panda_move/config
POSE_INFO_PATH = YAML_PATH + 'object_pose_info.yaml' #object grasp pose가 있는 파일 
STL_INFO_PATH = YAML_PATH + 'object_stl_info.yaml' #object pose와 scale이 있는 파일 
PLACEMENT_INFO_PATH = YAML_PATH + 'placement_pose_info.yaml' #cutting_board와 같은 placement_pose가 있는 파일
STL_PATH = dirname(dirname(dirname(__file__))) + '/object_sample/'  #object 종류가 들어있는 파일

def import_yaml(file_path):
    with open(file_path) as f:  
        yaml_data = yaml.load(f, Loader=yaml.FullLoader)
    return yaml_data

def pressEnter(msg):  #마우스 제어? 현제 사용x
    if msg.status:
        pyautogui.press('enter')

class ObjectLevelMotion(PoseLevelMotion): #poselevelmotion을 상속받음
    def __init__(self, use_unity, self_play=True):
        PoseLevelMotion.__init__(self, self_play)

        # True to use unity / False to not use unity
        self.unity = use_unity

        # yaml파일 불러옴 config폴더안에 yaml파일 존재
        self.obj_pose_yaml = import_yaml(POSE_INFO_PATH)
        self.obj_stl_yaml = import_yaml(STL_INFO_PATH)
        self.placement_yaml = import_yaml(PLACEMENT_INFO_PATH)

        # publisher
        self.marker_pub = rospy.Publisher('action', Marker, queue_size=1) #marker publisher

        # key=object state, val=object list
        self.objects = defaultdict(list)  #default값이 list인 딕션어리
        # obj instance -> obj type
        self.instance_type = dict()
        # place area -> list of placement pose name
        self.place_area_poses = defaultdict(list)
        # key=container, val=(sorted)list of objects
        self.contain_objects = dict()
        # key=object, val=number of pour
        self.num_of_pour = defaultdict(int) #default값이 int인 딕션어리
        # self.execution_check()
        # check_thread = threading.Thread(target=self.execution_check)
        # check_thread.start()

    #add objects to the scene and initialize lists
    def initialize(self, arrange_info, fixed_pose=None): #arrang_info = sandwich.obj_place 
        try:     
            # initialize self.place_area_poses
            for key, val in self.placement_yaml.items(): #config에 있는 파일
                for area in val['area']: #value값이 'area'인것에 대해서
                    self.place_area_poses[area].append(key) #key:area([stove_cookware_area]) value:stove_1 =>같은 area를 가지는 key값 존재
            #check self.object가 add object한 후 추가?

            # temp = []
            for (obj_instance, obj_type, place_area, obj_state) in arrange_info: #왜 ingredient가 2번 들어감? => bread같은 경우 bread1,bread2,bread3 존재
                # add object
                placement = self._select_pose_from_area(obj_type, place_area) #placement 선택
                self._arrange(obj_instance, obj_type, placement) # 그 placement에 add object

                # initialize obj_state
                if obj_state is not None:
                    self.objects[obj_state].append(obj_instance) #ex) key:activated value:tomato =>self.objects 추가 
                    
                
                # temp.append([obj_state, obj_instance])
                #
                #
                # initialize obj_instance
                self.instance_type[obj_instance] = obj_type # self.instance_type 추가 
            # for (a, b) in temp:
            #       self.objects[a] = b
            raw_input("Initial Scene Configuration Completed")

        except Exception as e:
            rospy.logerr(e)

    #ingredient를 possible_area에 random하게 배치
    def _select_pose_from_area(self, obj, obj_to_area):
        candidate_poses = []
        feasible_poses = []
        selected_pose = None

        # update place pose state
        place_available, _ = self._update_place_pose_state() #activated한 obj에 대해서
        print('-'*30)
        print(place_available)

        # candidate_poses
        candidate_poses = self.place_area_poses[obj_to_area] #레시피 파일의 place_area
        print('candidate_poses', candidate_poses)

        # feasible_poses
        for pose in candidate_poses: #하나의 area에 대한 여러개 candidate중
            if not place_available[pose]: #obj가 없으면 추가
                feasible_poses.append(pose)
        print('feasible_poses', feasible_poses)

        # selected_pose
        if feasible_poses:
            selected_pose = random.choice(feasible_poses) #random하게 하나 선택     
        print('selected_pose', selected_pose)
        print('-'*30)

        return selected_pose

 
    #return which objects are located at place poses => 함수 안 함수 구조
    #place poses에 어떤 물체들이 놓여져 있는지 return
    #activated(initialize할 때 spawn) <=> deactivated(나중에 spawn)
    def _update_place_pose_state(self):
        place_pose_state = {}
        place_thresh = 0.1
        
        rospy.loginfo('wait for update_place_pose_state') #loginfo 함수 check
        time.sleep(0.7)

        def distance(p1, p2): 
            return m.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

        # get collision object poses from Planing Scene 
        # 딕션어리 형태로 collision object pose들을 가져옴
        obj_poses = dict() 
        for obj in self.objects['activated']: #activated인 object에 대해서
            obj_pose = self.get_object_pose(obj) #poselevelmotion의 pose값 구하는 함수
            rospy.loginfo("obj={}, obj_pose={}".format(obj, obj_pose))
            if obj_pose: #값이 있으면
                obj_poses[obj] = obj_pose 
            else:
                rospy.logerr("self.objects", self.objects)
                exit()

        for key, val in self.placement_yaml.items():
            place_pose_state[key] = []
            
            # calculate xy_dist
            for obj, obj_pose in obj_poses.items():
                obj_type = self.instance_type[obj]
                place_pose = self._make_place_pose(obj_type)
                obj_place_pose = utils.concatenate_to_pose_list(obj_pose, place_pose)
                xy_dist = distance(val['pose'], obj_place_pose)
                if xy_dist < place_thresh:
                    # bottom = obj_place_pose[2] - self.obj_stl_yaml[obj_type]['thickness'][0]
                    bottom = obj_place_pose[2] #place_pose를 bottom으로 가져옴
                    place_pose_state[key].append({'name': obj, 'z': bottom})
            
            # sort by z value
            rospy.loginfo("^"*30) #??
            if place_pose_state[key]:
                rospy.loginfo("key={}, val={}".format(key, place_pose_state[key]))
                sorted_obj = sorted(place_pose_state[key], key=lambda x: x.get('z'))
                place_pose_state[key] = [obj['name'] for obj in sorted_obj] #key:table1_empty_1 value:tomatto => 하나씩 존재
        
        return place_pose_state, obj_poses.keys() 





    def _arrange(self, obj_name, obj_type, placement): #check
        try:
            placement_pose = self.placement_yaml[placement]['pose'] # placement_pose값을 가져옴
            place_pose = self._make_place_pose(obj_type) #obj에 대한 place_pose를 가져옴
            place_pose_inv = utils.inv_trans_mat(place_pose) # inverse로 변경
            
            object_pose = utils.concatenate_to_pose_list(placement_pose, place_pose_inv) #최종적으로 object pose 구함
            object_mesh = STL_PATH + self.obj_stl_yaml[obj_type]['file_name']
            object_size = self.obj_stl_yaml[obj_type]['scale']
            frame_id = self.placement_yaml[placement]['frame_id'] #world로 동일

            # raw_input(obj_name)
            rospy.loginfo(obj_name)
            self.add_object(obj_name, object_pose, 
                            object_mesh, object_size, frame_id) #obj 추가

        except Exception as e:
            rospy.logerr(e)

    #thickness와 orient를 고려하여 obj의 place pose를 설정
    def _make_place_pose(self, obj_type):
        if 'place_pos' in self.obj_pose_yaml[obj_type].keys(): #knife, spatula, scooper, spreader
            place_pos = self.obj_pose_yaml[obj_type]['place_pos'] # 파일에 있는 값 가져옴
        else:
            place_pos = [0, 0, -self.obj_stl_yaml[obj_type]['thickness'][0]-0.001] #이외의 모든 obj에 대한 thickness를 가져옴 ex)[0,0,0.0006]
        place_orient = utils.rpy_to_quaternion_list(self.obj_pose_yaml[obj_type]['place_orient']) #orient를 가져옴 euler -> quaternion
        place_pose = place_pos + place_orient

        return place_pose



    ### Unity - ROS Communication Method Start ###
    #Send initial configuration scene to Unity
    def init_sync(self):
        if self.unity == True: #unity와 연결되어 있을때
            try:
                rospy.wait_for_service("init_sync")
                init_sync_client = rospy.ServiceProxy("init_sync", Init) #Client 객체 생성
                init_sync_req = InitRequest() #obj의 정보와 joint정보를 request할 객체 생성

                joint_state = self.robot.get_current_state().joint_state.position #현재 로봇의 joint state를 가져옴
                init_sync_req.joint_state = joint_state #joint state의 정보를 담음

                for i in range(len(self.objects["activated"])): #activate된 object에 대해서 name,type,position,orientation정보를 가져옴
                    temp_name = self.objects["activated"][i]
                    temp_type = self.instance_type[temp_name] #bread1 -> bread
                    temp_position = self.get_object_pose(temp_name).position
                    temp_orientation = self.get_object_pose(
                        temp_name).orientation

                    init_sync_req.activated_object.append(temp_name) #이름 정보 담음
                    # init_sync_req.object_name.append(temp_name)
                    # scale과 관련된 정보 
                    init_sync_req.position.append(temp_position) #position 정보 담음
                    init_sync_req.orientation.append(temp_orientation) #orientation 정보 담음
                    temp_scale = geometry_msgs.msg.Vector3() #Vector3라는 객체 생성
                    temp_scale.x = self.obj_stl_yaml[temp_type]["scale"][0]
                    temp_scale.y = self.obj_stl_yaml[temp_type]["scale"][1]
                    temp_scale.z = self.obj_stl_yaml[temp_type]["scale"][2]
                    init_sync_req.scale.append(temp_scale) #scale에 대한 정보 담음
                
                init_sync_res = init_sync_client(init_sync_req) #request할 정보를 담아서 전달후 response 받음
                if init_sync_res.init_state == 1: #response를 받으면 1
                    raw_input("Initialization Sync Completed")
                else:
                    rospy.loginfo("[Unity Error] Initialization Sync Failed")

            except Exception as e:
                rospy.logerr(e)
        elif self.unity == False:
            pass
    
    #receive configuration of scene from Unity
    def scene_sync(self):
        if self.unity == True:
            try:
                rospy.wait_for_service("scene_sync")
                scene_sync_client = rospy.ServiceProxy("scene_sync", Sync) 
                scene_sync_req = SyncRequest()
                scene_sync_req.activated_object = self.objects["activated"] #activated obj를 request (deactivated ->activated)

                scene_sync_res = scene_sync_client(scene_sync_req) #request할 정보를 담아서 전달후 response 받음
                #joint와 관련된 정보
                for i in range(len(scene_sync_res.joint_state)): #unity의 joint state
                    if i == 0:
                        self.joint[i].move(scene_sync_res.joint_state[i]) #pose_level_motion에서 정의한 것들
                    elif i > 0 and i < 7:
                        self.joint[i].move(
                            scene_sync_res.joint_state[i] * m.pi / 180) # 왜 / 180?
                    else:
                        self.joint[i].move(scene_sync_res.joint_state[i]) #eef 

                #rviz상 scene update
                for i in range(len(scene_sync_res.object_name)): 
                    temp_name = scene_sync_res.object_name[i]
                    temp_pose = geometry_msgs.msg.Pose()
                    temp_pose.position = scene_sync_res.position[i]
                    temp_pose.orientation = scene_sync_res.orientation[i]
                    self.update_object_pose(temp_name, temp_pose) #rviz상 scene update
                rospy.loginfo("Scene Sync Completed")

            except Exception as e:
                rospy.logerr(e)

        elif self.unity == False:
            pass

    #send state of panda hand to Unity
    def hand_sync(self, object_name, grasp_size):
        if self.unity == True:
            try:#grasp_state, object_name, grasp_size와 관련된 정보들 전달
                rospy.wait_for_service("hand_sync")
                hand_sync_client = rospy.ServiceProxy("hand_sync", Hand)
                hand_sync_req = HandRequest()
                hand_sync_req.grasp_state = self.grasp_state
                hand_sync_req.object_name = object_name
                hand_sync_req.grasp_size = grasp_size

                hand_sync_res = hand_sync_client(hand_sync_req) #바로 request

                if hand_sync_res.execute_state == 1:
                    rospy.loginfo("Hand Sync Completed")
                else:
                    rospy.loginfo("[Unity Error] Hand Sync Failed")

            except Exception as e:
                rospy.logerr(e)

        elif self.unity == False:
            pass

    #send plan trajectoryof panda to Unity
    def panda_plan(self, plan_i): #plan을 입력받음
        if self.unity == True:
            try:#panda_plan_req정보를 전달
                rospy.wait_for_service("panda_plan")
                panda_plan_client = rospy.ServiceProxy("panda_plan", Plan)
                panda_plan_req = PlanRequest()
                panda_plan_req.trajectories.append(plan_i) 

                panda_plan_res = panda_plan_client(panda_plan_req) #trajectories 정보 request

                if panda_plan_res.execute_state == 1: #response
                    raw_input("Plan Execution Complelted")
                else:
                    rospy.loginfo("[Unity Error] Plan Execution Failed")

                # self.execution_check()

            except Exception as e:
                rospy.logerr(e)

        elif self.unity == False:
            pass
    
    #object에 대한 motion check?
    def motion_check(self, motion_type, object_1, object_2):
        if self.unity == True:
            try:
                rospy.wait_for_service("motion_check")
                motion_check_client = rospy.ServiceProxy("motion_check", MotionCheck)
                motion_check_req = MotionCheckRequest()
                motion_check_req.motion_type = motion_type
                motion_check_req.object_1 = object_1
                motion_check_req.object_2 = object_2

                motion_check_res = motion_check_client(motion_check_req)

                if motion_check_res.execute_state == 1:
                    rospy.loginfo("Motion Type Interaction Completed")
                else:
                    rospy.loginfo("[Unity Error] Motion Type Interaction Failed")
            except Exception as e:
                rospy.logerr(e)
        
        elif self.unity == False:
            pass

    # def execution_check(self):
    #     if self.unity == True:
    #         try:
    #             rospy.Subscriber("execution_check", ExecutionCheck, pressEnter)
    #             rospy.spin()
    #         except Exception as e:
    #             rospy.logerr(e)
        
    #     elif self.unity == False:
    #         pass

    # def pressEnter(self, msg):
    #     if msg.status:
    #         pyautogui.press('enter')
    ## Unity - ROS Communication Method End ##


    
    #place를 입력으로 받으면 category에 따른 area를 return
    def _match_place_to_area(self, place, obj_category):
        if place == 'table':
            if obj_category == 'ingredient':
                area = 'table1_ingredient_area'
            elif obj_category == 'ing_bottle':
                area = 'table1_ing_bottle_area'
            elif obj_category == 'cookware':
                area = 'table1_cookware_area'
            elif obj_category == 'dishware':
                area = 'table1_dishware_area'
            elif obj_category == 'tool':
                area = 'table1_tool_area'
        elif place == 'stove':
            if obj_category == 'cookware':
                area = 'stove_cookware_area'
        elif place == 'cutting_board':
            if obj_category == 'ingredient':
                area = 'cutting_board_ingredient_area'
        elif place == 'near_cutting_board':
            if obj_category == 'dishware':
                area = 'near_cutting_board_bowl_area'
        return area



    #change place pose states to symbolic state
    def _to_symbolic_state(self, place_pose_state, obj_list):
        symbolic_state = {}

        # holding
        holding_obj = copy.deepcopy(self.objects['attached'])
        if len(holding_obj) > 1:
            AssertionError("more than one holding obj")
        if holding_obj:
            symbolic_state['holding'] = holding_obj[0]

        # in, on, is_near
        for key, val in place_pose_state.items():
            if val:
                # rename for task planner
                re_val = copy.deepcopy(val)
                for i in range(len(val)):
                    # chopped obj
                    if val[i][:8] == 'chopped_':
                        re_val[i] = val[i][8:]
                    # poured obj
                    elif val[i][-2:] in ['_1', '_2', '_3']:
                        re_val[i] = val[i][:-2]
                        
                # symbolic state for bowl, pot, pan, plate
                if self.instance_type[re_val[0]] in ['bowl', 'pot', 'plate', 'pan']:
                    container = self.instance_type[re_val[0]]                    
                    # for container
                    if key in self.place_area_poses['near_cutting_board_bowl_area']:
                        symbolic_state[re_val[0]+'_is_on'] = 'near_cutting_board'
                    else:
                        symbolic_state[re_val[0]+'_is_on'] = self.placement_yaml[key]['type']
                    # for object in/on container
                    if container in ['bowl', 'pot']:
                        for i in range(1, len(val)):
                            symbolic_state[re_val[i]+'_is_in'] = re_val[0]
                    elif container in ['plate', 'pan']:
                        for i in range(1, len(re_val)):
                            symbolic_state[re_val[i]+'_is_on'] = re_val[i-1]
                
                # symbolic state for etc(sandwich)
                else:
                    symbolic_state[re_val[0]+'_is_on'] = self.placement_yaml[key]['type']
                    for i in range(1, len(re_val)):
                        symbolic_state[re_val[i]+'_is_on'] = re_val[i-1]
                    
        return symbolic_state



    def get_current_state(self): #현재 사용?
        place_pose_state, obj_list = self._update_place_pose_state()
        current_state = self._to_symbolic_state(place_pose_state, obj_list)

        return current_state


    #함수 안 함수
    def run(self, action):
        #marker 함수
        def marker_msg(action):
            marker_ = Marker()
            marker_.header.frame_id = "/table1"
            marker_.header.stamp = rospy.Time.now()
            marker_.type = marker_.TEXT_VIEW_FACING
            marker_.action = marker_.ADD
            marker_.text = str(action)
            marker_.pose.position.x = 0
            marker_.pose.position.y = 0
            marker_.pose.position.z = 0.8
            marker_.pose.orientation.x = 0
            marker_.pose.orientation.y = 0
            marker_.pose.orientation.z = 0
            marker_.pose.orientation.w = 1
            marker_.scale.x = 0.1
            marker_.scale.y = 0.1
            marker_.scale.z = 0.1

            marker_.color.r = 1
            marker_.color.g = 1
            marker_.color.b = 1
            marker_.color.a = 1
            return marker_
        self.marker_pub.publish(marker_msg(action))
        
        # Run each action
        success = False
        ola_info = dict() 
        if action[0] == 'PickUp':#
            success, mp_infos = self.pick_up(action[1])
            ola_info['length'] = 4
        elif action[0] == 'Place':#
            success, mp_infos = self.place(action[1], action[2], action[3])
            ola_info['length'] = 4
        elif action[0] == 'Pour':#
            success, mp_infos = self.pour(action[1], action[2], action[3])
            ola_info['length'] = 3
        elif action[0] == 'PutOn':#
            success, mp_infos = self.put_on(action[1], action[2], action[3])
            ola_info['length'] = 4
        elif action[0] == 'Chop':#
            success, mp_infos = self.chop(action[1]) ## tool
            ola_info['length'] = 6
        elif action[0] == 'Spread':#
            success, mp_infos = self.spread(action[1], action[2]) ## tool
            ola_info['length'] = 6
        elif action[0] == 'Stir':#
            success, mp_infos = self.stir(action[1], action[2]) ## tool
            ola_info['length'] = 7
        elif action[0] == 'Scoop':#
            success, mp_infos = self.scoop(action[1], action[2]) ## obj_to, tool
            ola_info['length'] = 7
        elif action[0] == 'Scrape':#
            success, mp_infos = self.scrape(action[1], action[2]) ## obj_to, tool
            ola_info['length'] = 5
        elif action[0] == 'Activate':#
            success, mp_infos = self.activate(action[1], action[2])
            ola_info['length'] = 0
        else:
            AssertionError("action name is wrong")
        
        # Save info
        # ola_info['action'] = action
        # ola_info['success'] = success
        # ola_info['mp_infos'] = mp_infos
        
        return success, ola_info

    ### Object Level Motion Method Start ###
    def place_to_pose(self, obj, obj_to_pose):
        obj_type = self.instance_type[obj]

        mp_infos = [] #정보들

        # Parameter
        pre_dist = 0.1
        if 'place_pos' in self.obj_pose_yaml[obj_type].keys(): #knife,...
            place_pos = self.obj_pose_yaml[obj_type]['place_pos'] #그 값을 가져옴
        else: #thickness에서 가져옴?
            place_pos = [0, 0, -self.obj_stl_yaml[obj_type]['thickness'][0]-0.001]
        #rpy_to_quaternion_list에서 orient를 가져옴 & grasp_pose & pose도 가져옴
        place_orient = utils.rpy_to_quaternion_list(self.obj_pose_yaml[obj_type]['place_orient'])
        grasp_pose = self.obj_pose_yaml[obj_type]['grasp_pose']
        placement_pose = self.placement_yaml[obj_to_pose]['pose']

        # Move to pre place pose
        pre_dist_pose = [0, 0, pre_dist, 0, 0, 0, 1] #up
        place_pose = place_pos + place_orient 
        place_pose_inv = utils.inv_trans_mat(place_pose) # inv_trans_mat을 이용하여 값을 변경
        pre_pose = utils.concatenate_to_pose(pre_dist_pose, placement_pose, place_pose_inv, grasp_pose) #concatenate_to_pose를 이용하여 pre_pose를 가져옴
        temp_plan, mp_info = self.move_to(pre_pose, False) #위의 구한 pre_pose를 이용하여 move
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Place
        temp_plan, mp_info = self.linear_motion([0, 0, -pre_dist], True)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Get object hierarchy
        obj_hierarchy = copy.deepcopy(self.objects['attached'])
        rospy.loginfo(obj_hierarchy)

        # Release object
        _, mp_info = self.release_object(obj_hierarchy)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.hand_sync(obj, 0.4)
        # self.hand_sync(obj_hierarchy[0], 0.4)
        # Motion Check Service Request
        self.motion_check("Place", [obj], ["None"])
        self.scene_sync()

        # Change object state
        for obj in obj_hierarchy:
            self.objects['activated'].append(obj)
            self.objects['attached'].remove(obj)

        # Post-place pose
        temp_plan, mp_info = self.linear_motion([0, 0, -pre_dist], True, "eef")
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        return True, mp_infos
    #다음 3개의 값을 input으로 받음
    def place(self, obj, obj_to, obj_category):
        obj_to_area = self._match_place_to_area(obj_to, obj_category)
        #place할 pose를 선택
        scp = self._select_pose_from_area(obj, obj_to_area)
        if scp:
            success, mp_infos = self.place_to_pose(obj, scp)
            return True and success, mp_infos
        else:
            return False, []



    def pick_up(self, obj):
        #obj_type을 가져옴
        obj_type = self.instance_type[obj]

        mp_infos = []
        
        # Parameter
        # 다음 4개의 parameter를 초기에 설정
        pre_dist = 0.1 # down
        post_dist = 0.1 # up
        #gripper size와 grasp할 위치를 가져옴
        grasp_size = self.obj_pose_yaml[obj_type]['grasp_size']
        grasp_pose = self.obj_pose_yaml[obj_type]['grasp_pose']
        
        # Move to pre-grasp pose
        obj_pose = self.get_object_pose(obj) #inv 필요x
        pre_dist_pose = [0, 0, -pre_dist, 0, 0, 0, 1] #[0,0,-0.1,0,0,0,1]
        #pre-pick_up motion
        pre_pose = utils.concatenate_to_pose(obj_pose, grasp_pose, pre_dist_pose) #obj위치 + gripper위치 + 초기위치
        temp_plan, mp_info = self.move_to(pre_pose, False)
        mp_infos.append(mp_info)

        if not mp_info['success']:
            return False, mp_infos
        # Service request to Unity
        # Unity에 적용
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Move to grasp pose
        # end-effector를 조절
        temp_plan, mp_info = self.linear_motion([0, 0, pre_dist], True, "eef") #eef를 사용하여 아래로 더 내려감
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()
        
        # Get object hierarchy
        # 이 부분 check
        obj_hierarchy = [obj] #object가 들어있는 list로 만든다? => 여러 obj handle
        if obj in self.contain_objects.keys(): #put_on과 같은 motion에서 추가됨
            obj_hierarchy += copy.deepcopy(self.contain_objects[obj])
        rospy.loginfo("obj_hierarchy = {}".format(obj_hierarchy))
        
        # Grasp target object
        # 위에서 구한 obj_hierarchy를 hold
        _, mp_info = self.hold_object(obj_hierarchy, grasp_size)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.hand_sync(obj, grasp_size)

        # Change object state
        for obj in obj_hierarchy: #obj_hierarchy에 대해서
            #activated는 제거 attached는 추가
            self.objects['activated'].remove(obj)
            self.objects['attached'].append(obj) 

        # Move to post-grasp pose
        temp_plan, mp_info = self.linear_motion([0, 0, post_dist], True) #다시 올라옴 check
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()
        
        #최종적으로 mp_infos를 결과값으로 받음
        return True, mp_infos

    
    

    # obj를 target obj에 올리기
    def put_on(self, obj, obj_to, new_obj='None'):
        obj_type = self.instance_type[obj] #attached object
        obj_to_type = self.instance_type[obj_to] #target object to put attached object on

        mp_infos = []

        # Parameter
        # obj에 대해서 
        pre_dist = 0.05
        place_pose = self._make_place_pose(obj_type)
        grasp_pose = self.obj_pose_yaml[obj_type]['grasp_pose']
        # puton_pos = [0, 0, self.obj_stl_yaml[obj_to_type]['thickness'][1]]
        #target object에 대해서
        if 'puton_dist' in self.obj_pose_yaml[obj_to_type].keys(): #bowl,plate,pan
            puton_dist = self.obj_pose_yaml[obj_to_type]['puton_dist'] 
        else:
            puton_dist = self.obj_stl_yaml[obj_to_type]['thickness'][1] #thickness의 1번째 원소

        # Move to pre put on pose
        pre_dist_pose = [0, 0, pre_dist, 0, 0, 0, 1]
        puton_pose = self.get_object_pose(obj_to) #target obj의 위치값
        puton_pose.position.z += puton_dist #앞에 구한 puton_dist를 현재 pose의 z축으로 더해줌 
        puton_pose.orientation = Quaternion(0, 0, 0, 1)
        place_pose_inv = utils.inv_trans_mat(place_pose) #place_pose의 inv형태를 불러옴    
        pre_pose = utils.concatenate_to_pose(pre_dist_pose, puton_pose, place_pose_inv, grasp_pose)
        temp_plan, mp_info = self.move_to(pre_pose, False) #pre_pose를 위와같이 설정하고 move
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Puton
        temp_plan, mp_info = self.linear_motion([0, 0, -pre_dist], True) #down
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos                
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Get object hierarchy
        obj_hierarchy = copy.deepcopy(self.objects['attached']) #attached object의 hierarchy를 가져옴
        
        # Release object
        _, mp_info = self.release_object(obj_hierarchy)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.hand_sync(obj, 0.4) #unity에 보낼때는 hand size를 0.4로 해서 보냄

        # Drop object
        if obj_to_type == 'bowl' and (not self.unity): #unity가 False 일때 
            obj_to_pose = utils.add(pose_to_list(self.get_object_pose(obj_to)), [0, 0, 0.02, 0, 0, 0, 0]) #현재 obj_pose에서 z축으로 0.02만큼 up
            obj_mesh = STL_PATH+self.obj_stl_yaml[obj_type]['file_name']
            obj_size = self.obj_stl_yaml[obj_type]['scale']
            self.add_object(obj, obj_to_pose, obj_mesh, obj_size) #obj추가

        # Change object state
        for obj in obj_hierarchy:
            #attached -> activated
            self.objects['activated'].append(obj)
            self.objects['attached'].remove(obj)
        
        # Motion Check Service Request
        self.motion_check("PutOn", [obj], [obj_to]) 
        self.scene_sync()

        # Reassign self.contains_objects
        # check
        place_pose_state, _ = self._update_place_pose_state()
        self.contain_objects = dict()
        for key, val in place_pose_state.items():
            if val and (self.instance_type[val[0]] in ['bowl', 'pot', 'plate', 'pan']):
                self.contain_objects[val[0]] = val[1:]
        rospy.loginfo(self.contain_objects)
        # Recover to original pose
        temp_plan, mp_info = self.linear_motion([0, 0, pre_dist], True) #up
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos
        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Only for Tuna Sandwich
        # new_obj에 Tuna Sandwich가 들어오면
        if (new_obj != 'None') and ('sandwich' in self.objects['deactivated']): #deactivated인 sandwich에 대해서 
            # Delete objects
            del_objects = []
            rospy.loginfo("*****************")
            # rospy.loginfo(place_pose_state)
            for key, val in place_pose_state.items():
                rospy.loginfo('{} : {}'.format(key, val))
                if val and (val[-1] == obj):
                    del_objects = val
                    rospy.loginfo('del_objects = {}'.format(val))
            
            new_obj_pose = pose_to_list(self.get_object_pose(new_obj))
            obj_to_pose = pose_to_list(self.get_object_pose(obj_to))
            #어떻게 delete?
            for dobj in del_objects:
                dobj_type = self.instance_type[dobj]
                dobj_mesh = STL_PATH+self.obj_stl_yaml[dobj_type]['file_name']
                dobj_size = self.obj_stl_yaml[dobj_type]['scale']
                self.add_object(dobj, new_obj_pose, dobj_mesh, dobj_size)

            # Add new object
            new_obj_type = self.instance_type[new_obj]
            obj_to_pose[2] = 0.4 + self.obj_stl_yaml[new_obj_type]['thickness'][0]
            new_obj_mesh = STL_PATH+self.obj_stl_yaml[new_obj_type]['file_name']
            new_obj_size = self.obj_stl_yaml[new_obj_type]['scale']
            self.add_object(new_obj, obj_to_pose, new_obj_mesh, new_obj_size)
            self.motion_check("Sandwich", ["None"], ["None"])
            
            # Change object state
            # del obj는 deactivated & new obj는 activated
            for dobj in del_objects:
                self.objects['activated'].remove(dobj)
                self.objects['deactivated'].append(dobj)
            self.objects['deactivated'].remove(new_obj)
            self.objects['activated'].append(new_obj)
            self.scene_sync()
            
        return True, mp_infos

    def pour(self, obj, obj_to, new_obj):
        obj_type = self.instance_type[obj]
        obj_to_type = self.instance_type[obj_to]

        mp_infos = []
        
        # Parameter
        # import math as m
        pour_angle = -2*m.pi/5 #-72 degree
        #pour_pos check 왜 이렇게 pose값?
        pour_pos = [0, -self.obj_stl_yaml[obj_type]['thickness'][1], sum(self.obj_stl_yaml[obj_to_type]['thickness']) + 0.1] 

        # Move to obj_to
        # obj_pose에 위에구한 pour_pos값을 더해줌
        pre_pose = self.get_object_pose(obj_to)
        pre_pose.position.x += pour_pos[0]
        pre_pose.position.y += pour_pos[1]
        pre_pose.position.z += pour_pos[2]
        pre_pose.orientation = self.get_cur_pose().orientation #orientation은 현재 pose로
        temp_plan, mp_info = self.move_to(pre_pose, True) #pour할 위치로 이동
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos                
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()
        
        # Pour
        pour_angle_pose = utils.list_to_pose([0, 0, 0, 0, 0, pour_angle]) #list마지막 원소에 pour_angle대입
        pour_pose = utils.concatenate_to_pose(pre_pose, pour_angle_pose) 
        temp_plan, mp_info = self.move_to(pour_pose, False) #-72 degree만큼 회전
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()
        
        # Get pour_obj name
        self.num_of_pour[obj] += 1 #항상 1?
        pour_obj = new_obj + '_' + str(self.num_of_pour[obj]) #ex)olive_oil_1
        pour_obj_type = self.instance_type[pour_obj] #ex) olive_oil
        rospy.loginfo(pour_obj)

        # Add pour_obj
        # if not self.unity:
        #     if obj_to == 'bowl':
        #         obj_to_pose = utils.add(pose_to_list(self.get_object_pose(obj_to)), [0, 0, 0.02, 0, 0, 0, 0])
        #     else:
        #         obj_to_pose = utils.add(pose_to_list(self.get_object_pose(obj_to)), [0, 0, 0.01, 0, 0, 0, 0])
        #     pour_obj_mesh = STL_PATH+self.obj_stl_yaml[pour_obj_type]['file_name']
        #     pour_obj_size = self.obj_stl_yaml[pour_obj_type]['scale']
        #     self.add_object(pour_obj, obj_to_pose, pour_obj_mesh, pour_obj_size)
        if not self.unity: #unity를 사용하지 않으면 
            if obj_to == 'bowl':
                obj_to_pose = utils.add(pose_to_list(self.get_object_pose(obj_to)), [0, 0, 0.02, 0, 0, 0, 0])
                pour_obj_mesh = STL_PATH+self.obj_stl_yaml[pour_obj_type]['file_name']
                pour_obj_size = self.obj_stl_yaml[pour_obj_type]['scale']
                self.add_object(pour_obj, obj_to_pose, pour_obj_mesh, pour_obj_size)

        if obj_to == 'bowl':
            # Change object state
            # pour object: deactivated -> activated
            self.objects['activated'].append(pour_obj)
            self.objects['deactivated'].remove(pour_obj)

        # Motion Check Service Request
        self.motion_check("Pour", [new_obj, pour_obj], [obj_to])
        self.scene_sync()

        # Reassign self.contains_objects
        # check
        rospy.loginfo("reassign")
        time.sleep(0.7)
        place_pose_state, _ = self._update_place_pose_state()
        self.contain_objects = dict()
        for key, val in place_pose_state.items():
            if val and (self.instance_type[val[0]] in ['bowl', 'pot', 'plate', 'pan']):
                self.contain_objects[val[0]] = val[1:]
        rospy.loginfo(self.contain_objects)

        # Recover pose
        temp_plan, mp_info = self.move_to(pre_pose, False) #원래pose로 이동
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        return True, mp_infos

    def chop(self, obj, chop_num=2):
        obj_type = self.instance_type[obj]
        cobj_type = 'chopped_'+obj_type #파일 이름이 chopped_로 시작

        mp_infos = []

        # Parameter
        pre_dist = 0.1
        use_orient = utils.rpy_to_quaternion(self.obj_pose_yaml['knife']['use_orient']) #knife의 orient값을 가져와서 quaternion으로 변경
        chop_pos = [0, 0, self.obj_stl_yaml[obj_type]['thickness'][1]]  #obj thickness의 1번째 원소를 가져옴 
        cut_size = sum(self.obj_stl_yaml[obj_type]['thickness']) #thickness의 합을 cut_size로

        # Change link
        self.move_group.clear_pose_target('ee_link')
        self.move_group.set_end_effector_link('_link_knife')
        

        # Change to using pose
        # 사용할 도구의 pose로 변경
        initial_pose = self.get_cur_pose() #현재 pose를 가져옴
        use_pose = copy.deepcopy(initial_pose)
        use_pose.orientation = use_orient #orient는 도구의 orient를 가져옴
        temp_plan, mp_info = self.move_to(use_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()
        
        # Move to obj
        pre_dist_pose = [0, 0, pre_dist, 0, 0, 0, 1] #up
        chop_pose = self.get_object_pose(obj) #현재 obj의 pose
        #위의 정의한 chop_pos parameter값들을 가져옴  
        chop_pose.position.x += chop_pos[0] 
        chop_pose.position.y += chop_pos[1]
        chop_pose.position.z += chop_pos[2]
        chop_pose.orientation = use_orient
        
        #obj의 위로 이동
        tar_pose = utils.concatenate_to_pose(pre_dist_pose, chop_pose)
        temp_plan, mp_info = self.move_to(tar_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Pre-cutting(한번 cutting 실행)
        temp_plan, mp_info = self.linear_motion([0, 0, -pre_dist], True)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        # Motion Check Service Request
        self.motion_check("Before_Chop", [obj], ["None"])
        self.scene_sync()

        # Cutting
        for i in range(chop_num):        
            #cut_size는 위에 정의함
            temp_plan, mp_info = self.reciprocating_motion('Z', cut_size, False) #chop을 하기 위해서 collision을 false?
            mp_infos.append(mp_info)
            if not mp_info['success']:
                return False, mp_infos
            # Service request to Unity
            self.panda_plan(temp_plan)
        
        ### TEMP ###
        # self.add_object()
        # self.update_object_pose()

        # Change object pose 
        # obj => chopped_obj
            # obj_pose = utils.add(pose_to_list(self.get_object_pose(obj)), [0, 0, -0.01, 0, 0, 0, 0])
            # obj_pose = utils.add(pose_to_list(self.get_object_pose(obj))[:3], [0, 0, -0.01])+[0, 0, 0, 1]
        obj_pose = pose_to_list(self.get_object_pose(obj)) #obj의 현재 pose를 가져옴
        #obj_pose z값을 cobj_type으로 변경
        obj_pose[2] -= self.obj_stl_yaml[obj_type]['thickness'][0]
        obj_pose[2] += self.obj_stl_yaml[cobj_type]['thickness'][0]
        obj_pose = obj_pose[:3] + [0, 0, 0, 1] 
        obj_mesh = STL_PATH + self.obj_stl_yaml[obj_type]['file_name']
        obj_size = self.obj_stl_yaml[obj_type]['scale']

        cobj_pose = pose_to_list(self.get_object_pose('chopped_'+obj))
        cobj_mesh = STL_PATH + self.obj_stl_yaml[cobj_type]['file_name']
        cobj_size = self.obj_stl_yaml[cobj_type]['scale']

        #왜 같이??
        self.add_object(obj, cobj_pose, obj_mesh, obj_size)
        self.add_object('chopped_'+obj, obj_pose, cobj_mesh, cobj_size)

        # Change object state
        # obj -> deactivated , chopped_obj -> activated
        self.objects['activated'].remove(obj)
        self.objects['deactivated'].append(obj)
        self.objects['activated'].append('chopped_'+obj)
        self.objects['deactivated'].remove('chopped_'+obj)

        # Motion Check Service Request        
        self.motion_check("After_Chop", [obj], ["chopped_"+obj])
        self.scene_sync()

        # Recover orientation
        recover_pose = self.get_cur_pose()
        recover_pose.orientation = initial_pose.orientation
        temp_plan, mp_info = self.move_to(recover_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Recover link
        self.move_group.clear_pose_target('_link_knife')
        self.move_group.set_end_effector_link('ee_link')

        return True, mp_infos


    #obj:butter / obj_to:bread
    def spread(self, obj, obj_to):
        obj_type = self.instance_type[obj]
        obj_to_type = self.instance_type[obj_to]

        mp_infos = []

        # Parameter
        pre_dist = 0.2
        use_orient = utils.rpy_to_quaternion(self.obj_pose_yaml['spreader']['use_orient']) #spreader사용
        spread_dist = 0.04  #y축 방향으로 이동
        spread_pos = [0, -spread_dist/2, self.obj_stl_yaml[obj_to_type]['thickness'][1]] 

        # Change link
        self.move_group.clear_pose_target('ee_link')
        self.move_group.set_end_effector_link('_link_spreader')
        
        # Change to using pose
        initial_pose = self.get_cur_pose()
        use_pose = copy.deepcopy(initial_pose)
        use_pose.orientation = use_orient #도구의 orientation
        temp_plan, mp_info = self.move_to(use_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Move to obj
        tar_pose = self.get_object_pose(obj)
        tar_pose.position.z += (self.obj_stl_yaml[obj]['thickness'][1] + 0.1)
        tar_pose.orientation = use_orient
        temp_plan, mp_info = self.move_to(tar_pose, False) #target pose 위로 이동
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Ready to spread
        temp_plan, mp_info = self.reciprocating_motion("Z", 0.08) #down
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()
        
        # Move to obj_to
        # tar_obj로 이동
        pre_dist_pose = [0, 0, pre_dist, 0, 0, 0, 1]
        spread_pose = self.get_object_pose(obj_to)
        #위에서 구한 spread_pos를 더해줌
        spread_pose.position.x += spread_pos[0]
        spread_pose.position.y += spread_pos[1]
        spread_pose.position.z += spread_pos[2]
        spread_pose.orientation = use_orient
        pre_pose = utils.concatenate_to_pose(pre_dist_pose, spread_pose)
        temp_plan, mp_info = self.move_to(pre_pose, True)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Spread
        temp_plan, mp_info = self.linear_motion([0, 0, -pre_dist], True) #z축 방향 down
        mp_infos.append(mp_info) 
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        # Motion Check Service Request  
        # self.motion_check("Before_Spread", [obj], ["None"])
        self.scene_sync()

        temp_plan, mp_info = self.linear_motion([0, spread_dist, 0], False) #y축 방향
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        # Motion Check Service Request  
        # self.motion_check("After_Spread", [obj], ["spread_"+obj])
        self.scene_sync()

        temp_plan, mp_info = self.linear_motion([0, 0, pre_dist], False) #up
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos    
        # Service request to Unity
        self.panda_plan(temp_plan)

        ### TEMP ###
        # self.add_object()
        # self.update_object_pose()

        # Change object pose
        # if not self.unity:
        # obj_pose = pose_to_list(self.get_object_pose(obj))
        # obj_mesh = STL_PATH + self.obj_stl_yaml[obj_type]['file_name']
        # obj_size = self.obj_stl_yaml[obj_type]['scale']

        # cobj_type = 'spread_'+obj_type
        # cobj_pose = pose_to_list(self.get_object_pose('spread_'+obj))
        # cobj_mesh = STL_PATH + self.obj_stl_yaml[cobj_type]['file_name']
        # cobj_size = self.obj_stl_yaml[cobj_type]['scale']

        # self.add_object(obj, cobj_pose, obj_mesh, obj_size)
        # self.add_object("spread_"+obj, obj_pose, cobj_mesh, cobj_size)

        # Change object state
        # self.objects['activated'].remove(obj)
        # self.objects['deactivated'].append(obj)
        # self.objects['activated'].append('spread_'+obj)
        # self.objects['deactivated'].remove('spread_'+obj)

        # Recover orientation
        # 초기에 설정한 orientation으로 변경
        recover_pose = self.get_cur_pose()
        recover_pose.orientation = initial_pose.orientation
        temp_plan, mp_info = self.move_to(recover_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()
        
        # Recover link
        
        self.move_group.clear_pose_target('_link_spreader')
        self.move_group.set_end_effector_link('ee_link')

        return True, mp_infos

    def stir(self, obj, new_obj, stir_num=2):
        obj_type = self.instance_type[obj]

        mp_infos = []

        # Parameter
        # spatula로만 사용
        pre_dist = 0.05
        use_orient = utils.rpy_to_quaternion(self.obj_pose_yaml['spatula']['use_orient'])
        stir_r = 0.05
        stir_pos = [0, 0, self.obj_stl_yaml['bowl']['thickness'][1]-0.02]

        # Change link
        self.move_group.clear_pose_target('ee_link')
        self.move_group.set_end_effector_link('_link_spatula')

        # Change to using pose
        initial_pose = self.get_cur_pose()
        use_pose = copy.deepcopy(initial_pose)
        use_pose.orientation = use_orient
        temp_plan, mp_info = self.move_to(use_pose, False) #orientaion만 도구에서 가져옴
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Move to obj
        stir_pose = self.get_object_pose(obj)
        stir_pose.position.x += stir_pos[0]
        stir_pose.position.y += stir_pos[1]
        stir_pose.position.z += stir_pos[2]
        stir_pose.orientation = use_orient
        pre_dist_pose = [0, 0, pre_dist, 0, 0, 0, 1]
        pre_pose = utils.concatenate_to_pose(pre_dist_pose, stir_pose) #up
        temp_plan, mp_info = self.move_to(pre_pose, True)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Stir
        temp_plan, mp_info = self.linear_motion([0, 0, -pre_dist], True) #down
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        for i in range(stir_num):
            temp_plan, mp_info = self.circular_motion('Z', 'CW', stir_r, 0, 360, False)
            mp_infos.append(mp_info)
            if not mp_info['success']:
                return False, mp_infos
            # Service request to Unity
            self.panda_plan(temp_plan)

        ### TEMP ###
        # self.add_object()
        # self.update_object_pose()

        # Change object pose
        # if not self.unity:
        if new_obj in self.objects['deactivated']: #deactivated인 new_obj에대해서
            obj_pose = utils.add(pose_to_list(self.get_object_pose(obj)), [0, 0, 0.02, 0, 0, 0, 0])
            nobj_type = self.instance_type[new_obj]
            nobj_mesh = STL_PATH + self.obj_stl_yaml[nobj_type]['file_name']
            nobj_size = self.obj_stl_yaml[nobj_type]['scale']
            self.add_object(new_obj, obj_pose, nobj_mesh, nobj_size)

            for dobj in self.contain_objects[obj]: #현재 contaion하는 obj
                dobj_type = self.instance_type[dobj]
                dobj_pose = [0, 4, 4, 0, 0, 0, 1]
                dobj_mesh = STL_PATH + self.obj_stl_yaml[dobj_type]['file_name']
                dobj_size = self.obj_stl_yaml[dobj_type]['scale']
                self.add_object(dobj, dobj_pose, dobj_mesh, dobj_size)
            
            # Change object state
            for cobj in self.contain_objects[obj]:
                self.objects['activated'].remove(cobj)
                self.objects['deactivated'].append(cobj)
            self.objects['activated'].append(new_obj)
            self.objects['deactivated'].remove(new_obj)

            # Motion Check Service Request
            self.motion_check("Stir", self.contain_objects[obj], [new_obj])
        self.scene_sync()

        # Recover pose
        temp_plan, mp_info = self.linear_motion([0, 0, pre_dist], True)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Recover orientation
        recover_pose = self.get_cur_pose()
        recover_pose.orientation = initial_pose.orientation
        temp_plan, mp_info = self.move_to(recover_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Recover link
        self.move_group.clear_pose_target('_link_spatula')
        self.move_group.set_end_effector_link('ee_link')

        return True, mp_infos

    def scoop(self, obj, obj_to):
        obj_type = self.instance_type[obj]
        obj_to_type = self.instance_type[obj_to]
        
        mp_infos = []

        # Parameter
        use_orient = utils.rpy_to_quaternion(self.obj_pose_yaml['scooper']['use_orient'])
        #chopped된 obj인지 아닌지에 따라서 z값을 달리 가져옴\
        #chopped->cutting_board위에 / 나머지는 -> bowl위에
        if "chopped" in obj:
            scoop_pos = [0, 0, self.obj_stl_yaml[obj_type]["thickness"][1]+0.1]
        else:
            scoop_pos = [0, 0, self.obj_stl_yaml['bowl']['thickness'][1]]
        scoop_r = 0.05 #사용하지 않음
        scoop_to_pos = [0, -0.025, self.obj_stl_yaml[obj_to_type]['thickness'][1]+0.1]
        scoop_to_angle = -1*m.pi/10 #-18 degree

        # Change link
        self.move_group.clear_pose_target('ee_link')
        self.move_group.set_end_effector_link('_link_scooper')

        # # Drop object (delete)
        # obj_pose = utils.pose_to_list(self.get_object_pose(obj))
        # obj_pose[2] -= 0.05
        # self.add_object(obj, obj_pose, STL_PATH+self.obj_stl_yaml[obj]['file_name'], self.obj_stl_yaml[obj_type]['scale'])

        # Change to using pose
        initial_pose = self.get_cur_pose()
        use_pose = copy.deepcopy(initial_pose)
        use_pose.orientation = use_orient #scooper의 orientation을 가져옴
        temp_plan, mp_info = self.move_to(use_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Move to obj
        scoop_pose = self.get_object_pose(obj)
        scoop_pose.orientation = self.get_cur_pose().orientation
        #scoop_pos의 값을 더해줌
        scoop_pose.position.x += scoop_pos[0]
        scoop_pose.position.y += scoop_pos[1]
        scoop_pose.position.z += scoop_pos[2]
        scoop_pose.orientation = use_orient
        temp_plan, mp_info = self.move_to(scoop_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.motion_check("Before_Scoop", [obj], ["None"])
        self.scene_sync()

        # Scoop
        # temp_plan, mp_info = self.circular_motion('Y', 'CW', scoop_r, 90, 180, False)
        # temp_plan, mp_info = self.linear_motion([0, 0, -0.1], True) ## ?
        # temp_plan, mp_info = self.reciprocating_motion('Z', 0.1, False)
        temp_plan, mp_info = self.linear_motion([0, 0, -0.1], True) #down
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        # Motion Check Service Request
        self.motion_check("After_Scoop", [obj], ["None"])
        self.scene_sync()
        # post-scoop
        temp_plan, mp_info = self.linear_motion([0, 0, 0.1], True) #up
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Move to obj_to
        pre_pose = self.get_object_pose(obj_to)
        #위에 구한 scoop_to_pos값을 더해줌
        pre_pose.position.x += scoop_to_pos[0]
        pre_pose.position.y += scoop_to_pos[1]
        pre_pose.position.z += scoop_to_pos[2]
        pre_pose.orientation = initial_pose.orientation
        temp_plan, mp_info = self.move_to(pre_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Scoop to
        scoop_to_angle_pose = utils.list_to_pose([0, 0, 0, 0, scoop_to_angle, 0]) #y축방향으로 회전
        scoop_to_pose = utils.concatenate_to_pose(pre_pose, scoop_to_angle_pose)
        temp_plan, mp_info = self.move_to(scoop_to_pose, False) #scoop
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)

        # Change object pose
        # unity를 사용하지 않는다면
        if not self.unity:
            obj_to_pose = utils.add(pose_to_list(self.get_object_pose(obj_to)), [0, 0, 0.015, 0, 0, 0, 0])
            obj_mesh = STL_PATH + self.obj_stl_yaml[obj_type]['file_name']
            obj_size = self.obj_stl_yaml[obj_type]['scale']
            self.add_object(obj, obj_to_pose, obj_mesh, obj_size)
        
        # Motion Check Service Request
        self.motion_check("ScoopOn", [obj], [obj_to])
        self.scene_sync()

        # pose와 orientation원상태로
        # Recover pose
        temp_plan, mp_info = self.move_to(pre_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Recover orientation
        recover_pose = self.get_cur_pose()
        recover_pose.orientation = initial_pose.orientation
        temp_plan, mp_info = self.move_to(recover_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()
        
        # Recover link
        self.move_group.clear_pose_target('_link_scooper')
        self.move_group.set_end_effector_link('ee_link')

        return True, mp_infos

    def scrape(self, obj, obj_to):
        obj_type = self.instance_type[obj]

        # Parameter
        pre_dist = 0.09
        use_orient = utils.rpy_to_quaternion(self.obj_pose_yaml['knife']['use_orient'])
        scrape_pos = [0, -0.04, 0] 
        scrape_to_pos = [0, 0, self.obj_stl_yaml['bowl']['thickness'][1]+0.03]

        mp_infos = []

        # Change link
        self.move_group.clear_pose_target('ee_link')
        self.move_group.set_end_effector_link('_link_knife')

        # Change to using pose
        # knife로 target pose변경
        initial_pose = self.get_cur_pose()
        use_pose = copy.deepcopy(initial_pose)
        use_pose.orientation = use_orient
        temp_plan, mp_info = self.move_to(use_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Move to start pose
        scrape_pose = self.get_object_pose(obj)
        scrape_pose.position.x += scrape_pos[0]
        scrape_pose.position.y += scrape_pos[1]
        scrape_pose.position.z += scrape_pos[2]
        scrape_pose.orientation = use_orient
        pre_dist_pose = [0, 0, pre_dist, 0, 0, 0, 1] #up
        pre_pose = utils.concatenate_to_pose(pre_dist_pose, scrape_pose)
        temp_plan, mp_info = self.move_to(pre_pose, True)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()

        # Scrape
        # temp_plan, mp_info = self.linear_motion('Z', -pre_dist, True)
        temp_plan, mp_info = self.linear_motion([0, 0, -pre_dist], True) #down
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos        
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.motion_check("Before_Scrape", [obj], ["None"])
        self.scene_sync()

        scrape_to_pose = self.get_object_pose(obj_to) #현재 bowl의 pose를 가져옴
        #knowledge에 저장된 bowl pose를 추가적으로 더해줌(z값)
        scrape_to_pose.position.x += scrape_to_pos[0] 
        scrape_to_pose.position.y += scrape_to_pos[1]
        scrape_to_pose.position.z += scrape_to_pos[2]
        scrape_to_pose.orientation = use_orient
        #현재 bowl pose - concacenated한 pose
        #z값은 위에서 이미 적용
        dist_x = scrape_to_pose.position.x - pre_pose.position.x
        dist_y = scrape_to_pose.position.y - pre_pose.position.y
        temp_plan, mp_info = self.linear_motion([dist_x, dist_y, 0], False)  # <TEMP> direction + or -
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos                
        # Service request to Unity
        self.panda_plan(temp_plan)

        # Change object pose
        if not self.unity:
            obj_to_pose = utils.add(pose_to_list(self.get_object_pose(obj_to)), [0, 0, 0.03, 0, 0, 0, 0])
            obj_mesh = STL_PATH + self.obj_stl_yaml[obj_type]['file_name']
            obj_size = self.obj_stl_yaml[obj_type]['scale']
            self.add_object(obj, obj_to_pose, obj_mesh, obj_size, "world")
        
        # Motion Check Service Request
        self.motion_check("After_Scrape", [obj], [obj_to])
        self.scene_sync()
        
        # Reassign self.contains_objects
        rospy.loginfo("reassign")
        time.sleep(0.7)
        place_pose_state, _ = self._update_place_pose_state()
        # rospy.loginfo(place_pose_state)
        self.contain_objects = dict()
        for key, val in place_pose_state.items():
            if val and (self.instance_type[val[0]] in ['bowl', 'pot', 'plate', 'pan']):
                self.contain_objects[val[0]] = val[1:]
        rospy.loginfo(self.contain_objects)

        # Recover to initial orientation
        # 현재 pose로 돌아옴
        recover_pose = self.get_cur_pose()
        recover_pose.orientation = initial_pose.orientation
        temp_plan, mp_info = self.move_to(recover_pose, False)
        mp_infos.append(mp_info)
        if not mp_info['success']:
            return False, mp_infos                
        # Service request to Unity
        self.panda_plan(temp_plan)
        self.scene_sync()
        
        # Recover link
        self.move_group.clear_pose_target('_link_knife')
        self.move_group.set_end_effector_link('ee_link')

        return True, mp_infos

    def activate(self, obj, cooked_obj):
        # obj = 'stove'        
        rospy.loginfo('obj={}, cooked_obj={}'.format(obj, cooked_obj))
        self.motion_check("Activate", [cooked_obj], ["None"])

        ''' Not Assigned
        # Move to activate pose
        obj_pose = self.get_object_pose(obj)
        obj_mat = utils.pose_to_mat(obj_pose)
        
        rel_pose_list = self.obj_pose_yaml[obj]['activate_pose']
        rel_mat = utils.pose_list_to_mat(rel_pose_list)
        tar_mat = np.dot(obj_mat, rel_mat)
        tar_pose = utils.mat_to_pose(tar_mat)
        self.move_to(tar_pose, False)
        
        # Activate Request to Unity
        '''
        mp_infos = []
        return True, mp_infos

    def deactivate(self, obj):
        pass
    
def main():
    use_moveit = True
    use_unity = False

    # sample
    #sandwich = sample.club_sandwich
    sandwich = sample.carrot_salad
    # sandwich = sample.tuna_sandwich
    # sandwich = sample.greek_salad
    # sandwich = sample.shrimp_salad
    # sandwich = sample.test_15_predict3_v2
    # sandwich = sample.test_33_predict2_v2
    # sandwich = sample.test_49_predict2_v2
    # sandwich = sample.test_80_predict2_v2

    # # csv #여기서 
    # test_dir = dirname(dirname(__file__)) + '/test_set/default_v2/'
    # # test_dir = dirname(dirname(__file__)) + '/test_set/predict2_v2/'
    # # test_dir = dirname(dirname(__file__)) + '/test_set/predict3_v2/'
    # result_dir = dirname(dirname(__file__)) + '/result/default_v2/'
    # # result_dir = dirname(dirname(__file__)) + '/result/predict2_v2/'
    # # result_dir = dirname(dirname(__file__)) + '/result/predict3_v2/'
    # for target_dir in [test_dir, result_dir]:
    #     if not os.path.exists(target_dir):
    #         os.makedirs(target_dir)

    # test_path = test_dir + sandwich.test_file_name
    # #suffix = datetime.datetime.now().strftime("_%y%m%d_%H%M%S")
    # # tp_result_path = result_dir + sandwich.test_file_name[:-4] + suffix + '_tp.csv'
    # # ola_result_path = result_dir + sandwich.test_file_name[:-4] + suffix + '_ola.csv'
    # # mp_result_path = result_dir + sandwich.test_file_name[:-4] + suffix + '_mp.csv'


    
    # raw_input("Experiment Start!!")

    # initialize for motion planning
    if use_moveit:
        obj_test = ObjectLevelMotion(use_unity)
        obj_test.initialize(sandwich.obj_place) #recipe의 object_place를 가져옴
    total_action_sequences = []
    for result in sandwich.task_plan:
        action_sequences = [action.split('/') for action in result.split(" -> ") if action]
        total_action_sequences.append(action_sequences)
        #print(action_sequences)
    
    if use_moveit:
        # success = False
        
        for i, action in enumerate(total_action_sequences):
            print(i,action)
            obj_test.run(action)


    # obj_test.pick_up('mayonnaise_bottle')
    # obj_test.pour('mayonnaise_bottle','bread2','mayonnaise') #(self, obj, obj_to, new_obj) Pour/mayonnaise_bottle/bread2/mayonnaise
    # obj_test.place('onion','cutting_board','ingredient')
    # obj_test.pick_up('knife') 
    # obj_test.chop('onion')
    # #####
    # obj_test.place('knife','table','tool')
    # obj_test.pick_up('bowl')
    # obj_test.place('bowl','near_cutting_board','dishware')
    # obj_test.pick_up('knife')
    # obj_test.scrape('chopped_onion','bowl')
    # ####
    # obj_test.place('knife','table','tool')
    # obj_test.pick_up('cucumber')
    # obj_test.place('cucumber','cutting_board','ingredient')
    # obj_test.pick_up('knife')

    # obj_test.chop('cucumber')
    # obj_test.scrape('chopped_cucumber','bowl')
    # ####
    # obj_test.place('knife','table','tool')
    # obj_test.pick_up('sweet_pepper')
    # obj_test.place('sweet_pepper','cutting_board','ingredient') #pepper -> 고추
    # obj_test.pick_up('knife')
    # obj_test.chop('sweet_pepper')
    # ####
    # obj_test.place('knife','table','tool')
    # obj_test.pick_up('feta_cheese')
    # obj_test.place('feta_cheese','cutting_board','ingredient') 
    # obj_test.pick_up('knife')
    # obj_test.chop('feta_cheese')
    # obj_test.scrape('chopped_sweet_pepper','bowl')
    # obj_test.scrape('chopped_feta_cheese','bowl')
    # ####
    # obj_test.pick_up('black_olive')
    # obj_test.put_on('black_olive','bowl','None')
    # ####
    # obj_test.pick_up('tomato')
    # obj_test.place('tomato','cutting_board','ingredient')
    # obj_test.pick_up('knife')
    # obj_test.chop('tomato')
    # obj_test.scrape('chopped_tomato','bowl')
    # ####
    # obj_test.place('knife','table','tool')
    # obj_test.pick_up('potato')
    # obj_test.place('potato','cutting_board','ingredient')
    # obj_test.pick_up('knife')
    # obj_test.chop('potato')
    # obj_test.scrape('chopped_potato','bowl')
    # ####
    # obj_test.place('knife','table','tool')
    # obj_test.pick_up('spatula')
    # raw_input()
    # obj_test.stir('bowl','salad')

if __name__ == '__main__':
    main()