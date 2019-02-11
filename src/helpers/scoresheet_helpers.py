from modules import *
import helpers.helpers as helper

### Some file specific helper functions
# Add whitespace/other characters to string
def enlarge_string_width(input_string, add_begin, add_end, wanted_width, font_size):
    width = stringWidth(input_string, 'Arial', font_size)
    while width < wanted_width:
        input_string = '{}{}{}'.format(add_begin, input_string, add_end)
        width = stringWidth(input_string, 'Arial', font_size)
    return (input_string, width)

def enlarge_string_size(input_string, wanted_width, font_size):
    width = stringWidth(input_string, 'Arial', font_size)
    while width > wanted_width:
        font_size *= 0.95
        width = stringWidth(input_string, 'Arial', font_size)
    return (width, font_size)

# Format limit string with given cumulative limit, minutes and seconds
def format_limit_string(cumulative, minutes, seconds):
    if cumulative:
        if ',' in cumulative:
            return 'Result ({}:{} cumulative limit for {} and {})'.format(minutes, seconds, cumulative.split(',')[0], cumulative.split(',')[1])
        else:
            return 'Result (Time Limit {}:{} cumulative)'.format(minutes, seconds)
    else:
        return 'Result (Time Limit {}:{})'.format(minutes, seconds)

### Some helper functions to create different parts of scoresheets
def scoresheet_competitor_and_competition_name(competitor_name, competition_name, label, height, width):
    font_size = 13
    name_width, font_size = enlarge_string_size(competitor_name, 140, font_size)
    r = shapes.String(45,height-80, competitor_name, fontName='Arial')
    r.fontSize = font_size
    label.add(r)
    if not competitor_name:
        scoresheet_blank_header(label, height, width, competition_name, '')
    else:
        label.add(shapes.String(10, height-16, competition_name, fontSize=10, fontName='Arial'))

def scoresheet_limit(event_name, limit, cumulative, text_width):
    event_width = stringWidth(event_name, 'Arial', fontSize=25)
    minutes, seconds = helper.format_minutes_and_seconds(limit)
    limit = format_limit_string(cumulative, minutes, seconds)
    event_width, font_size_event = enlarge_string_size(event_name, text_width, font_size=25)
    
    return(event_width, font_size_event, limit)

def scoresheet_event_name(cutoff, limit, event_name, label, width, height, font_size_event):
    cutoff_time = ''
    if cutoff != 0:
        minutes, seconds = helper.format_minutes_and_seconds(limit)
        cutoff_time = '{}:{}'.format(minutes, seconds)

    s = shapes.String(width/2.0, height-50, event_name, textAnchor='middle', fontName='Arial')
    s.fontSize = font_size_event
    label.add(s)
    
    return (cutoff_time, label)

# Body of scoresheet, containing competitor name, competition name, event, group etc.
def scoresheet_body(registration_id, group, limit, font_size_limit, label, height, width, scrambler_signature, event_format, event_name, cutoff_number, cutoff_time, name):
    if registration_id:
        registration_id = helper.enlarge_string(registration_id, ' ', 3)
        label.add(shapes.Rect(10,height-83,22, 15, fillColor=colors.white))
        label.add(shapes.String(14, height-79, registration_id, fontSize=10, fontName='Arial'))
    label.add(shapes.String(width-50, height-80, group, fontSize=12, fontName='Arial'))

    # Making header for result-boxes: # attempt, result (with (cumulative) limits), judge and competitor signature
    limit_width = stringWidth(limit, 'Arial', font_size_limit)
    height = scoresheet_results_header(label, limit, limit_width, font_size_limit, height, scrambler_signature)

    # Creation of result boxes, depending on # of attempts for event and round
    height = scoresheet_result_boxes(label, height, width, event_format, event_name, cutoff_number, cutoff_time, name, scrambler_signature)
    
    # Add unlabelled box for extras and provisional solves
    scoresheet_extra(label, height, width, scrambler_signature)

# Header with limit and headlines
# Depending on the length of the 'limit' string (which includes (cumulative) limits), the box height gets choosen
def scoresheet_results_header(label, limit, limit_width, font_size_limit, height, scrambler_signature):
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
        time_limit_string1, time_limit_string2 = helper.create_two_strings_out_of_one(limit, font_size_limit, 120 + extra_width)

        label.add(shapes.Rect(80-shift,height-120,125+shift, 30, fillColor=colors.white))
        label.add(shapes.String(84-shift,height-100,time_limit_string1, fontSize=font_size_limit, fontName='Arial'))
        label.add(shapes.String(84-shift,height-115,time_limit_string2, fontSize=font_size_limit, fontName='Arial'))
        height = height - 15
    elif time_limit_width > (240 + extra_width):
        time_limit_string1, time_limit_string2 = helper.create_two_strings_out_of_one(limit, font_size_limit, 120 + extra_width)
        limit = time_limit_string2.replace('  ', ' ')
        time_limit_string2, time_limit_string3 = helper.create_two_strings_out_of_one(limit, font_size_limit, 120 + extra_width)

        label.add(shapes.Rect(80-shift,height-135,125+shift, 45, fillColor=colors.white))
        label.add(shapes.String(84-shift,height-100,time_limit_string1, fontSize=font_size_limit, fontName='Arial'))
        label.add(shapes.String(84-shift,height-115,time_limit_string2, fontSize=font_size_limit, fontName='Arial'))
        label.add(shapes.String(84-shift,height-130,time_limit_string3, fontSize=font_size_limit, fontName='Arial'))
        height = height - 30
    else:
        label.add(shapes.Rect(80-shift,height-105,125+shift, 15, fillColor=colors.white))
        label.add(shapes.String(84-shift,height-100,limit, fontSize=font_size_limit, fontName='Arial'))
    return height

# Extra header for blank scoresheets with fields for event, round, competitor name and id
def scoresheet_blank_header(label, height, width, competition_name, blank_sheets_round_name):
    text_width = width - 10
    font_size = 25
    competition_name_width, font_size = enlarge_string_size(competition_name, text_width, font_size)
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

# Boxes for the actual attempts
# Automatic determination of amount of rows needed
def scoresheet_result_boxes(label, height, width, format, event, cutoff_number, cutoff_time, name, scrambler_signature):
    height = height - 105
    number = 1
    number_of_attempts = int(format[-1:])
    if (isinstance(name, dict) and name['name'] == 'name') or (isinstance(name, list) and name[0] == 'name'):
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
        
        # Special treatment for 3x3x3 Multi-Blindfolded: additional info in result boxes
        if event == '333mbf':
            label.add(shapes.Line(82-shift, height+8, 95-shift, height+8,trokeColor=colors.black))
            label.add(shapes.String(97-shift,height+10,'out of',fontSize=8, fontName='Arial'))
            label.add(shapes.Line(120-shift, height+8, 135-shift, height+8,trokeColor=colors.black))
            label.add(shapes.String(132-shift,height+10,'  Time:',fontSize=8, fontName='Arial'))
            label.add(shapes.Line(160-shift, height+8, 200-shift, height+8,trokeColor=colors.black))

        # Add cutoff information (if there is any)
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

# Boxes for extra attempt
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
