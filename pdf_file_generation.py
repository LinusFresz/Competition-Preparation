'''
    This file contains all functions to generate files:
    PDF:
        - (blank) scoresheets
        - nametags
        - schedule
    .csv:
        - registration
        - grouping
        - scrambling
'''

from modules import *
from grouping_scrambling_functions import events_ranking_by_speed
from helpers.helpers import format_minutes_and_seconds, enlarge_string, create_two_strings_out_of_one
from helpers.scoresheet_helpers import scoresheet_competitor_and_competition_name, scoresheet_limit, scoresheet_event_name, scoresheet_body, scoresheet_results_header, scoresheet_blank_header, scoresheet_result_boxes, scoresheet_extra, create_two_strings_out_of_one, enlarge_string_width, enlarge_string_size

### PDF splitter and merger
# Both are used for twosided nametags
def pdf_splitter(path, competition_name):
    fname = os.path.splitext(os.path.basename(path))[0]
    pdf = PdfFileReader(path)
    for page in range(pdf.getNumPages()):
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf.getPage(page))
        output_filename = '{}/{}_page_{}.pdf'.format(competition_name, fname, page+1)
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)

def merger(output_path, input_paths):
    pdf_merger = PdfFileMerger()
    for path in input_paths:
        pdf_merger.append(path)
        os.remove(path)
    with open(output_path, 'wb') as fileobj:
        pdf_merger.write(fileobj)

### Functions to create different files: registration, schedule, nametags, grouping, scrambling, scoresheets
def create_registration_file(output_registration, registration_list, column_ids):
    with open(output_registration, 'w') as registration_file:
        if isinstance(registration_list[0][len(registration_list[0]) - 1], str):
            print('Name, Country, WCA ID, Date of Birth, Gender, Guests, Comment', file=registration_file)
        else:
            print('Name, Country, WCA ID, Date of Birth, Gender, Days, Events, Guests, Comment', file=registration_file)
        for competitor in registration_list:
            competitor_info = ''
            for column in range(1, column_ids[min(column_ids, key=column_ids.get)]):
                competitor_info = ''.join([competitor_info, competitor[column], ','])
            if not isinstance(competitor[len(competitor) - 1], str) and not isinstance(competitor[len(competitor) - 2], str):
                for day in competitor[len(competitor) - 2]:
                    competitor_info = ''.join([competitor_info, day, '/'])
                competitor_info = ''.join([competitor_info[:-1], ','])
                for events_per_day in competitor[len(competitor) - 1]:
                    competitor_info = ''.join([competitor_info, str(events_per_day), '+'])
            competitor_info = ''.join([competitor_info[:-1], ','])
            if competitor[0].isdigit():
                competitor_info = ''.join([competitor_info, competitor[0], ','])
            else:
                competitor_info = ''.join([competitor_info, '0,'])
            if not competitor[3]:
                competitor_info = ''.join([competitor_info, 'Newcomer (Check identification!)'])
            print(competitor_info, file=registration_file)

def create_schedule_file(competition_name, competition_name_stripped, full_schedule, event_info, competition_days, competition_start_day, timezone_utc_offset, formats, format_names, round_counter):
    specs_scoresheets = labels.Specification(210, 297, 1, 1, 210, 297)
    
    sheet = labels.Sheet(specs_scoresheets, write_schedule, border=False)
    schedule_file = '{}/{}Schedule.pdf'.format(competition_name, competition_name_stripped)
    
    sheet.add_labels((competition_name, competition_name_stripped, full_schedule, event_info, competition_days, competition_start_day, schedule_day, timezone_utc_offset, formats, format_names, round_counter) for schedule_day in range(competition_days))
    sheet.save(schedule_file)
    
def create_nametag_file(competitor_information, competition_name, competition_name_stripped, two_sided_nametags, create_only_nametags, result_string, event_ids, scrambler_list, event_dict, round_counter, group_list):
    # Format information for nametags: usual DIN-A4 layout with 2 rows of 4 nametags each with a size of 85x55mm
    specs = labels.Specification(210, 297, 2, 4, 85, 55)
    
    competitor_information_nametags = sorted(competitor_information, key=lambda x: ftfy.fix_text(x['name']))
    sheet = labels.Sheet(specs, write_name, border=True)
    sheet.add_labels((name, competition_name) for name in competitor_information_nametags)
    nametag_file = '{}/{}Nametags.pdf'.format(competition_name, competition_name_stripped)
    sheet.save(nametag_file)

    if two_sided_nametags:
        if create_only_nametags:
            for person in result_string:
                for competitor in competitor_information:
                    if person[0] == competitor['name']:
                        person[2] = competitor['personId']
                        break

        result_string_nametags = sorted(result_string, key=lambda x: ftfy.fix_text(x[0]))
        
        if len(result_string_nametags) % 2 == 1:
            result_string_nametags.append(('', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',),)
        for person in range(0, len(result_string_nametags)):
            if person % 2 == 0:
                swapping_id = person + 1
                swapping_person = result_string_nametags[swapping_id]
                result_string_nametags[swapping_id] = result_string_nametags[person]
                result_string_nametags[person] = swapping_person
        sheet = labels.Sheet(specs, write_grouping, border=True)
        sheet.add_labels((name, result_string_nametags, event_ids, scrambler_list, event_dict, round_counter, group_list) for name in result_string_nametags)
        grouping_nametag_file = '{}/{}-nametags-grouping.pdf'.format(competition_name, competition_name_stripped)
        sheet.save(grouping_nametag_file)

        pdf_splitter(grouping_nametag_file, competition_name)
        pdf_splitter(nametag_file, competition_name)

        paths1 = glob.glob('{}/{}Nametags_*.pdf'.format(competition_name, competition_name_stripped))
        paths2 = glob.glob('{}/{}-nametags-grouping_*.pdf'.format(competition_name, competition_name_stripped))
        paths = paths1 + paths2
        paths = sorted(paths, key=lambda x: x.split('_')[2])

        merger(nametag_file, paths)
        os.remove(grouping_nametag_file)

    if create_only_nametags:
        print('Nametags compiled into PDF: {0:d} label(s) output on {1:d} page(s).'.format(sheet.label_count, sheet.page_count))
        sys.exit()

    return sheet
    
def create_grouping_file(output_grouping, event_ids, event_dict, result_string):
    with open(output_grouping, 'w') as grouping_file:
        header = ',Name'
        all_events = ('333', '222', '444', '555', '666', '777', '333bf', '333fm', '333oh', '333ft', 'minx', 'pyram', 'clock', 'skewb', 'sq1', '444bf', '555bf', '333mbf')
        for event in all_events:
            if event in event_ids and event_ids[event] != 999:
                header = '{},{}'.format(header, event_dict[event])

        print(header, file = grouping_file)
        id = 0
        for person in result_string:
            id += 1
            grouping_list = '{},{}'.format(str(id), person[0])        
            for event in all_events:
                    if event in event_ids and event_ids[event] != 999:
                        grouping_list = '{},{}'.format(grouping_list, str(person[event_ids[event]]))
            print(grouping_list, file = grouping_file)
            
def create_scrambling_file(output_scrambling, competition_name, scrambler_list):
    with open(output_scrambling, 'w') as scrambling_file:
        header = 'Event,Group,Scrambler 1,Scrambler 2,Scrambler 3,Scrambler 4,Scrambler 5'

        print('Scrambling List {}'.format(competition_name), file = scrambling_file)

        print(header, file = scrambling_file)

        for scrambler in scrambler_list:
            if 'Fewest Moves' not in scrambler[0]:
                scramblers_clean = ()
                scramblers = (scrambler[2], scrambler[3], scrambler[4], scrambler[5], scrambler[6])
                sorted_scramblers = sorted(scramblers, key=lambda x: x.split()[-1])
                for scrambler_id in range(0, len(scramblers)):
                    scramblers_clean += (sorted_scramblers[scrambler_id].replace('dummy name', ''),)
                print(''.join(''.join([field, ',']) for field in [scrambler[0], str(scrambler[1]), scramblers_clean[0], scramblers_clean[1], scramblers_clean[2], scramblers_clean[3], scramblers_clean[4]])[:-1], file = scrambling_file)

def create_blank_sheets(competition_name, scrambler_signature, blank_sheets_round_name):
    specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)
    scoresheet_list = []
    sheet = labels.Sheet(specs_scoresheets, write_blank_sheets, border=False)
    scoresheet_file = '{}Blank_Scoresheets.pdf'.format(competition_name.replace('  ', ''))
    for scoresheet_count in range(0, 4):
        scoresheet_list.append({'name': '', 'country': '', 'personId': '', 'registrationId': ''})
    sheet.add_labels((name, competition_name, scrambler_signature, blank_sheets_round_name) for name in scoresheet_list)
    sheet.save(scoresheet_file)
    sys.exit()

def create_scoresheets(competition_name, competition_name_stripped, result_string, event_ids, event_info, event_dict, only_one_competitor, round_counter, competitor_information, scoresheet_competitor_name, scrambler_signature):
    # Format information for scoresheets: usual DIN-A4 layout with 2 rows of 2 scoresheets each with a size of 100x130mm
    specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)
    sheet = labels.Sheet(specs_scoresheets, write_scoresheets, border=False)
    scoresheet_file = '{}/{}Scoresheets.pdf'.format(competition_name, competition_name_stripped) 

    for event in event_info:
        if event['event'] != '333fm' and event['round'] == '1':
            scoresheet_list = []
            counter = 0
            result_string_sorted_events = result_string
            
            if event['event'] in events_ranking_by_speed:
                result_string_sorted_events = sorted(result_string[0], key=lambda x:x[event_ids[event['event']]])
            if (len(result_string_sorted_events) == 2):
                result_string_sorted_events = result_string_sorted_events[0]
            print(event, len(result_string_sorted_events))
            for name in result_string_sorted_events:
                if isinstance(name, list):
                    if str(name[event_ids[event['event']]]).isdigit():
                        scoresheet_list.append(name)
                        counter += 1
            
            # Fill empty pages with blank scoresheets
            if (counter % 4) != 0 and not only_one_competitor:
                for filling in range(0,4-counter%4):
                    scoresheet_list.append(('name', 'country', 'id', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''))
            sheet.add_labels((name, event_ids, event_dict, round_counter, competitor_information, competition_name, event, scrambler_signature) for name in scoresheet_list)
            
    if only_one_competitor:
        scoresheet_file = '{}/{}Scoresheets{}.pdf'.format(competition_name, competition_name_stripped, scoresheet_competitor_name.replace(' ', ''))
    sheet.save(scoresheet_file)

def create_scoresheets_second_rounds(competition_name, competitor_information, advancing_competitors, event_round_name, event_info, event_2, next_round_name, scrambler_signature):
    specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)
    sheet = labels.Sheet(specs_scoresheets, write_scoresheets_second_round, border=False)

    competitor_information = sorted(competitor_information, key = lambda x: x['ranking'])
    
    # Fill empty pages with blank scoresheets
    if (advancing_competitors % 4) != 0:
        for filling in range(0,(4-len(competitor_information))%4):
            competitor_information.append({'name': '', 'country': '', 'personId': '', 'registrationId': ''})
                
    # Create scoresheets
    sheet.add_labels((name, event_info, event_2, next_round_name, event_round_name, competition_name, scrambler_signature) for name in competitor_information)
    scoresheet_file = '{}/Scoresheets{}.pdf'.format(competition_name, event_round_name)
    sheet.save(scoresheet_file)
    
    print('')
    print('Scoresheets for {} sucessfully saved in folder {}.'.format(event_round_name, competition_name))
    sys.exit()

### Writer functions
def write_name(label, width, height, information):
    name = information[0]
    competition_name = information[1]
    
    # Write the title.
    label.add(shapes.String(width/2.0, height-20, competition_name, textAnchor='middle', fontSize=15, fontName='Arial'))
                            
    # Measure the width of the name and (possible) competitor roles and shrink the font size until it fits.
    font_size = 30
    text_width = width - 10
    name_width, font_size = enlarge_string_size(name['name'], text_width, font_size)
    
    role_font_size = 22
    role_width = stringWidth(name['role'], 'Arial', role_font_size)
    if name['role']:
        name_height = height - 53
        role_width, role_font_size = enlarge_string_size(name['role'], text_width, role_font_size)
    else:
        name_height = height - 70

    # Write name and role on nametag
    s = shapes.String(width/2.0, name_height, name['name'], fontName='Arial', textAnchor='middle')
    s.fontSize = font_size
    s.fillColor = colors.black
    label.add(s)

    r = shapes.String(width/2.0, height-85, name['role'], fontName='Arial', textAnchor='middle')
    r.fontSize = role_font_size
    r.fillColor = colors.red
    label.add(r)

    # Country
    label.add(shapes.String(width/2.0, height-110, name['country'], textAnchor='middle', fontSize=15, fontName='Arial'))

    # Addition of competition count. String used depending on amount of competitions
    competitions = ''
    if name['comp_count'] != 0:
        count = name['comp_count'] + 1
        if count % 10 == 1 and count != 11:
            competitions = '{}st Competition'.format(str(count))
        elif count % 10 == 2 and count != 12:
            competitions = '{}nd Competition'.format(str(count))
        elif count % 10 == 3 and count  != 13:
            competitions = '{}rd Competition'.format(str(count))
        else:
            competitions = '{}th Competition'.format(str(count))
    label.add(shapes.String(width/2.0, height-130, competitions, textAnchor='middle', fontSize = 12, fontName='Arial'))

    # Ranking
    ranking = ''
    if name['single'] != '0.00':
        ranking = '3x3x3: {} ({})'.format(str(name['single']), str(name['average']))
    label.add(shapes.String(width/2.0, height-145, ranking, textAnchor='middle', fontSize=12, fontName='Arial'))
    
### Write grouping on back of a nametag
# 'information' contains all information to create ONE nametag backside
def write_grouping(label, width, height, information):
    name = information[0]
    result_string_nametags = information[1]
    event_ids = information[2]
    scrambler_list = information[3]
    event_dict = information[4]
    round_counter = information[5]
    group_list = information[6]
    
    if not name[0]:
        return
    text_width = width - 12 - stringWidth('s = Scrambler', 'Arial', 9)
    width -= 235
    height -= 20
    name_and_id = ftfy.fix_text(name[0])
    
    # Add competitor name and WCA Id on top
    if name[2]:
        name_and_id = ''.join([name_and_id, ', ', name[2]])
    fontsize = 11
    name_width, fontsize = enlarge_string_size(name_and_id, text_width, fontsize)
    label.add(shapes.String(width, height, name_and_id, fontSize = fontsize, fontName='Arial'))
    
    # Determine if competitor is scrambler
    # if yes -> clearify abbreviation on nametag
    is_scrambler = False
    for event_scrambler in scrambler_list:
        for scrambler in event_scrambler:
            scrambler = str(scrambler)
            if ftfy.fix_text(name[0]) == ftfy.fix_text(scrambler.strip()): 
                scrambler_for_event = event_scrambler[0].split(' - ')[0].strip()
                scrambler_for_event = list(event_dict.keys())[list(event_dict.values()).index(scrambler_for_event)]
                is_scrambler = True
                break
    
    indent = 22
    height -= 30
    top_line = height
    # Table of events in which the competitor participates
    counter = 0
    if not is_scrambler:
        max_event_width = calculate_event_width(name, 0, 9, result_string_nametags, event_ids, event_dict)
    else:
        max_event_width = 80
    header = 'Event '
    header, header_width = enlarge_string_width(header, '', ' ', (indent + max_event_width - stringWidth('Group', 'Arial', 10)), 10)
    header = ''.join([header, 'Group'])
    header_height = height
    label.add(shapes.String(width, height+15, header, fontSize = 10, fontName='Arial'))
    does_scramble = False
    
    # Write all relevant events and group/scrambling information on nametag
    for group_event in range(3, len(name)):
        scrambling = []
        current_event = list(event_ids.keys())[list(event_ids.values()).index(group_event)]
        if name[group_event] or (is_scrambler and current_event == scrambler_for_event):
            if counter == 9:
                low_height = height
                width += max_event_width+30
                height = top_line
                if not is_scrambler:
                    max_event_width = calculate_event_width(name, 9, 18, result_string_nametags, event_ids, event_dict)
                else:
                    max_event_width = 80
                header = 'Event '
                header_width = stringWidth('Event ', 'Arial', 10) + stringWidth('Group', 'Arial', 10)
                header, header_width = enlarge_string_width(header, '', ' ', (indent + max_event_width - stringWidth('Group', 'Arial', 10)), 10)
                header = ''.join([header, 'Group'])

                label.add(shapes.String(width, height+15, header, fontSize = 10, fontName='Arial'))
                label.add(shapes.Line(width-4, height+23, width-4, low_height+10,trokeColor=colors.black))
                
            current_event = list(event_ids.keys())[list(event_ids.values()).index(group_event)]
            event_name = event_dict[current_event]
            label.add(shapes.String(width, height, event_name, fontSize = 8, fontName='Arial'))
                    
            for event_scrambler in scrambler_list:
                scrambling_event = event_scrambler[0].split(' - ')[0].strip()
                if event_scrambler[0].strip()[-1:] == '1' or round_counter[current_event] == 1:
                    scrambling_event = list(event_dict.keys())[list(event_dict.values()).index(scrambling_event)]
                    for scrambler in event_scrambler:
                        if current_event == scrambling_event:
                            scrambler = str(scrambler)
                            if ftfy.fix_text(name[0]) == ftfy.fix_text(scrambler.strip()): 
                                scrambling.append(event_scrambler[1])
            
            group_string, group_number = '', ''
            if name[group_event]:
                group_number = name[group_event]
            for event_infos in group_list:
                if event_infos[0] == current_event and event_infos[1][-1:] == '1':
                    group_count = event_infos[2]
            if scrambling:
                does_scramble = True
                for rounds in range(1,group_count+1):
                    if str(rounds) != group_number and rounds in scrambling:
                        group_string = '{}s{},'.format(group_string, str(rounds))
                    elif str(rounds) == group_number:
                        group_string = '{}{},'.format(group_string, str(group_number))
                group_string = group_string[:-1]
            else:
                group_string = str(group_number)

            group_string, group_width = enlarge_string_width(group_string, ' ', '', 40, 8)
            label.add(shapes.String(width+max_event_width-18, height, group_string, fontSize = 8, fontName='Arial'))
            height -= 11
            counter += 1
    if does_scramble:
        label.add(shapes.String(180, 140, 's = Scrambler', fontSize = 8, fontName='Arial'))

def calculate_event_width(name, min, limit, result_string_nametags, event_ids, event_dict):
    max_event_width = 0
    counter = 0
    if limit > len(name):
        limit = len(name)
    for person in result_string_nametags:
        if name[0] == person[0]:
            for group_event in range(3, len(name)):
                if counter == limit:
                    return max_event_width
                if name[group_event]:
                    group_event_id = list(event_ids.keys())[list(event_ids.values()).index(group_event)]
                    event_width = stringWidth(event_dict[group_event_id], 'Arial', 9)
                    if event_width > max_event_width and counter >= min:
                        max_event_width = event_width
                    counter += 1
    return max_event_width

# Schedule writer
# 'information' contains all information needed for all competition days
# however, write_schedule only creates the schedule for one day
def write_schedule(label, width, height, information):
    competition_name = information[0]
    competition_name_stripped = information[1]
    full_schedule = information[2]
    event_info = information[3]
    competition_days = information[4]
    competition_start_day = information[5]
    schedule_day = information[6]
    timezone_utc_offset = information[7]
    formats = information[8]
    format_names = information[9]
    round_counter = information[10]
    year = int(competition_start_day.split('-')[0])
    month = int(competition_start_day.split('-')[1])
    day = int(competition_start_day.split('-')[2])
    
    competition_day_date = datetime.date(year, month, day) + datetime.timedelta(days=schedule_day)
    competition_day = str(competition_day_date)
    
    text_width = width - 10

    font_size = 40
    competition_name_width, font_size = enlarge_string_size(competition_name, text_width, font_size)
    label.add(shapes.String(width/2, height-70, competition_name, textAnchor='middle', fontSize=font_size, fontName='Arial'))
    
    day_id = datetime.date(year, month, day).weekday() + schedule_day
    if day_id > 7:
        day_id -= 7

    day_name = '{}, {}. {}'.format(calendar.day_name[day_id], str(competition_day_date.day), calendar.month_name[month])
    day_name_width = stringWidth(day_name, 'Arial', font_size)
    font_size = 35
    competition_name_width, font_size = enlarge_string_size(day_name, text_width, font_size)
    label.add(shapes.String(width/2, height-120, day_name, textAnchor='middle', fontSize=font_size, fontName='Arial'))
    
    # Add header of table
    header_font_size = 16
    label.add(shapes.Rect(10,height-166,52, 26, fillColor=colors.white))
    label.add(shapes.String(20, height-160, 'Start', fontSize=header_font_size, fontName='Arial'))
    label.add(shapes.Rect(62,height-166,52, 26, fillColor=colors.white))
    label.add(shapes.String(71, height-160, 'Stop', fontSize=header_font_size, fontName='Arial'))
    label.add(shapes.Rect(112,height-166,160, 26, fillColor=colors.white))
    label.add(shapes.String(192, height-160, 'Event', fontSize=header_font_size, textAnchor='middle', fontName='Arial'))
    label.add(shapes.Rect(272,height-166,115, 26, fillColor=colors.white))
    label.add(shapes.String(330, height-160, 'Timelimit', fontSize=header_font_size, textAnchor='middle', fontName='Arial'))
    label.add(shapes.Rect(387,height-166,190, 26, fillColor=colors.white))
    label.add(shapes.String(485, height-160, 'Format', fontSize=header_font_size, textAnchor='middle', fontName='Arial'))
    
    # Add each event for the selected day
    height += 13
    for event in full_schedule:
        double_height = False
        event_day = event['startTime'].split('T')[0]
        
        # Determination and validation of a lot of event specific information (start and end time, timelimit, cutoff, advancing competitors etc.)
        if event_day == competition_day:
            event_start = event['startTime'].split('T')[1][:-1]
            event_start = '{}:{}'.format(event_start.split(':')[0], event_start.split(':')[1])
            event_end = event['endTime'].split('T')[1][:-1]
            event_end = '{}:{}'.format(event_end.split(':')[0], event_end.split(':')[1])
            event_name = event['event_name']

            limit, round_format, seconds, minutes, seconds_cutoff, minutes_cutoff = '', '', '', '', '', ''
            for events in event_info:
                if event['event_id'] == events['event'] and event['event_name'].split(' - ')[1][-1:] == events['round']:
                    minutes, seconds = format_minutes_and_seconds(events['limit'])
                    limit = '{}:{}'.format(minutes, seconds)
                    if events['cumulative']:                            
                        limit = ''.join([limit, ' cumulative'])
                    if events['cutoff_number'] != 0:
                        event_name = event_name.replace('Round', 'Combined Round')
                    
                        format_name = 'bo{}'.format(str(events['cutoff_number']))
                        cutoff_limit  = events['cutoff']
                        minutes_cutoff, seconds_cutoff = divmod(cutoff_limit, 60)
                        minutes_cutoff = str(minutes_cutoff)
                        seconds_cutoff = str(seconds_cutoff) 
                        seconds_cutoff = enlarge_string(seconds_cutoff, '0', 2)
                        
                        round_format = '{} (< {}:{}) / '.format(format_names[format_name], minutes_cutoff, seconds_cutoff)   
                    round_format += format_names[str(events['format'])]
                    
                    if events['advancing']:
                        round_format += ' ({} proceed)'.format(events['advancing'])
            if not 'Attempt' in event['event_name']:
                round_number = event['event_name'][-1:]
            else:
                round_number = event['event_name'].split(' - ')[1][-1:]
            if round_number == str(round_counter[event['event_id']]) or round_number == '3':
                replace_string = ' Round {}'.format(str(round_number))
                if round_number == '3' and round_counter[event['event_id']] != 3:
                    event_name = event_name.replace(replace_string, ' Semi Final')
                else:
                    event_name = event_name.replace(replace_string, ' Final')
            
            event_name = event_name.replace('Round 1', 'First Round')
            event_name = event_name.replace('Round 2', 'Second Round')
                    
            event_font_size = 12
            box_height = event_font_size + 4
            set_box_height = 0
            if stringWidth(event_name, 'Arial', event_font_size) > 155 or stringWidth(round_format, 'Arial', event_font_size) > 190:
                double_height = True
                
                set_box_height = box_height
                box_height += box_height
                event_name_string1 = event_name
                event_name_string2 = ''
                format_string1 = round_format
                format_string2 = ''
                if stringWidth(event_name, 'Arial', event_font_size) > 155:
                    event_name_string1, event_name_string2 = create_two_strings_out_of_one(event_name, event_font_size, 155)
                if event_name_string1[-2:] == '- ':
                    event_name_string1 = event_name_string1[:-2]
                if event_name_string2[:1] == '-':
                    event_name_string2 = event_name_string2[2:]
                if stringWidth(round_format, 'Arial', event_font_size) > 190:
                    format_string1, format_string2 = create_two_strings_out_of_one(round_format, event_font_size, 190)
            
            # Actual printing of the event row
            label.add(shapes.Rect(10,height-195-set_box_height,52, box_height, fillColor=colors.white))
            label.add(shapes.Rect(62,height-195-set_box_height,52, box_height, fillColor=colors.white))
            label.add(shapes.Rect(112,height-195-set_box_height,160, box_height, fillColor=colors.white))
            label.add(shapes.Rect(272,height-195-set_box_height,115, box_height, fillColor=colors.white))
            label.add(shapes.Rect(387,height-195-set_box_height,190, box_height, fillColor=colors.white))
    
            if double_height:
                label.add(shapes.String(192, height-190, event_name_string1, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
                label.add(shapes.String(192, height-190-set_box_height, event_name_string2, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
                if not format_string2:
                    label.add(shapes.String(485, height-190-set_box_height/2, format_string1, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
                else:
                    label.add(shapes.String(485, height-190, format_string1, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
                label.add(shapes.String(485, height-190-set_box_height, format_string2, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
            else:
                label.add(shapes.String(192, height-190, event_name, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
                label.add(shapes.String(485, height-190, round_format, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
            label.add(shapes.String(21, height-190-set_box_height/2, event_start, fontSize=event_font_size, fontName='Arial'))
            label.add(shapes.String(71, height-190-set_box_height/2, event_end, fontSize=event_font_size, fontName='Arial'))
            label.add(shapes.String(330, height-190-set_box_height/2, limit, textAnchor='middle', fontSize=event_font_size, fontName='Arial'))
            
            if double_height:
                height -= (event_font_size + 4) * 2
            else:
                height -= event_font_size + 4

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
        group = 'Group {}'.format(str(name[event_ids[event['event']]]))
        
        event_width, font_size_event, limit = scoresheet_limit(event_name, event['limit'], event['cumulative'], text_width)
    else:
        event_name, group, round = '', '', ''
        limit = 'Result'
    cutoff_time, label = scoresheet_event_name(event['cutoff'], event['cutoff'], event_name, label, width, height, font_size_event)

    # Competitor information: name, WCA ID and registration id
    competitor_name, registration_id, id = '', '', ''

    for person in competitor_information:
        if (name[2] and ftfy.fix_text(name[2]) == ftfy.fix_text(person['personId'])) or (ftfy.fix_text(name[0]) == ftfy.fix_text(person['name'])):
            competitor_name = person['name']
            registration_id = str(person['registration_id'])
            id = person['personId']
            if id == '':
                id = 'New Competitor'
            else:
                id = '     {}'.format(id)
    
    scoresheet_competitor_and_competition_name(competitor_name, competition_name, label, height, width)

    label.add(shapes.String(width-78, height-16, id, fontSize=10, fontName='Arial'))
    
    scoresheet_body(
            registration_id, group, limit, \
            font_size_limit, label, \
            height, width, scrambler_signature, \
            event['format'], event['event'], str(event['cutoff_number']), \
            cutoff_time, name \
            )

def write_scoresheets_second_round(label, width, height, information):
    name = information[0]
    event_info = information[1]
    event_2 = information[2]
    next_round_name = information[3]
    event_name = information[4]
    competition_name = information[5]
    scrambler_signature = information[6]
    
    # Dummy dict
    event = {'event': '', 'cutoff': ''}
    
    # WCA ID
    if name['name'] and not name['personId']:
        id = 'New Competitor'
    else:
        id = '     {}'.format(name['personId'])
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
    
    event_width, font_size_event, limit = scoresheet_limit(event_name, limit, cumulative, text_width)
    if not name['name']:
        event_name, group, round = '', '', ''
        limit = 'Result'
    cutoff_time, label = scoresheet_event_name(cutoff, limit, event_name, label, width, height, font_size_event)
    
    # Competitor information: name, WCA ID and registration id
    competitor_name, registration_id, ranking = '', '', ''
    if name['name']:
        competitor_name = name['name']
        registration_id = str(name['registration_id'])
        ranking = str(name['ranking'])

    scoresheet_competitor_and_competition_name(competitor_name, competition_name, label, height, width)

    ranking = enlarge_string(ranking, ' ', 3)
    label.add(shapes.String(width-22, height-80, ranking, fontSize=12, fontName='Arial'))
    
    scoresheet_body(
            registration_id, '', limit, \
            font_size_limit, label, \
            height, width, scrambler_signature, \
            format, event, cutoff_number, \
            cutoff_time, name \
            )
    
def write_blank_sheets(label, width, height, information):
    name = information[0]
    competition_name = information[1]
    scrambler_signature = information[2]
    blank_sheets_round_name = information[3]
    
    scoresheet_blank_header(label, height, width, competition_name, blank_sheets_round_name)
    
    height = scoresheet_results_header(label, '', 0, 10, height, scrambler_signature)

    # Creation of result boxes, depending on # of attempts for event and round
    height = scoresheet_result_boxes(label, height, width, '5', '', 0, 0, name, scrambler_signature)
    
    # Add unlabeled box for extras and provisional solves
    scoresheet_extra(label, height, width, scrambler_signature)
