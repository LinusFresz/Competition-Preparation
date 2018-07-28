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
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.graphics import shapes
from reportlab.lib import colors
from competition_grouping_scrambling import *

# format information for scoresheets: usual DIN-A4 layout with 2 rows of 2 scoresheets each with a size of 100x130mm
specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)

# Creation of scoresheets
def write_scoresheets(label, width, height, name):
    # Competition name
    label.add(shapes.String(10, height-16, competition_name, fontSize=10, fontName='Arial'))
    
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
        label.add(shapes.String(10, height-80, 'Name:', fontSize=12, fontName='Arial'))
        label.add(shapes.Line(45, height-80, 160,height-80, trokeColor=colors.black))

    if registration_id:
        while len(registration_id) < 3:
            registration_id = ' ' + registration_id
        label.add(shapes.Rect(10,height-83,22, 15, fillColor=colors.white))
        label.add(shapes.String(14, height-79, registration_id, fontSize=10, fontName='Arial'))
    label.add(shapes.String(width-50, height-80, group, fontSize=12, fontName='Arial'))

    # Making header for result-boxes: # attempt, result (with (cumulative) limits), judge and competitor signature
    ### Depending on the length of the 'limit' string (which includes (cumulative) limits), the box height gets choosen
    if stringWidth(limit, 'Arial', font_size_limit) > 150:
        box_height = 15
    else:
        box_height = 0
    label.add(shapes.Rect(10,height-105-box_height,30, 15+box_height, fillColor=colors.white))
    label.add(shapes.String(12,height-100-box_height/2.0,'Attempt',fontSize=7, fontName='Arial'))
    label.add(shapes.Rect(210,height-105-box_height,30, 15+box_height, fillColor=colors.white))
    label.add(shapes.String(215,height-100-box_height/2.0,'Judge',fontSize=8, fontName='Arial'))
    label.add(shapes.Rect(245,height-105-box_height,30, 15+box_height, fillColor=colors.white))
    label.add(shapes.String(250,height-100-box_height/2.0,'Comp',fontSize=8, fontName='Arial'))
    
    if stringWidth(limit, 'Arial', font_size_limit) > 150:
        label.add(shapes.Rect(45,height-120,160, 30, fillColor=colors.white))
        label.add(shapes.String(49,height-100,limit[:40], fontSize=font_size_limit, fontName='Arial'))
        label.add(shapes.String(49,height-115,limit[41:], fontSize=font_size_limit, fontName='Arial'))
        height = height - 15
    else:
        label.add(shapes.Rect(45,height-105,160, 15, fillColor=colors.white))
        label.add(shapes.String(49,height-100,limit, fontSize=font_size_limit, fontName='Arial'))

    # Creation of result boxes, depending on # of attempts for event and round
    height = height - 105
    number = 1
    for k in range(0,event['format']):
        height -= 35
        label.add(shapes.Rect(10,height,30, 30, fillColor=colors.white))
        label.add(shapes.String(22,height+10,str(number),fontSize=12, fontName='Arial'))
        label.add(shapes.Rect(45,height,160, 30, fillColor=colors.white))
        label.add(shapes.Rect(210,height,30, 30, fillColor=colors.white))
        label.add(shapes.Rect(245,height,30, 30, fillColor=colors.white))
        
        # Special treatment for 3x3x3 Multi-Blindfolded: additional info in result boxes
        if event['event'] == '333mbf':
            label.add(shapes.Line(50, height+8, 72, height+8,trokeColor=colors.black))
            label.add(shapes.String(74,height+10,'out of',fontSize=10, fontName='Arial'))
            label.add(shapes.Line(100, height+8, 125, height+8,trokeColor=colors.black))
            label.add(shapes.String(125,height+10,'  Time:',fontSize=10, fontName='Arial'))
            label.add(shapes.Line(156, height+8, 200, height+8,trokeColor=colors.black))
    
        # Add cutoff information (if there are any) 
        if event['cutoff_number'] == number and name[0]:
            if event['cutoff_number'] == 1: 
                cutoff = 'Continue if Attempt 1 is below ' + cutoff_time
                indent = 70
            else:
                cutoff = 'Continue if Attempt 1 or Attempt 2 is below ' + cutoff_time
                indent = 93
            label.add(shapes.Line(10,height-13,width/2.0-indent,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
            label.add(shapes.Line(width/2+indent,height-13,width-10,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
            label.add(shapes.String(width/2.0,height-15,cutoff,fontSize=8,textAnchor='middle', fontName='Arial'))
            height -= 20
        number+= 1
    
    # Add unlabeled box for extras and provisional solves 
    label.add(shapes.Line(10,height-13,width/2.0-50,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
    label.add(shapes.Line(width/2+50,height-13,width-10,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
    label.add(shapes.String(width/2.0,height-15,'Extra or Provisional Solve',fontSize=8,textAnchor='middle', fontName='Arial'))
    label.add(shapes.Rect(10,height-55,30, 30, fillColor=colors.white))
    label.add(shapes.Rect(45,height-55,160, 30, fillColor=colors.white))
    label.add(shapes.Rect(210,height-55,30, 30, fillColor=colors.white))
    label.add(shapes.Rect(245,height-55,30, 30, fillColor=colors.white))


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
