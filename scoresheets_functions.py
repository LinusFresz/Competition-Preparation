'''import labels
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.graphics import shapes
from reportlab.lib import colors
'''

from wca_registration import *

def scoresheet_results_header(label, limit, limit_width, font_size_limit, height):
    ### Depending on the length of the 'limit' string (which includes (cumulative) limits), the box height gets choosen
    if limit_width > 150:
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
        
def scoresheet_result_boxes(label, height, format, event, cutoff_number, name):
    height = height - 105
    number = 1
    for k in range(0,int(format[-1:])):
        height -= 35
        label.add(shapes.Rect(10,height,30, 30, fillColor=colors.white))
        label.add(shapes.String(22,height+10,str(number),fontSize=12, fontName='Arial'))
        label.add(shapes.Rect(45,height,160, 30, fillColor=colors.white))
        label.add(shapes.Rect(210,height,30, 30, fillColor=colors.white))
        label.add(shapes.Rect(245,height,30, 30, fillColor=colors.white))
        
        # Special treatment for 3x3x3 Multi-Blindfolded: additional info in result boxes
        if event == '333mbf':
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
    return height
        
def scoresheet_extra(label, height, width):
    label.add(shapes.Line(10,height-13,width/2.0-50,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
    label.add(shapes.Line(width/2+50,height-13,width-10,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
    label.add(shapes.String(width/2.0,height-15,'Extra or Provisional Solve',fontSize=8,textAnchor='middle', fontName='Arial'))
    label.add(shapes.Rect(10,height-55,30, 30, fillColor=colors.white))
    label.add(shapes.Rect(45,height-55,160, 30, fillColor=colors.white))
    label.add(shapes.Rect(210,height-55,30, 30, fillColor=colors.white))
    label.add(shapes.Rect(245,height-55,30, 30, fillColor=colors.white))
    
def scoresheet_blank_header(label, height, width, competition_name):
    text_width = width - 10
    font_size = 25
    comp_name_width = stringWidth(competition_name, 'Arial', font_size)
    while comp_name_width > text_width:
        font_size *= 0.95
        comp_name_width = stringWidth(competition_name, 'Arial', font_size)
    label.add(shapes.String(width/2, height-25, competition_name, textAnchor='middle', fontSize=font_size, fontName='Arial'))

    label.add(shapes.Rect(10,height-63,125, 17, fillColor=colors.white))
    label.add(shapes.String(12, height-58, 'Event:', fontSize=12, fontName='Arial'))
    label.add(shapes.Rect(140,height-63,65, 17, fillColor=colors.white))
    label.add(shapes.String(142, height-58, 'Round:', fontSize=12, fontName='Arial'))
    label.add(shapes.Rect(210,height-63,65, 17, fillColor=colors.white))
    label.add(shapes.String(212, height-58, 'Group:', fontSize=12, fontName='Arial'))
    label.add(shapes.Rect(10,height-85,195, 17, fillColor=colors.white))
    label.add(shapes.String(12, height-80, 'Name:', fontSize=12, fontName='Arial'))
    label.add(shapes.Rect(210,height-85,65, 17, fillColor=colors.white))
    label.add(shapes.String(212, height-80, 'Id:', fontSize=12, fontName='Arial'))
    
def write_scoresheets_second_round(label, width, height, information):
    name = information[0]
    event_info = information[1]
    event_2 = information[2]
    next_round_name = information[3]
    event_round_name = information[4]
    competition_name = information[5]
    event = information[6]
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
    
def write_blank_sheets(label, width, height, information):    
    name = information[0]
    competition_name = information[1]
    
    scoresheet_blank_header(label, height, width, competition_name)
    
    scoresheet_results_header(label, '', 0, 10, height)

    # Creation of result boxes, depending on # of attempts for event and round
    height = scoresheet_result_boxes(label, height, '5', '', 0, name)
    
    # Add unlabeled box for extras and provisional solves
    scoresheet_extra(label, height, width) 

def write_scoresheets(label, width, height, information):
    name = information[0]
    event_ids = information[1]
    event_dict = information[2]
    round_counter = information[3]
    competitor_information = information[4]
    competition_name = information[5]
    event = information[6]
    
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
    id = ''
    for person in competitor_information:
        if (name[2] and ftfy.fix_text(name[2]) == ftfy.fix_text(person['personId'])) or (ftfy.fix_text(name[0]) == ftfy.fix_text(person['name'])):
            comp_name = person['name']
            registration_id = str(person['registration_id'])
            id = person['personId']
            if id == '':
                id = 'New Competitor'
            else:
                id = '     ' + id
    font_size = 13
    name_width = stringWidth(comp_name, 'Arial', font_size)    
    while name_width > 140:
        font_size *= 0.95
        name_width = stringWidth(comp_name, 'Arial', font_size)
    
    r = shapes.String(45,height-80, comp_name, fontName='Arial')
    r.fontSize = font_size
    label.add(r)
    
    label.add(shapes.String(width-78, height-16, id, fontSize=10, fontName='Arial'))
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
