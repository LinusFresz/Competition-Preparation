#!/usr/bin/python

'''
Create scoresheets for succeeding rounds of the competition. Script collects data from cubecomps.com and wca website.
Note that you can only create scoresheets for one round at a time.
'''

import labels
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.graphics import shapes
from reportlab.lib import colors
from information_analysis import *


if wca_info:
    registerFont(TTFont('Arial', 'Trebuchet.ttf'))
else:
    if os.path.exists('STIXGeneral.ttf'):
        registerFont(TTFont('Arial', 'STIXGeneral.ttf'))
    else:
        print('TrueType font Trebuchet (Trebuchet.ttf) not found, used Arial instead.')
        registerFont(TTFont('Arial', 'Arial.ttf'))


# format information for scoresheets: usual DIN-A4 layout with 2 rows of 2 scoresheets each with a size of 100x130mm
specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)

# Creation of scoresheets
def write_scoresheets(label, width, height, name):
    # Competition name
    label.add(shapes.String(10, height-16, competition_name, fontSize=10, fontName='Arial'))
    
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
        label.add(shapes.String(10, height-80, 'Name:', fontSize=12, fontName='Arial'))
        label.add(shapes.Line(45, height-80, 160,height-80, trokeColor=colors.black))

    if registration_id:
        while len(registration_id) < 3:
            registration_id = ' ' + registration_id
        label.add(shapes.Rect(10,height-83,22, 15, fillColor=colors.white))
        label.add(shapes.String(14, height-79, registration_id, fontSize=10, fontName='Arial'))


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
    for k in range(0,format):
        height -= 35
        label.add(shapes.Rect(10,height,30, 30, fillColor=colors.white))
        label.add(shapes.String(22,height+10,str(number),fontSize=12, fontName='Arial'))
        label.add(shapes.Rect(45,height,160, 30, fillColor=colors.white))
        label.add(shapes.Rect(210,height,30, 30, fillColor=colors.white))
        label.add(shapes.Rect(245,height,30, 30, fillColor=colors.white))
        
        # Special treatment for 3x3x3 Multi-Blindfolded: additional info in result boxes
        if event_2 == '333mbf':
            label.add(shapes.Line(50, height+8, 72, height+8,trokeColor=colors.black))
            label.add(shapes.String(74,height+10,'out of',fontSize=10, fontName='Arial'))
            label.add(shapes.Line(100, height+8, 125, height+8,trokeColor=colors.black))
            label.add(shapes.String(125,height+10,'  Time:',fontSize=10, fontName='Arial'))
            label.add(shapes.Line(156, height+8, 200, height+8,trokeColor=colors.black))
    
        # Add cutoff information (if there are any)
        if cutoff_number == number and name['name']:
            if cutoff_number == 1: 
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

# Loop to create scoresheets for this round
if not new_creation:
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
    scoresheet_file = competition_name + '/' + 'Scoresheets' +event_round_name + '.pdf'
    sheet.save(scoresheet_file)
    
    print('')
    print('Scoresheets for ' + event_round_name + ' sucessfully saved in folder ' + competition_name + '.')
    sys.exit()
