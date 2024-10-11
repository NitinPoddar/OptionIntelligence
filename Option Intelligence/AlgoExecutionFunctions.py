# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 14:47:00 2024

@author: Nitin
"""


# Process the input condition
def entry_process_condition(condition,order):
    if Trade("Position",0)=="True":
        # Split by 'and' and strip whitespace
        conditions = [part.strip() for part in condition.split('and')]
        
        # Initialize variables to hold conditions
        target_condition = None
        other_conditions = []

        # Separate Target conditions from others
        for cond in conditions:
            if "Target" in cond:
                target_condition = cond
            else:
                other_conditions.append(cond)

        # Convert '=' to '==' in other conditions
        for i in range(len(other_conditions)):
            other_conditions[i] = other_conditions[i].replace('=', '==')

        # Evaluate the Target condition if it exists
        if target_condition:
            exec(target_condition)  # Use exec for assignment

            # Evaluate other conditions if they exist
            if other_conditions:
                combined_other_conditions = ' and '.join(other_conditions)
                if eval(combined_other_conditions):
                    print("success")

    
        
    