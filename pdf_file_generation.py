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
        
    additional functions for scoresheets can be found in scoresheets_functions.py
'''

from modules import *
from grouping_scrambling_functions import EventsRankingBySpeed

if not os.path.isfile('Trebuchet.ttf'):
    print("ERROR!! File 'Trebuchet.ttf' does not exist. Please download from \n",
           "https://www.fontpalace.com/font-download/Trebuchet+MS/\n and add to",
           "{}/.".format(os.path.dirname(os.path.abspath(__file__))))
    sys.exit()

registerFont(TTFont('Arial', 'Trebuchet.ttf'))

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

def enlarge_string(input_string, add_string, string_length):
    while len(input_string) < string_length:
        input_string = ''.join([add_string, input_string])
    return input_string
    
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

def format_minutes_and_seconds(time_string):
    minutes, seconds = divmod(time_string, 60)
    minutes = str(minutes)
    seconds = enlarge_string(str(seconds), '0', 2)
    return (minutes, seconds)

def create_blank_sheets(write_blank_sheets, competition_name, scrambler_signature, blank_sheets_round_name):
    specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)
    scoresheet_list = []
    sheet = labels.Sheet(specs_scoresheets, write_blank_sheets, border=False)
    scoresheet_file = '{}Blank_Scoresheets.pdf'.format(competition_name.replace('  ', ''))
    for scoresheet_count in range(0, 4):
        scoresheet_list.append({'name': '', 'country': '', 'personId': '', 'registrationId': ''})
    sheet.add_labels((name, competition_name, scrambler_signature, blank_sheets_round_name) for name in scoresheet_list)
    sheet.save(scoresheet_file)
    sys.exit()

def create_scoresheets(competition_name, competition_name_stripped, result_string, event_ids, event_info, event_dict, only_one_competitor, round_counter, competitor_information, event, scoresheet_competitor_name, scrambler_signature):
    # format information for scoresheets: usual DIN-A4 layout with 2 rows of 2 scoresheets each with a size of 100x130mm
    specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)
    sheet = labels.Sheet(specs_scoresheets, write_scoresheets, border=False)
    scoresheet_file = '{}/{}Scoresheets.pdf'.format(competition_name, competition_name_stripped) 

    for event in event_info:
        if event['event'] != '333fm' and event['round'] == '1':
            scoresheet_list = []
            counter = 0
            result_string_sorted_events = result_string
            
            if event['event'] in EventsRankingBySpeed.events:
                result_string_sorted_events = sorted(result_string, key=lambda x:x[event_ids[event['event']]])
            for name in result_string_sorted_events:
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

def create_scoresheets_second_rounds(write_scoresheets_second_round, competition_name, competitor_information, advancing_competitors, event_round_name, event_info, event_2, next_round_name, event, scrambler_signature):
    specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)
    sheet = labels.Sheet(specs_scoresheets, write_scoresheets_second_round, border=False)

    competitor_information = sorted(competitor_information, key = lambda x: x['ranking'])
    
    # Fill empty pages with blank scoresheets
    if (advancing_competitors % 4) != 0:
        for filling in range(0,(4-len(competitor_information))%4):
            competitor_information.append({'name': '', 'country': '', 'personId': '', 'registrationId': ''})
                
    # Create scoresheets
    sheet.add_labels((name, event_info, event_2, next_round_name, event_round_name, competition_name, event, scrambler_signature) for name in competitor_information)
    scoresheet_file = '{}/Scoresheets{}.pdf'.format(competition_name, event_round_name)
    sheet.save(scoresheet_file)
    
    print('')
    print('Scoresheets for {} sucessfully saved in folder {}.'.format(event_round_name, competition_name))
    sys.exit()

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

def create_scrambling_file(output_scrambling, competition_name, scramblerlist):
    with open(output_scrambling, 'w') as scrambling_file:
        header = 'Event,Group,Scrambler 1,Scrambler 2,Scrambler 3,Scrambler 4,Scrambler 5'

        print('Scrambling List {}'.format(competition_name), file = scrambling_file)

        print(header, file = scrambling_file)

        for scrambler in scramblerlist:
            if 'Fewest Moves' not in scrambler[0]:
                scramblers_clean = ()
                scramblers = (scrambler[2], scrambler[3], scrambler[4], scrambler[5], scrambler[6])
                sorted_scramblers = sorted(scramblers, key=lambda x: x.split()[-1])
                for scrambler_id in range(0, len(scramblers)):
                    scramblers_clean += (sorted_scramblers[scrambler_id].replace('dummy name', ''),)
                print(''.join(''.join([field, ',']) for field in [scrambler[0], str(scrambler[1]), scramblers_clean[0], scramblers_clean[1], scramblers_clean[2], scramblers_clean[3], scramblers_clean[4]])[:-1], file = scrambling_file)
                
def create_grouping_file(output_grouping, event_ids, event_dict, result_string):
    with open(output_grouping, 'w') as grouping_file:
        header = ',Name'
        for event in ('333', '222', '444', '555', '666', '777', '333bf', '333fm', '333oh', '333ft', 'minx', 'pyram', 'clock', 'skewb', 'sq1', '444bf', '555bf', '333mbf'):
            if event in event_ids and event_ids[event] != 999:
                header = '{},{}'.format(header, event_dict[event])

        print(header, file = grouping_file)
        id = 0
        for person in result_string:
            id += 1
            grouping_list = '{},{}'.format(str(id), person[0])        
            for event in ('333', '222', '444', '555', '666', '777', '333bf', '333fm', '333oh', '333ft', 'minx', 'pyram', 'clock', 'skewb', 'sq1', '444bf', '555bf', '333mbf'):
                    if event in event_ids and event_ids[event] != 999:
                        grouping_list = '{},{}'.format(grouping_list, str(person[event_ids[event]]))
            print(grouping_list, file = grouping_file)
            
def create_nametag_file(competitor_information, competition_name, competition_name_stripped, two_sided_nametags, create_only_nametags, result_string, event_ids, scramblerlist, event_dict, only_one_competitor, round_counter, group_list, scoresheet_competitor_name):
    # format information for nametags: usual DIN-A4 layout with 2 rows of 4 nametags each with a size of 85x55mm
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
        sheet.add_labels((name, result_string_nametags, event_ids, scramblerlist, event_dict, round_counter, group_list) for name in result_string_nametags)
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
    
def get_grouping_from_file(grouping_file_name, event_dict, event_ids, only_one_competitor, scoresheet_competitor_name):
    result_string = []
    with open(grouping_file_name, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        file_information = list(reader)
    counter = 1
    for events in file_information[0]:
        if counter > 2:
            event_short = list(event_dict.keys())[list(event_dict.values()).index(events)]
            if event_short in event_ids:
                event_ids.update({event_short: counter})
        counter += 1
    grouping_competitor = ''
    for person in range(0, len(file_information)):
        if file_information[person][0] and 'Name' not in file_information[person][1]:
            file_information[person][0] = file_information[person][1]
            file_information[person].insert(2, '')
            result_string.append(file_information[person])
            if only_one_competitor:
                if ftfy.fix_text(scoresheet_competitor_name) == ftfy.fix_text(file_information[person][0]):
                    grouping_competitor = file_information[person]
                    break
    if only_one_competitor:
        if grouping_competitor:
            return [grouping_competitor]
        else:
            print('')
            print("ERROR!! Competitor '{}' not found.".format(scoresheet_competitor_name))
            sys.exit()
    return result_string

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
    
### Write grouping on back of a nametag
# 'information' contains all information to create ONE back page
def write_grouping(label, width, height, information):
    name = information[0]
    result_string_nametags = information[1]
    event_ids = information[2]
    scramblerlist = information[3]
    event_dict = information[4]
    round_counter = information[5]
    group_list = information[6]
    
    if not name[0]:
        return
        
    text_width = width - 12 - stringWidth('s = Scrambler', 'Arial', 9)
    width -= 235
    height -= 20
    name_and_id = ftfy.fix_text(name[0])
    
    # add competitor name and WCA Id on top
    if name[2]:
        name_and_id = ''.join([name_and_id, ', ', name[2]])
    fontsize = 11
    name_width, fontsize = enlarge_string_size(name_and_id, text_width, fontsize)
    label.add(shapes.String(width, height, name_and_id, fontSize = fontsize, fontName='Arial'))
    
    # determine if competitor is scrambler
    # if yes -> clearify abbreviation on nametag
    is_scrambler = False
    for event_scrambler in scramblerlist:
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
    
    # table of events in which the competitor participates
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
    
    # write all relevant events and group/scrambling information on nametag
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
                    
            for event_scrambler in scramblerlist:
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

### Function to create schedule PDF
# 'information' contains all information needed for all competition days
# however, write_schedule only creates a the schedule for one day
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
    comp_name_width, font_size = enlarge_string_size(competition_name, text_width, font_size)
    label.add(shapes.String(width/2, height-70, competition_name, textAnchor='middle', fontSize=font_size, fontName='Arial'))
    
    day_id = datetime.date(year, month, day).weekday() + schedule_day
    if day_id > 7:
        day_id -= 7

    day_name = '{}, {}. {}'.format(calendar.day_name[day_id], str(competition_day_date.day), calendar.month_name[month])
    day_name_width = stringWidth(day_name, 'Arial', font_size)
    font_size = 35
    comp_name_width, font_size = enlarge_string_size(day_name, text_width, font_size)
    label.add(shapes.String(width/2, height-120, day_name, textAnchor='middle', fontSize=font_size, fontName='Arial'))
    
    # add header of table
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
    
    # add each event for the selected day
    height += 13
    for event in full_schedule:
        double_height = False
        event_day = event['startTime'].split('T')[0]
        
        # determination and validation of a lot of event specific information (start and end time, timelimit, cutoff, advancing competitors etc.)
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
                        round_format = '({} proceed)'.format(events['advancing'])
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
            
            # actual printing of the event row
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

### Creation of schedule file
def create_schedule_file(competition_name, competition_name_stripped, full_schedule, event_info, competition_days, competition_start_day, timezone_utc_offset, formats, format_names, round_counter):
    specs_scoresheets = labels.Specification(210, 297, 1, 1, 210, 297)
    
    sheet = labels.Sheet(specs_scoresheets, write_schedule, border=False)
    schedule_file = '{}/{}Schedule.pdf'.format(competition_name, competition_name_stripped)
    
    sheet.add_labels((competition_name, competition_name_stripped, full_schedule, event_info, competition_days, competition_start_day, schedule_day, timezone_utc_offset, formats, format_names, round_counter) for schedule_day in range(competition_days))
    sheet.save(schedule_file)

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

    scoresheet_body(
            registration_id, group, limit, \
            font_size_limit, label, \
            height, width, scrambler_signature, \
            event['format'], event['event'], str(event['cutoff_number']), \
            cutoff_time, name \
            )

def scoresheet_body(registration_id, group, limit, font_size_limit, label, height, width, scrambler_signature, event_format, event_name, cutoff_number, cutoff_time, name):
    if registration_id:
        registration_id = enlarge_string(registration_id, ' ', 3)
        label.add(shapes.Rect(10,height-83,22, 15, fillColor=colors.white))
        label.add(shapes.String(14, height-79, registration_id, fontSize=10, fontName='Arial'))
    label.add(shapes.String(width-50, height-80, group, fontSize=12, fontName='Arial'))

    # making header for result-boxes: # attempt, result (with (cumulative) limits), judge and competitor signature
    limit_width = stringWidth(limit, 'Arial', font_size_limit)
    height = scoresheet_results_header(label, limit, limit_width, font_size_limit, height, scrambler_signature)

    # creation of result boxes, depending on # of attempts for event and round
    height = scoresheet_result_boxes(label, height, width, event_format, event_name, cutoff_number, cutoff_time, name, scrambler_signature)
    
    # add unlabelled box for extras and provisional solves
    scoresheet_extra(label, height, width, scrambler_signature)
