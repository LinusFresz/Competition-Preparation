'''
Multiple helper functions for various things
'''

from modules import *

def initiate_result_string(registration_list):
    result_string = []
    for person in registration_list:
        result_string.append((person[1], person[2], person[3]))
    return result_string

def update_scrambler_list(scrambler_list):
    for person in range(0, len(scrambler_list)):
        scrambler_list[person][1] = int(scrambler_list[person][1])
    return scrambler_list
