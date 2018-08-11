#!/usr/bin/python

'''
Create scoresheets for succeeding rounds of the competition. Script collects data from cubecomps.com and wca website.
Note that you can only create scoresheets for one round at a time.
'''

import labels
from scoresheets_functions import *
from information_analysis import *


registerFont(TTFont('Arial', 'Trebuchet.ttf'))

# format information for scoresheets: usual DIN-A4 layout with 2 rows of 2 scoresheets each with a size of 100x130mm
specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)

# Creation of scoresheets
def write_scoresheets(label, width, height, name):    
    # WCA ID
    if name['name'] and not name['personId']:
        id = 'New Competitor'
    else:
        id = '     ' + name['personId']
    label.add(shapes.String(width-78, height-16, id, fontSize=10, fontName='Arial'))
    
    # Selection of event information and shrinking to fit on scoresheets
    text_width = width - 10
    font_size_event = 25
    font_size_limit = 8
    
    for event_infos in event_info:
        if event_infos['event'] == event_2 and event_infos['round'] == str(next_round_name[-1:]):
            limit = event_infos['limit']
            cutoff = event_infos['cutoff']
            cumulative = event_infos['cumulative']
            round = event_infos['round']
            cutoff_number = event_infos['cutoff_number']
            format = event_infos['format']
        
    event_name = event_round_name
       
    event_width = stringWidth(event_name, 'Arial', fontSize=25)
    minutes, seconds = divmod(limit, 60)
    minutes = str(minutes)
    seconds = str(seconds)
    if len(seconds) < 2:
        while len(seconds) < 2:
            seconds = '0' + str(seconds)
    if cumulative:
        if ',' in cumulative:
            events = cumulative.split(',')
            limit = 'Result (' + minutes + ':' + seconds + ' cumulative limit for ' + events[0] + ' and ' + events[1] + ')'
        else:
            limit = 'Result (' + minutes + ':' + seconds + ' cumulative limit)'
    else:
        limit = 'Result (' + minutes + ':' + seconds + ' limit)'

    font_size_event = 25
    while event_width > text_width:
        font_size_event *= 0.95
        event_width = stringWidth(event_name, 'Arial', font_size_event)

    if not name['name']:
        event_name, group, round = '', '', ''
        limit = 'Result'

    if cutoff != 0:
        minutes, seconds = divmod(cutoff, 60)
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
    ranking = ''

    if name['name']:
        comp_name = name['name']
        registration_id = str(name['registration_id'])
        ranking = str(name['ranking'])
        
    font_size = 13
    name_width = stringWidth(comp_name, 'Arial', font_size)    
    while name_width > 140:
        font_size *= 0.95
        name_width = stringWidth(comp_name, 'Arial', font_size)
    
    r = shapes.String(45,height-80, comp_name, fontName='Arial')
    r.fontSize = font_size
    label.add(r)

    while len(ranking) < 3:
        ranking = ' ' + ranking
    label.add(shapes.String(width-22, height-80, ranking, fontSize=12, fontName='Arial'))

    if not comp_name:
        scoresheet_blank_header(label, height, width, competition_name)
    else:
        label.add(shapes.String(10, height-16, competition_name, fontSize=10, fontName='Arial'))

    if registration_id:
        while len(registration_id) < 3:
            registration_id = ' ' + registration_id
        label.add(shapes.Rect(10,height-83,22, 15, fillColor=colors.white))
        label.add(shapes.String(14, height-79, registration_id, fontSize=10, fontName='Arial'))

    # Making header for result-boxes: # attempt, result (with (cumulative) limits), judge and competitor signature
    limit_width = stringWidth(limit, 'Arial', font_size_limit)
    scoresheet_results_header(label, limit, limit_width, font_size_limit, height)

    # Creation of result boxes, depending on # of attempts for event and round
    height = scoresheet_result_boxes(label, height, format, event, cutoff_number, name)
    
    # Add unlabelled box for extras and provisional solves
    scoresheet_extra(label, height, width)
    
def write_blank_sheets(label, width, height, name):    

    scoresheet_blank_header(label, height, width, competition_name)
    
    scoresheet_results_header(label, '', 0, 10, height)

    # Creation of result boxes, depending on # of attempts for event and round
    height = scoresheet_result_boxes(label, height, 5, '', 0, name)
    
    # Add unlabeled box for extras and provisional solves
    scoresheet_extra(label, height, width) 

# Loop to create scoresheets for this round
if not new_creation:
    if blank_sheets:
        scoresheet_list = []
        sheet = labels.Sheet(specs_scoresheets, write_blank_sheets, border=False)
        scoresheet_file = 'Blank_Scoresheets.pdf'
        print('Creating blank sheets')
        for scoresheet_count in range(0, 4):
            scoresheet_list.append({'name': '', 'country': '', 'personId': '', 'registrationId': ''})
        sheet.add_labels(name for name in scoresheet_list)
        sheet.save(scoresheet_file)
    else:
        print('Creating scoresheets for ' + event_round_name + '...')
        sheet = labels.Sheet(specs_scoresheets, write_scoresheets, border=False)
        scoresheet_list = []
        counter = 0
        for name in competitor_information:
            scoresheet_list.append(name)
            counter += 1

        scoresheet_list = sorted(scoresheet_list, key=lambda x: x['ranking'])

        # Fill empty pages with blank scoresheets
        if (advancing_competitors % 4) != 0:
            for filling in range(0,4-counter%4):
                scoresheet_list.append({'name': '', 'country': '', 'personId': '', 'registrationId': ''})
                
        # Create scoresheets
        sheet.add_labels(name for name in scoresheet_list)
        scoresheet_file = competition_name + '/' + 'Scoresheets' + event_round_name + '.pdf'
        sheet.save(scoresheet_file)
    
        print('')
        print('Scoresheets for ' + event_round_name + ' sucessfully saved in folder ' + competition_name + '.')
        os.remove(wcif_file.name)
    sys.exit()
