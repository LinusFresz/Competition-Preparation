### Multiple helper functions for various things

from modules import *

# Create list which contains all competitors
# Later on, grouping informating gets added to each list of this tuple
def initiate_result_string(registration_list):
    result_string = []
    for person in registration_list:
        result_string.append((person[1], person[2], person[3]))
    return result_string

# Make the second column (containing the round number) of the scrambler list an integer
def update_scrambler_list(scrambler_list):
    for person in range(0, len(scrambler_list)):
        scrambler_list[person][1] = int(scrambler_list[person][1])
    return scrambler_list

# Return minutes and seconds for given amount of seconds
def format_minutes_and_seconds(time_string):
    minutes, seconds = divmod(time_string, 60)
    minutes = str(int(minutes))
    seconds = enlarge_string(str(int(seconds)), '0', 2)
    return (minutes, seconds)

# Add whitespace/other characters to string
def enlarge_string(input_string, add_string, string_length):
    while len(input_string) < string_length:
        input_string = ''.join([add_string, input_string])
    return input_string

# Split string into to if lenght is longer than column width
def create_two_strings_out_of_one(input_string, font_size, width):
    input_string_string1 = ''
    for substring in input_string.split():
        new_string = ''.join([input_string_string1, substring, ' '])
        if stringWidth(new_string, 'Arial', font_size) < width:
            input_string_string1 = ''.join([input_string_string1, substring, ' '])
        else:
            break
    input_string_string2 = input_string.replace(input_string_string1, '')
    return (input_string_string1, input_string_string2)
