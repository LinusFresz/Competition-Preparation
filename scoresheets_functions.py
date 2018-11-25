'''
    Additional functions for the scoresheet creation.
'''

from wca_registration import *
    
def format_limit_string(cumulative, minutes, seconds):
    if cumulative:
        if ',' in cumulative:
            return 'Result ({}:{} cumulative limit for {} and {})'.format(minutes, seconds, cumulative.split(',')[0], cumulative.split(',')[1])
        else:
            return 'Result (Time Limit {}:{} cumulative)'.format(minutes, seconds)
    else:
        return 'Result (Time Limit {}:{})'.format(minutes, seconds)

def scoresheet_results_header(label, limit, limit_width, font_size_limit, height, scrambler_signature):
    ### Depending on the length of the 'limit' string (which includes (cumulative) limits), the box height gets choosen
    shift = 35
    extra_width = 30
    if scrambler_signature:
        shift = 0
        extra_width = 0
        
    if limit_width > (120 + shift) and limit_width <= (240 + shift):
        box_height = 15
    elif limit_width > (240 + shift):
        box_height = 30
    else:
        box_height = 0
    label.add(shapes.Rect(10,height-105-box_height,30, 15+box_height, fillColor=colors.white))
    label.add(shapes.String(12,height-100-box_height/2.0,'Attempt',fontSize=7, fontName='Arial'))
    if scrambler_signature:
        label.add(shapes.Rect(45,height-105-box_height,30, 15+box_height, fillColor=colors.white))
        label.add(shapes.String(47,height-100-box_height/2.0,'Scrambler',fontSize=6, fontName='Arial'))
    label.add(shapes.Rect(210,height-105-box_height,30, 15+box_height, fillColor=colors.white))
    label.add(shapes.String(215,height-100-box_height/2.0,'Judge',fontSize=8, fontName='Arial'))
    label.add(shapes.Rect(245,height-105-box_height,30, 15+box_height, fillColor=colors.white))
    label.add(shapes.String(250,height-100-box_height/2.0,'Comp',fontSize=8, fontName='Arial'))
    
    time_limit_width = stringWidth(limit, 'Arial', font_size_limit)
    time_limit_string1 = limit
    time_limit_string2, time_limit_string3 = '', ''
    if time_limit_width > (120 + extra_width) and time_limit_width <= (240 + 2*extra_width):
        time_limit_string1, time_limit_string2 = create_two_strings_out_of_one(limit, font_size_limit, 120 + extra_width)

        label.add(shapes.Rect(80-shift,height-120,125+shift, 30, fillColor=colors.white))
        label.add(shapes.String(84-shift,height-100,time_limit_string1, fontSize=font_size_limit, fontName='Arial'))
        label.add(shapes.String(84-shift,height-115,time_limit_string2, fontSize=font_size_limit, fontName='Arial'))
        height = height - 15
    elif time_limit_width > (240 + extra_width):
        time_limit_string1, time_limit_string2 = create_two_strings_out_of_one(limit, font_size_limit, 120 + extra_width)
        limit = time_limit_string2.replace('  ', ' ')
        time_limit_string2, time_limit_string3 = create_two_strings_out_of_one(limit, font_size_limit, 120 + extra_width)

        label.add(shapes.Rect(80-shift,height-135,125+shift, 45, fillColor=colors.white))
        label.add(shapes.String(84-shift,height-100,time_limit_string1, fontSize=font_size_limit, fontName='Arial'))
        label.add(shapes.String(84-shift,height-115,time_limit_string2, fontSize=font_size_limit, fontName='Arial'))
        label.add(shapes.String(84-shift,height-130,time_limit_string3, fontSize=font_size_limit, fontName='Arial'))
        height = height - 30
    else:
        label.add(shapes.Rect(80-shift,height-105,125+shift, 15, fillColor=colors.white))
        label.add(shapes.String(84-shift,height-100,limit, fontSize=font_size_limit, fontName='Arial'))
    return height

# boxes for the actual attempts
# automatic determination of amount of needed rows
def scoresheet_result_boxes(label, height, width, format, event, cutoff_number, cutoff_time, name, scrambler_signature):
    height = height - 105
    number = 1
    number_of_attempts = int(format[-1:])
    if (type(name) is dict and name['name'] == 'name') or (type(name) is list and name[0] == 'name'):
        number_of_attempts = 5
    for attempts in range(0,number_of_attempts):
        height -= 35
        label.add(shapes.Rect(10,height,30, 30, fillColor=colors.white))
        label.add(shapes.String(22,height+10,str(number),fontSize=12, fontName='Arial'))
        shift = 35
        if scrambler_signature:
            label.add(shapes.Rect(45,height,30, 30, fillColor=colors.white))
            shift = 0
        label.add(shapes.Rect(80-shift,height,125+shift, 30, fillColor=colors.white))
        label.add(shapes.Rect(210,height,30, 30, fillColor=colors.white))
        label.add(shapes.Rect(245,height,30, 30, fillColor=colors.white))
        
        # special treatment for 3x3x3 Multi-Blindfolded: additional info in result boxes
        if event == '333mbf':
            label.add(shapes.Line(82-shift, height+8, 95-shift, height+8,trokeColor=colors.black))
            label.add(shapes.String(97-shift,height+10,'out of',fontSize=8, fontName='Arial'))
            label.add(shapes.Line(120-shift, height+8, 135-shift, height+8,trokeColor=colors.black))
            label.add(shapes.String(132-shift,height+10,'  Time:',fontSize=8, fontName='Arial'))
            label.add(shapes.Line(160-shift, height+8, 200-shift, height+8,trokeColor=colors.black))
    
        # add cutoff information (if there is any)
        if cutoff_number == str(number) and name[0] != 'name':
            if cutoff_number == '1': 
                cutoff = 'Continue if Attempt 1 is below {}'.format(cutoff_time)
                indent = 70
            else:
                cutoff = 'Continue if Attempt 1 or Attempt 2 is below {}'.format(cutoff_time)
                indent = 93
            label.add(shapes.Line(10,height-13,width/2.0-indent,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
            label.add(shapes.Line(width/2+indent,height-13,width-10,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
            label.add(shapes.String(width/2.0,height-15,cutoff,fontSize=8,textAnchor='middle', fontName='Arial'))
            height -= 20
        number+= 1
    return height
  
# boxes for extra attempt
def scoresheet_extra(label, height, width, scrambler_signature):
    label.add(shapes.Line(10,height-13,width/2.0-30,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
    label.add(shapes.Line(width/2+30,height-13,width-10,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
    label.add(shapes.String(width/2.0,height-15,'Extra Attempt',fontSize=8,textAnchor='middle', fontName='Arial'))
    label.add(shapes.Rect(10,height-55,30, 30, fillColor=colors.white))
    shift = 35
    if scrambler_signature:
        label.add(shapes.Rect(45,height-55,30, 30, fillColor=colors.white))
        shift = 0
    label.add(shapes.Rect(80-shift,height-55,125+shift, 30, fillColor=colors.white))
    label.add(shapes.Rect(210,height-55,30, 30, fillColor=colors.white))
    label.add(shapes.Rect(245,height-55,30, 30, fillColor=colors.white))
    
# extra header for blank scoresheets with fields for event, round, competitor name and id
def scoresheet_blank_header(label, height, width, competition_name, blank_sheets_round_name):
    text_width = width - 10
    font_size = 25
    comp_name_width, font_size = enlarge_string_size(competition_name, text_width, font_size)

    label.add(shapes.String(width/2, height-25, competition_name, textAnchor='middle', fontSize=font_size, fontName='Arial'))
    
    if blank_sheets_round_name:
        font_size_round = 25
        event_width = text_width + 1
        event_width, font_size_round = enlarge_string_size(blank_sheets_round_name, text_width, font_size_round)

        s = shapes.String(width/2.0, height-55, blank_sheets_round_name, textAnchor='middle', fontName='Arial')
        s.fontSize = font_size_round
        label.add(s)

    else:
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
    
# writing scoresheets for consecutive rounds
### this function needs review in the future ###
def write_scoresheets_second_round(label, width, height, information):
    name = information[0]
    event_info = information[1]
    event_2 = information[2]
    next_round_name = information[3]
    event_round_name = information[4]
    competition_name = information[5]
    event = information[6]
    scrambler_signature = information[7]
    
    # WCA ID
    if name['name'] and not name['personId']:
        id = 'New Competitor'
    else:
        id = '     {}'.format(name['personId'])
    label.add(shapes.String(width-78, height-16, id, fontSize=10, fontName='Arial'))
    
    # selection of event information and shrinking to fit on scoresheets
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
    minutes, seconds = format_minutes_and_seconds(limit)
    limit = format_limit_string(cumulative, minutes, seconds)
    
    font_size_event = 25
    event_width, font_size_event = enlarge_string_size(event_name, text_width, font_size_event)

    if not name['name']:
        event_name, group, round = '', '', ''
        limit = 'Result'

    cutoff_time = ''
    if cutoff != 0:
        minutes, seconds = format_minutes_and_seconds(limit)
        cutoff_time = '{}:{}'.format(minutes, seconds) 

    s = shapes.String(width/2.0, height-50, event_name, textAnchor='middle', fontName='Arial')
    s.fontSize = font_size_event
    label.add(s)

    # competitor information: name, WCA ID and registration id 
    comp_name, registration_id, ranking = '', '', ''

    if name['name']:
        comp_name = name['name']
        registration_id = str(name['registration_id'])
        ranking = str(name['ranking'])
        
    font_size = 13
    name_width, font_size = enlarge_string_size(comp_name, 140, font_size)

    r = shapes.String(45,height-80, comp_name, fontName='Arial')
    r.fontSize = font_size
    label.add(r)

    ranking = enlarge_string(ranking, ' ', 3)
    label.add(shapes.String(width-22, height-80, ranking, fontSize=12, fontName='Arial'))

    if not comp_name:
        scoresheet_blank_header(label, height, width, competition_name, '')
    else:
        label.add(shapes.String(10, height-16, competition_name, fontSize=10, fontName='Arial'))

    if registration_id:
        registration_id = enlarge_string(registration_id, ' ', 3)
        label.add(shapes.Rect(10,height-83,22, 15, fillColor=colors.white))
        label.add(shapes.String(14, height-79, registration_id, fontSize=10, fontName='Arial'))

    # making header for result-boxes: # attempt, result (with (cumulative) limits), judge and competitor signature
    limit_width = stringWidth(limit, 'Arial', font_size_limit)
    height = scoresheet_results_header(label, limit, limit_width, font_size_limit, height, scrambler_signature)

    # creation of result boxes, depending on # of attempts for event and round
    height = scoresheet_result_boxes(label, height, width, format, event, cutoff_number, cutoff_time, name, scrambler_signature)
    
    # add unlabelled box for extras and provisional solves
    scoresheet_extra(label, height, width, scrambler_signature)
    
def write_blank_sheets(label, width, height, information):    
    name = information[0]
    competition_name = information[1]
    scrambler_signature = information[2]
    blank_sheets_round_name = information[3]
    
    scoresheet_blank_header(label, height, width, competition_name, blank_sheets_round_name)
    
    height = scoresheet_results_header(label, '', 0, 10, height, scrambler_signature)

    # creation of result boxes, depending on # of attempts for event and round
    height = scoresheet_result_boxes(label, height, width, '5', '', 0, 0, name, scrambler_signature)
    
    # add unlabeled box for extras and provisional solves
    scoresheet_extra(label, height, width, scrambler_signature) 

### this function needs review in the future ###
def write_scoresheets(label, width, height, information):
    name = information[0]
    event_ids = information[1]
    event_dict = information[2]
    round_counter = information[3]
    competitor_information = information[4]
    competition_name = information[5]
    event = information[6]
    scrambler_signature = information[7]
    
    text_width = width - 10
    font_size_event = 25
    font_size_limit = 8
    if name[event_ids[event['event']]]:
        event_name = '{} - Round {}'.format(event_dict[event['event']], str(event['round']))
        if round_counter[event['event']] == 1:
            if event['cutoff_number'] == 0:
                event_name = event_name.replace(' Round 1', ' Final')
            else:
                event_name = event_name.replace(' Round 1', ' Combined Final')
        event_width = stringWidth(event_name, 'Arial', fontSize=25)
        group = 'Group {}'.format(str(name[event_ids[event['event']]]))
        minutes, seconds = format_minutes_and_seconds(event['limit'])
        limit = format_limit_string(event['cumulative'], minutes, seconds)
        
        font_size_event = 25
        event_width, font_size_event = enlarge_string_size(event_name, text_width, font_size_event)
        
    else:   
        event_name, group, round = '', '', ''
        limit = 'Result'

    cutoff_time = ''
    if event['cutoff'] != 0:
        minutes, seconds = format_minutes_and_seconds(event['cutoff'])
        cutoff_time = '{}:{}'.format(minutes, seconds)

    s = shapes.String(width/2.0, height-50, event_name, textAnchor='middle', fontName='Arial')
    s.fontSize = font_size_event
    label.add(s)

    # competitor information: name, WCA ID and registration id 
    comp_name, registration_id, id = '', '', ''

    for person in competitor_information:
        if (name[2] and ftfy.fix_text(name[2]) == ftfy.fix_text(person['personId'])) or (ftfy.fix_text(name[0]) == ftfy.fix_text(person['name'])):
            comp_name = person['name']
            registration_id = str(person['registration_id'])
            id = person['personId']
            if id == '':
                id = 'New Competitor'
            else:
                id = '     {}'.format(id)
    font_size = 13
    name_width, font_size = enlarge_string_size(comp_name, 140, font_size)
    
    r = shapes.String(45,height-80, comp_name, fontName='Arial')
    r.fontSize = font_size
    label.add(r)
    
    label.add(shapes.String(width-78, height-16, id, fontSize=10, fontName='Arial'))
    if not comp_name:
        scoresheet_blank_header(label, height, width, competition_name, '')
    else:
        label.add(shapes.String(10, height-16, competition_name, fontSize=10, fontName='Arial'))

    if registration_id:
        registration_id = enlarge_string(registration_id, ' ', 3)
        label.add(shapes.Rect(10,height-83,22, 15, fillColor=colors.white))
        label.add(shapes.String(14, height-79, registration_id, fontSize=10, fontName='Arial'))
    label.add(shapes.String(width-50, height-80, group, fontSize=12, fontName='Arial'))

    # making header for result-boxes: # attempt, result (with (cumulative) limits), judge and competitor signature
    limit_width = stringWidth(limit, 'Arial', font_size_limit)
    height = scoresheet_results_header(label, limit, limit_width, font_size_limit, height, scrambler_signature)

    # creation of result boxes, depending on # of attempts for event and round
    height = scoresheet_result_boxes(label, height, width, event['format'], event['event'], str(event['cutoff_number']), cutoff_time, name, scrambler_signature)
    
    # add unlabelled box for extras and provisional solves 
    scoresheet_extra(label, height, width, scrambler_signature)
