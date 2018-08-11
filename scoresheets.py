#!/usr/bin/python

'''
Create scoresheets for all first rounds of the competition. Information that can be found on the scoresheets:
    - event
    - round
    - group number
    - registration id of competitor
    - competitor name
    - competitor WCA ID
    - time limit
    - cutoff
    - possible cumulative limits
'''

import ftfy
import labels
from competition_grouping_scrambling import *
from scoresheets_functions import *

# format information for scoresheets: usual DIN-A4 layout with 2 rows of 2 scoresheets each with a size of 100x130mm
specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)

# Creation of scoresheets
def write_scoresheets(label, width, height, name):    
    # WCA ID
    id = ''
    if name[event_ids[event['event']]]:
        if not name[2]:
            id = 'New Competitor'
        else:
            id = '     ' + name[2]
    label.add(shapes.String(width-78, height-16, id, fontSize=10, fontName='Arial'))
    
    # Selection of event information and shrinking to fit on scoresheets
    text_width = width - 10
    font_size_event = 25
    font_size_limit = 8
    if name[event_ids[event['event']]]:
        event_name = event_dict[event['event']] + ' - Round ' + str(event['round'])
        if round_counter[event['event']] == 1:
            if event['cutoff_number'] == 0:
                event_name = event_name.replace(' Round 1', ' Final')
            else:
                event_name = event_name.replace(' Round 1', ' Combined Final')
        event_width = stringWidth(event_name, 'Arial', fontSize=25)
        group = 'Group ' + str(name[event_ids[event['event']]])
        minutes, seconds = divmod(event['limit'], 60)
        minutes = str(minutes)
        seconds = str(seconds)
        if len(seconds) < 2:
            while len(seconds) < 2:
                seconds = '0' + str(seconds)
        if event['cumulative']:
            if ',' in event['cumulative']:
                events = event['cumulative'].split(',')
                limit = 'Result (' + minutes + ':' + seconds + ' cumulative limit for ' + events[0] + ' and ' + events[1] + ')'
            else:
                limit = 'Result (' + minutes + ':' + seconds + ' cumulative limit)'
        else:
            limit = 'Result (' + minutes + ':' + seconds + ' limit)'

        font_size_event = 25
        while event_width > text_width:
            font_size_event *= 0.95
            event_width = stringWidth(event_name, 'Arial', font_size_event)

    else:   
        event_name, group, round = '', '', ''
        limit = 'Result'

    if event['cutoff'] != 0:
        minutes, seconds = divmod(event['cutoff'], 60)
        minutes = str(minutes)
        seconds = str(seconds)
        if len(seconds) < 2:
            while len(seconds) < 2:
                seconds = '0' + str(seconds)
        cutoff_time = minutes + ':' + seconds

    s = shapes.String(width/2.0, height-50, event_name, textAnchor='middle', fontName='Arial')
    s.fontSize = font_size_event
    label.add(s)

    # Competitor information: name, WCA ID and registration id 
    comp_name = ''
    registration_id = ''
    for person in competitor_information:
        if name[2]:
            if name[2] == person['personId']:
                comp_name = person['name']
                registration_id = str(person['registration_id'])
        else:
            if name[1] == person['country'] and ftfy.fix_text(name[0]) == person['name']:
                comp_name = person['name']
                registration_id = str(person['registration_id'])
    font_size = 13
    name_width = stringWidth(comp_name, 'Arial', font_size)    
    while name_width > 140:
        font_size *= 0.95
        name_width = stringWidth(comp_name, 'Arial', font_size)
    
    r = shapes.String(45,height-80, comp_name, fontName='Arial')
    r.fontSize = font_size
    label.add(r)
    if not comp_name:
        scoresheet_blank_header(label, height, width, competition_name)
    else:
        label.add(shapes.String(10, height-16, competition_name, fontSize=10, fontName='Arial'))

    if registration_id:
        while len(registration_id) < 3:
            registration_id = ' ' + registration_id
        label.add(shapes.Rect(10,height-83,22, 15, fillColor=colors.white))
        label.add(shapes.String(14, height-79, registration_id, fontSize=10, fontName='Arial'))
    label.add(shapes.String(width-50, height-80, group, fontSize=12, fontName='Arial'))

    # Making header for result-boxes: # attempt, result (with (cumulative) limits), judge and competitor signature
    limit_width = stringWidth(limit, 'Arial', font_size_limit)
    scoresheet_results_header(label, limit, limit_width, font_size_limit, height)

    # Creation of result boxes, depending on # of attempts for event and round
    height = scoresheet_result_boxes(label, height, event['format'], event['event'], str(event['cutoff_number']), name)
    
    # Add unlabelled box for extras and provisional solves 
    scoresheet_extra(label, height, width)

# Loop to create all scoresheets
### EXCEPTION: no scoresheets created for 3x3x3 Fewest Moves
print('Creating scoresheets for first rounds...')
sheet = labels.Sheet(specs_scoresheets, write_scoresheets, border=False)
for event in event_info:
    if event['event'] != '333fm' and event['round'] == '1':
        scoresheet_list = []
        counter = 0
        for name in result_string:
            if name[event_ids[event['event']]]:
                scoresheet_list.append(name)
                counter += 1
        # Fill empty pages with blank scoresheets
        if (counter % 4) != 0:
            for filling in range(0,4-counter%4):
                scoresheet_list.append(('name', 'country', 'id', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''))
        sheet.add_labels(name for name in scoresheet_list)
scoresheet_file = competition_name + '/' + competition_name_stripped + 'Scoresheets.pdf'
sheet.save(scoresheet_file)

# Error handling for entire script
if error_messages:
    print('Notable errors while creating grouping and scrambling:')
    for errors in error_messages:
        print(error_messages[errors])
else:
    print('No errors while creating files.')

print('Please see folder ' + competition_name + ' for files.')
