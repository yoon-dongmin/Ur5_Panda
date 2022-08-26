# -*- coding: utf-8 -*-
###########################################################
test_file_name = 'test_carrot_salad_v2.csv'

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
obj_state.append(['banana', 'banana', ['exist']])
obj_state.append(['oregano', 'oregano', ['exist']])

obj_state.append(['relish', 'relish', ['exist']])
obj_state.append(['lemon_juice', 'lemon_juice', ['exist']])
obj_state.append(['olive_oil', 'olive_oil', ['exist']])
obj_state.append(['mayonnaise', 'mayonnaise', ['exist']])
obj_state.append(['sugar', 'sugar', ['exist']])
obj_state.append(['salad', 'salad', []])

# ingredient bottle
obj_state.append(['relish_bottle', 'relish_bottle', None])
obj_state.append(['lemon_juice_bottle', 'lemon_juice_bottle', None])
obj_state.append(['olive_oil_bottle', 'olive_oil_bottle', None])
obj_state.append(['mayonnaise_bottle', 'mayonnaise_bottle', None])
obj_state.append(['sugar_bottle', 'sugar_bottle', None])


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

obj_state.append(['cucumber', 'cucumber', ['exist']])
obj_state.append(['banana', 'banana', ['exist']])
obj_state.append(['oregano', 'oregano', ['exist']])


obj_place.append(['turkey', 'turkey', 'table1_ingredient_area', 'activated'])
obj_place.append(['walnut', 'walnut', 'table1_ingredient_area', 'activated'])
obj_place.append(['tuna', 'tuna', 'table1_ingredient_area', 'activated'])
obj_place.append(['potato', 'potato','table1_ingredient_area', 'activated'])
obj_place.append(['lettuce', 'lettuce', 'table1_ingredient_area', 'activated'])


# for Chop
obj_place.append(['chopped_cucumber', 'chopped_cucumber', 'deactivate', 'deactivated'])
obj_place.append(['chopped_banana', 'chopped_banana', 'deactivate', 'deactivated'])

# for Spread

# for Pour
obj_place.append(['relish_1', 'relish', 'deactivate', 'deactivated'])
obj_place.append(['lemon_juice_1', 'lemon_juice', 'deactivate', 'deactivated']) 
obj_place.append(['olive_oil_1', 'olive_oil', 'deactivate', 'deactivated'])
obj_place.append(['mayonnaise_1', 'mayonnaise', 'deactivate', 'deactivated'])
obj_place.append(['sugar_1', 'sugar', 'deactivate', 'deactivated'])




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
# task_plan
task_plan = []
task_plan.append(' -> PickUp/cucumber')
# -> Place/cucumeber/cutting_board/ingredient -> PickUp/knife -> Chop/cucumber/knife')
task_plan.append(' -> Place/knife/table/tool -> PickUp/bowl -> Place/bowl/near_cutting_board/dishware -> PickUp/knife -> Scrape/chopped_cucumber/bowl/knife')
task_plan.append(' -> Place/knife/table/tool ->  PickUp/lemon_juice_bottle -> Pour/lemon_juice_bottle/bowl/lemon_juice')
task_plan.append(' -> Place/lemon_juice_bottle/table/ing_bottle → PickUp/sugar_bottle -> Pour/sugar_bottle/bowl/sugar')
task_plan.append(' -> Place/sugar_bottle/table/ing_bottle  -> PickUp/relish_bottle -> Pour/relish_bottle/bowl/relish')
task_plan.append(' -> Place/relish_bottle/table/ing_bottle ->PickUp/olive_oil -> Pour/olive_oil_bottle/bowl/olive_oil')
task_plan.append(' -> Place/olive_oil_bottle/table/ing_bottle -> PickUp/mayonnaise_bottle -> Pour/mayonnaise_bottle/bowl/mayonnaise ')
task_plan.append(' -> Place/mayonnaise_bottle -> Stir/bowl/chopped_lettuce/spatula')
task_plan.append(' -> Place/spatula/table/tool -> PickUp/banana -> Place/banana/cutting_board/ingredient')
task_plan.append(' -> PickUp/knife -> Chop/Chopped_banana/knife')
task_plan.append(' -> Place/knife/table/tool -> PickUp/oregano -> PutOn/oregano/chopped_lettuce/None')
task_plan.append(' -> Scrape/Chopped_banana/bowl/scooper -> PutOn/Chopped_banana/raisin/None')
task_plan.append(' -> Place/scooper/table/tool-> PickUp/spatula -> Stir/bowl/salad/spatula')

##########################################################
# action_sequences
"""
total_action_sequences = []
for result in task_plan:
    action_sequences = [action.split('/') for action in result.split(" -> ") if action]
    #print(action_sequences,1)

    total_action_sequences.append(action_sequences)
"""