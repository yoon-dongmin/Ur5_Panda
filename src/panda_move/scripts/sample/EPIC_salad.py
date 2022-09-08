# -*- coding: utf-8 -*-
test_file_name = 'test_EPIC_salad_v2.csv'
###########################################################
# instance-type-state
obj_state = []

# container
obj_state.append(['pan', 'pan', None])
obj_state.append(['plate', 'plate', None])
obj_state.append(['bowl', 'bowl', None])

# tool
obj_state.append(['spatula', 'spatula', None])
obj_state.append(['spreader', 'spreader', None])
obj_state.append(['scooper', 'scooper', None])
obj_state.append(['knife', 'knife', None])

# place
obj_state.append(['table', 'table', None])
obj_state.append(['stove', 'stove', None])
obj_state.append(['cutting_board', 'cutting_board', None])
obj_state.append(['near_cutting_board', 'near_cutting_board', None])

# ingredient
obj_state.append(['cucumber', 'cucumber', ['exist']])
obj_state.append(['tomato', 'tomato', ['exist']])
obj_state.append(['cheese', 'cheese', ['exist']])

#obj_state.append(['relish', 'relish', ['exist']])
#obj_state.append(['lemon_juice', 'lemon_juice', ['exist']])
obj_state.append(['black_pepper', 'black_pepper', ['exist']])
obj_state.append(['olive_oil', 'olive_oil', ['exist']])
obj_state.append(['mayonnaise', 'mayonnaise', ['exist']])
obj_state.append(['salt', 'salt', ['exist']])
obj_state.append(['salad', 'salad', []])

# ingredient bottle
#obj_state.append(['relish_bottle', 'relish_bottle', None])
obj_state.append(['black_pepper_bottle', 'black_pepper_bottle', None])
obj_state.append(['olive_oil_bottle', 'olive_oil_bottle', None])
obj_state.append(['mayonnaise_bottle', 'mayonnaise_bottle', None])
obj_state.append(['salt_bottle', 'salt_bottle', None])


###########################################################
# instance-type-placement-state #list하나당 4개의 element를 가짐
obj_place = []

# fixed set
# obj_place.append(['pan', 'pan', 'table1_pan', 'activated'])
# obj_place.append(['pot', 'pot', 'table1_pot', 'activated'])
# obj_place.append(['plate', 'plate', 'table1_plate', 'activated'])
# obj_place.append(['bowl', 'bowl', 'table1_empty_4', 'activated'])
# obj_place.append(['spatula', 'spatula', 'table1_spatula', 'activated'])
# obj_place.append(['spreader', 'spreader', 'table1_spreader', 'activated'])
# obj_place.append(['scooper', 'scooper', 'table1_scooper', 'activated'])
# obj_place.append(['knife', 'knife', 'table1_knife', 'activated'])
# obj_place.append(['cutting_board', 'cutting_board', 'table1_cutting_board', None])

obj_place.append(['pan', 'pan', 'table1_cookware_area', 'activated'])
obj_place.append(['pot', 'pot', 'table1_cookware_area', 'activated'])
obj_place.append(['plate', 'plate', 'table1_dishware_area', 'activated'])
obj_place.append(['bowl', 'bowl', 'table1_dishware_area', 'activated'])
obj_place.append(['spatula', 'spatula', 'table1_tool_area', 'activated'])
obj_place.append(['spreader', 'spreader', 'table1_tool_area', 'activated'])
obj_place.append(['scooper', 'scooper', 'table1_tool_area', 'activated'])
obj_place.append(['knife', 'knife', 'table1_tool_area', 'activated'])
obj_place.append(['cutting_board', 'cutting_board', 'table1_cutting_board', None]) ##

# ingredeint set
# obj_place.append(['onion', 'onion', 'table1_ing_1', 'activated'])
# obj_place.append(['cucumber', 'cucumber', 'table1_ing_2', 'activated'])
# obj_place.append(['sweet_pepper', 'sweet_pepper', 'table1_ing_3', 'activated'])
# obj_place.append(['feta_cheese', 'feta_cheese', 'table1_ing_4', 'activated'])
# obj_place.append(['oregano', 'oregano', 'table1_ing_5', 'activated'])
# obj_place.append(['black_olive', 'black_olive', 'table1_ing_6', 'activated'])
# obj_place.append(['tomato', 'tomato', 'table1_ing_7', 'activated'])
# obj_place.append(['potato', 'potato', 'table1_ing_8', 'activated'])

# obj_state.append(['cucumber', 'cucumber', ['exist']])
# obj_state.append(['tomato', 'tomato', ['exist']])
# obj_state.append(['oregano', 'oregano', ['exist']])


obj_place.append(['tomato', 'tomato', 'table1_ingredient_area', 'activated'])
obj_place.append(['cucumber', 'cucumber', 'table1_ingredient_area', 'activated'])
obj_place.append(['cheese', 'cheese', 'table1_ingredient_area', 'activated'])
obj_place.append(['black_pepper_bottle', 'black_pepper_bottle', 'table1_ing_bottle_area', 'activated'])
obj_place.append(['olive_oil_bottle', 'olive_oil_bottle', 'table1_ing_bottle_area', 'activated'])
obj_place.append(['salt_bottle', 'salt_bottle', 'table1_ing_bottle_area', 'activated'])
obj_place.append(['mayonnaise_bottle', 'mayonnaise_bottle', 'table1_ing_bottle_area', 'activated'])
# for Chop
obj_place.append(['chopped_cucumber', 'chopped_cucumber', 'deactivate', 'deactivated'])
obj_place.append(['chopped_tomato', 'chopped_tomato', 'deactivate', 'deactivated'])
obj_place.append(['chopped_cheese', 'chopped_cheese', 'deactivate', 'deactivated'])
# for Spread

# for Pour
#obj_place.append(['relish_1', 'relish', 'deactivate', 'deactivated'])
obj_place.append(['black_pepper_1', 'black_pepper', 'deactivate', 'deactivated']) 
obj_place.append(['olive_oil_1', 'olive_oil', 'deactivate', 'deactivated'])
obj_place.append(['mayonnaise_1', 'mayonnaise', 'deactivate', 'deactivated'])
obj_place.append(['salt_1', 'salt', 'deactivate', 'deactivated'])





# for Stir
# obj_place.append(['salad', 'salad', 'deactivate', 'deactivated'])

###########################################################
# network_output -> goals, using_ings, recipe
goals = []
using_ings = []

goals.append({'cooked_bacon': True})
using_ings.append([{'bacon'}, {}])

recipe = {'sandwich' : ['bread1', 'ham', 'turkey', 'cheese', 'bread2', 'bacon', 'lettuce', 'tomato', 'bread3']}

network_output = (goals, using_ings, recipe)

###########################################################
# # task_plan
task_plan = []
task_plan.append(' -> PickUp/tomato -> Place/tomato/cutting_board/ingredient -> PickUp/knife -> Chop/tomato/knife')
task_plan.append(' -> Place/knife/table/tool -> PickUp/cucumber -> Place/cucumber/cutting_board/ingredient -> PickUp/knife -> Chop/cucumber/knife')
task_plan.append(' -> Place/knife/table/tool -> PickUp/cheese -> Place/cheese/cutting_board/ingredient -> PickUp/knife -> Chop/cheese/knife')
task_plan.append(' -> Scrape/chopped_cheese/bowl/knife')
task_plan.append(' -> Place/knife/table/tool -> PickUp/salt_bottle -> Pour/salt_bottle/bowl/salt')
task_plan.append(' -> Place/salt_bottle/table/ing_bottle -> PickUp/black_pepper_bottle -> Pour/black_pepper_bottle/bowl/black_pepper')
task_plan.append(' -> Place/black_pepper_bottle/table/ing_bottle -> PickUp/olive_oil_bottle -> Pour/olive_oil_bottle/bowl/olive_oil')
task_plan.append(' -> Place/olive_oil_bottle/table/ing_bottle -> PickUp/knife -> Scrape/chopped_cucumber/bowl/knife')
task_plan.append(' -> Place/knife/table/tool -> PickUp/mayonnaise_bottle -> PourIn/mayonnaise_bottle/bowl/mayonnaise')
task_plan.append(' -> Place/mayonnaise_bottle/table/ing_bottle -> PickUp/spatula -> Stir/bowl/salad/spatula')
# ###
# task_plan = []
# task_plan.append(' -> PickUp/apple -> Place/apple/cutting_board/ingredient -> PickUp/knife -> Chop/apple/knife')
# task_plan.append(' -> Place/knife/table/tool -> PickUp/cucumber -> Place/cucumber/cutting_board/ingredient -> PickUp/knife -> Chop/cucumber/knife')
# task_plan.append(' -> Place/knife/table/tool -> PickUp/cheddar -> Place/cheddar/cutting_board/ingredient -> PickUp/knife -> Chop/cheddar/knife')
# task_plan.append(' -> Scrape/chopped_cheddar/bowl/knife')
# task_plan.append(' -> Place/knife/table/tool -> PickUp/salt_bottle -> PourIn/salt_bottle/bowl/salt')
# task_plan.append(' -> Place/salt_bottle/table/ing_bottle -> PickUp/black_pepper_bottle -> PourIn/black_pepper_bottle/bowl/black_pepper')
# task_plan.append(' -> Place/black_pepper_bottle/table/ing_bottle -> PickUp/grapeseed_oil_bottle -> PourIn/grapeseed_oil_bottle/bowl/grapeseed_oil')
# task_plan.append(' -> Place/grapeseed_oil_bottle/table/ing_bottle -> PickUp/knife -> Scrape/chopped_cucumber/bowl/knife')
# task_plan.append(' -> Place/knife/table/tool -> PickUp/salad_dressing_bottle -> PourIn/salad_dressing_bottle/bowl/salad_dressing')
# task_plan.append(' -> Place/salad_dressing_bottle/table/ing_bottle -> PickUp/spatula -> Stir/bowl/salad/spatula')




if __name__ == '__main__':
    carrot_path = './carrot_mapping.yaml'
    with open(carrot_path) as f:
        carrot_map = yaml.load(f,Loader=yaml.FullLoader)



    total_action_sequences = []
    for result in task_plan:
        action_sequences = [action.split('/') for action in result.split(" -> ") if action]
        total_action_sequences.append(action_sequences)

    
        
    for action_sequences in total_action_sequences:



        for i, action in enumerate(action_sequences):
            #print(i, action)
            for obj in carrot_map.keys():
                if obj in action:
                    #print(obj,1111111)
                    idx = action.index(obj) #obj의 list idx를 찾음
                    print(action,11111)
                    action[idx]=carrot_map[obj] #carrot_map의 value값으로 변환
                    print(action,22222)
#########################################################
#action_sequences

# total_action_sequences = []
# for result in task_plan:
#     action_sequences = [action.split('/') for action in result.split(" -> ") if action]
#     #print(action_sequences,1)

#     total_action_sequences.append(action_sequences)

# for action_sequences in total_action_sequences:
#     for i, action in enumerate(action_sequences):
#         print(i, action)




    # for obj in self.carrot_map.keys():
    #     idx = obj_list.index(obj) #obj의 list idx를 찾음
    #     obj_list[idx]=self.carrot_map[obj] #carrot_map의 value값으로 변환
