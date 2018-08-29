import os, sys, getpass, ftfy, unicodedata, random, labels, glob, datetime, calendar, pytz
from collections import Counter
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.graphics import shapes
from reportlab.lib import colors

registerFont(TTFont('Arial', 'Trebuchet.ttf'))

wcif_file = ''

def quit_program(wcif_file):
    if isinstance(wcif_file, str):
        if os.path.exists(wcif_file):
            os.remove(wcif_file)
    else:
        try: 
            wcif_file
        except NameError: 
            wcif_file = ''
        else:
            os.remove(wcif_file.name)
    sys.exit()

def create_blank_sheets(write_blank_sheets, competition_name):
    specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)
    scoresheet_list = []
    sheet = labels.Sheet(specs_scoresheets, write_blank_sheets, border=False)
    scoresheet_file = competition_name.replace(' ', '') + 'Blank_Scoresheets.pdf'
    print('Creating blank sheets')
    for scoresheet_count in range(0, 4):
        scoresheet_list.append({'name': '', 'country': '', 'personId': '', 'registrationId': ''})
    sheet.add_labels((name, competition_name) for name in scoresheet_list)
    sheet.save(scoresheet_file)
    quit_program(wcif_file)

def create_scoresheets(competition_name, competition_name_stripped, result_string, event_ids, event_info, event_dict, only_one_competitor, round_counter, competitor_information, event, write_scoresheets, scoresheet_competitor_name):
    # format information for scoresheets: usual DIN-A4 layout with 2 rows of 2 scoresheets each with a size of 100x130mm
    specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)
    print('Creating scoresheets...')
    sheet = labels.Sheet(specs_scoresheets, write_scoresheets, border=False)
    scoresheet_file = competition_name + '/' + competition_name_stripped + 'Scoresheets.pdf'

    for event in event_info:
        if event['event'] != '333fm' and event['round'] == '1':
            scoresheet_list = []
            counter = 0
            for name in result_string:
                if str(name[event_ids[event['event']]]).isdigit():
                    scoresheet_list.append(name)
                    counter += 1
            # Fill empty pages with blank scoresheets
            if (counter % 4) != 0 and not only_one_competitor:
                for filling in range(0,4-counter%4):
                    scoresheet_list.append(('name', 'country', 'id', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''))
            sheet.add_labels((name, event_ids, event_dict, round_counter, competitor_information, competition_name, event) for name in scoresheet_list)
    if only_one_competitor:
        scoresheet_file = competition_name + '/' + competition_name_stripped + 'Scoresheets' + scoresheet_competitor_name.replace(' ', '') + '.pdf' 
    sheet.save(scoresheet_file)

def create_scoresheets_second_rounds(write_scoresheets_second_round, competition_name, competitor_information, advancing_competitors, event_round_name, event_info, event_2, next_round_name, event):
    specs_scoresheets = labels.Specification(210, 297, 2, 2, 100, 130)
    print('Creating scoresheets for ' + event_round_name + '...')
    sheet = labels.Sheet(specs_scoresheets, write_scoresheets_second_round, border=False)
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
    sheet.add_labels((name, event_info, event_2, next_round_name, event_round_name, competition_name, event) for name in scoresheet_list)
    scoresheet_file = competition_name + '/' + 'Scoresheets' + event_round_name + '.pdf'
    sheet.save(scoresheet_file)
    
    print('')
    print('Scoresheets for ' + event_round_name + ' sucessfully saved in folder ' + competition_name + '.')
    quit_program(wcif_file)


def create_registration_file(output_registration, registration_list, column_ids, competition_days):
    with open(output_registration, 'w') as registration_file:
        print('Name, Country, WCA ID, Date of Birth, Gender, Days, Events, Guests, Comment, Check Box', file=registration_file)
        for competitor in registration_list:
            competitor_info = ''
            for column in range(1, column_ids[min(column_ids, key=column_ids.get)]):
                competitor_info += competitor[column] + ','
            for day in competitor[len(competitor) - 2]:
                competitor_info += day + '/'
            competitor_info = competitor_info[:-1]
            competitor_info += ','
            for events_per_day in competitor[len(competitor) - 1]:
                competitor_info += str(events_per_day) + '+'
            competitor_info = competitor_info[:-1]
            competitor_info += ','
            if competitor[0].isdigit():
                competitor_info += competitor[0] + ','
            else:
                competitor_info += '0,'
            if not competitor[3]:
                competitor_info += 'Newcomer (Check identification!)'
            competitor_info += ','
            print(competitor_info, file=registration_file)

def create_scrambling_file(output_scrambling, competition_name, scramblerlist):
    with open(output_scrambling, 'w') as scrambling_file:
        header = 'Event, Group, Scrambler 1, Scrambler 2, Scrambler 3, Scrambler 4, Scrambler 5'

        print('Scrambling List ' + competition_name, file = scrambling_file)

        print(header, file = scrambling_file)

        for scrambler in scramblerlist:
            if 'Fewest Moves' not in scrambler[0]:
                scramblers_clean = ()
                scramblers = (scrambler[2], scrambler[3], scrambler[4], scrambler[5], scrambler[6])
                sorted_scramblers = sorted(scramblers, key=lambda x: x.split()[-1])
                for scrambler_id in range(0, len(scramblers)):
                    scramblers_clean += (sorted_scramblers[scrambler_id].replace('dummy name', ''),)
                print(scrambler[0], ',', scrambler[1], ',', scramblers_clean[0], ',', scramblers_clean[1], ',', scramblers_clean[2], ',', scramblers_clean[3], ',', scramblers_clean[4], file = scrambling_file)
                
def create_grouping_file(output_grouping, event_ids, event_dict, result_string):
    with open(output_grouping, 'w') as grouping_file:
        header = ' ,Name'
        for event in ('333', '222', '444', '555', '666', '777', '333bf', '333fm', '333oh', '333ft', 'minx', 'pyram', 'clock', 'skewb', 'sq1', '444bf', '555bf', '333mbf'):
            if event in event_ids and event_ids[event] != 999:
                header += ',' + event_dict[event]

        print(header, file = grouping_file)

        id = 0
        for person in result_string:
            id += 1
            grouping_list = str(id) + ',' + person[0]
        
            for event in ('333', '222', '444', '555', '666', '777', '333bf', '333fm', '333oh', '333ft', 'minx', 'pyram', 'clock', 'skewb', 'sq1', '444bf', '555bf', '333mbf'):
                    if event in event_ids and event_ids[event] != 999:
                        grouping_list += ',' + str(person[event_ids[event]])

            print(grouping_list, file = grouping_file)
            
def create_nametag_file(competitor_information, competition_name, competition_name_stripped, two_sided_nametags, create_only_nametags, result_string, event_ids, scramblerlist, grouping_file_name, event_dict, only_one_competitor, round_counter, group_list, scoresheet_competitor_name):
    # format information for nametags: usual DIN-A4 layout with 2 rows of 4 nametags each with a size of 85x55mm
    specs = labels.Specification(210, 297, 2, 4, 85, 55)
    
    competitor_information_nametags = sorted(competitor_information, key=lambda x: x['name'])
    sheet = labels.Sheet(specs, write_name, border=True)
    sheet.add_labels((name, competition_name) for name in competitor_information_nametags)
    nametag_file = competition_name + '/' + competition_name_stripped + '-nametags.pdf'
    sheet.save(nametag_file)

    if two_sided_nametags:
        if create_only_nametags:
            result_string = get_grouping_from_file(grouping_file_name, event_dict, event_ids, only_one_competitor, scoresheet_competitor_name)
            for person in result_string:
                for competitor in competitor_information:
                    if person[0] == competitor['name']:
                        person[2] = competitor['personId']
                        break

        result_string_nametags = sorted(result_string, key=lambda x: x[0])
        
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
        grouping_nametag_file = competition_name + '/' + competition_name_stripped + '-nametags-grouping.pdf'
        sheet.save(grouping_nametag_file)

        pdf_splitter(grouping_nametag_file, competition_name)
        pdf_splitter(nametag_file, competition_name)

        paths1 = glob.glob(competition_name + '/' + competition_name_stripped + '-nametags_*.pdf')
        paths2 = glob.glob(competition_name + '/' + competition_name_stripped + '-nametags-grouping_*.pdf')
        paths = paths1 + paths2
        paths = sorted(paths, key=lambda x: x.split('_')[2])

        merger(nametag_file, paths)
        os.remove(grouping_nametag_file)

    if create_only_nametags:
        quit_program(wcif_file)

    return sheet
    
def get_grouping_from_file(grouping_file_name, event_dict, event_ids, only_one_competitor, scoresheet_competitor_name):
    import csv
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
    if only_one_competitor:
        if grouping_competitor:
            return [grouping_competitor]
        else:
            print('')
            print("ERROR!! Competitor '" + scoresheet_competitor_name + "' not found.")
            quit_program(wcif_file)
    return result_string
    
def pdf_splitter(path, competition_name):
    fname = os.path.splitext(os.path.basename(path))[0]
 
    pdf = PdfFileReader(path)
    for page in range(pdf.getNumPages()):
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf.getPage(page))
 
        output_filename = competition_name + '/{}_page_{}.pdf'.format(
            fname, page+1)
 
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)
            
def merger(output_path, input_paths):
    pdf_merger = PdfFileMerger()
    file_handles = []
 
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
    name_width = stringWidth(name['name'], 'Arial', font_size)
    
    while name_width > text_width:
        font_size *= 0.95
        name_width = stringWidth(name['name'], 'Arial', font_size)
    
    role_font_size = 22
    role_width = stringWidth(name['role'], 'Arial', role_font_size)
    if name['role']:
        name_height = height - 53
        while role_width > text_width:
            role_font_size *= 0.95
            role_width = stringWidth(name['role'], 'Arial', role_font_size)
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
            competitions = str(count) + 'st Competition'
        elif count % 10 == 2 and count != 12:
            competitions = str(count) + 'nd Competition'
        elif count % 10 == 3 and count  != 13:
            competitions = str(count) + 'rd Competition'
        else:
            competitions = str(count) + 'th Competition'
    label.add(shapes.String(width/2.0, height-130, competitions, textAnchor='middle', fontSize = 12, fontName='Arial'))

    # Ranking
    ranking = ''
    if name['single'] != '0.00':
        ranking = '3x3x3: ' + str(name['single']) + ' (' + str(name['average']) + ')'
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
    if name[2]:
        name_and_id += ', ' + name[2]
    fontsize = 11
    name_width = stringWidth(name_and_id, 'Arial', fontsize)
    while name_width > text_width:
        fontsize *= 0.95
        name_width = stringWidth(name_and_id, 'Arial', fontsize)
    label.add(shapes.String(width, height, name_and_id, fontSize = fontsize, fontName='Arial'))
    
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
    
    counter = 0
    if not is_scrambler:
        max_event_width = calculate_event_width(name, 0, 9, result_string_nametags, event_ids, event_dict)
    else:
        max_event_width = 80
    header = 'Event '
    header_width = stringWidth('Event ', 'Arial', 10) + stringWidth('Group', 'Arial', 10)
    while header_width < (indent + max_event_width - stringWidth('Group', 'Arial', 10)):
        header += ' '
        header_width = stringWidth(header, 'Arial', 10)
    header += 'Group'
    header_height = height
    label.add(shapes.String(width, height+15, header, fontSize = 10, fontName='Arial'))
    does_scramble = False
    
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
                while header_width < (indent + max_event_width - stringWidth('Group', 'Arial', 10)):
                    header += ' '
                    header_width = stringWidth(header, 'Arial', 10)
                header += 'Group'

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
                        group_string += 's' + str(rounds) + ','
                    elif str(rounds) == group_number:
                        group_string += str(group_number) + ','

                group_string = group_string[:-1]
            else:
                group_string = str(group_number)

            group_width = stringWidth(group_string, 'Arial', 8)
            while group_width < 40:
                group_string = ' ' + group_string
                group_width = stringWidth(group_string, 'Arial', 8)

            label.add(shapes.String(width+max_event_width-18, height, group_string, fontSize = 8, fontName='Arial'))
            height -= 11
            counter += 1
    if does_scramble:
        label.add(shapes.String(180, 140, 's = Scrambler', fontSize = 8, fontName='Arial'))

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
    comp_name_width = stringWidth(competition_name, 'Arial', font_size)
    while comp_name_width > text_width:
        font_size *= 0.95
        comp_name_width = stringWidth(competition_name, 'Arial', font_size)
    
    label.add(shapes.String(width/2, height-70, competition_name, textAnchor='middle', fontSize=font_size, fontName='Arial'))
    
    day_id = datetime.date(year, month, day).weekday() + schedule_day
    if day_id > 7:
        day_id -= 7

    day_name = calendar.day_name[day_id] + ', ' + str(competition_day_date.day) + '. ' + calendar.month_name[month]
    day_name_width = stringWidth(day_name, 'Arial', font_size)
    font_size = 35
    while day_name_width > text_width:
        font_size *= 0.95
        comp_name_width = stringWidth(day_name, 'Arial', font_size)
    label.add(shapes.String(width/2, height-120, day_name, textAnchor='middle', fontSize=font_size, fontName='Arial'))
    
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
    
    height += 13
    for event in full_schedule:
        double_height = False
        event_day = event['startTime'].split('T')[0]
        if event_day == competition_day:
            event_start = event['startTime'].split('T')[1][:-1]
            event_start = event_start.split(':')[0] + ':' + event_start.split(':')[1]
            event_end = event['endTime'].split('T')[1][:-1]
            event_end = event_end.split(':')[0] + ':' + event_end.split(':')[1]
            event_name = event['event_name'].replace('\\u0026', '&')

            limit = ''
            format = ''
            seconds = ''
            minutes = ''
            seconds_cutoff = ''
            minutes_cutoff = ''
            for events in event_info:
                if event['event_id'] == events['event'] and event['event_name'][-1:] == events['round']:
                    time_limit = events['limit']
                    minutes, seconds = divmod(time_limit, 60)
                    minutes = str(minutes)
                    seconds = str(seconds)
                    if len(seconds) < 2:
                        while len(seconds) < 2:
                            seconds = '0' + str(seconds)
                    limit = minutes + ':' + seconds
                    if events['cumulative']:
                        limit += ' cumulative'
                    if events['cutoff_number'] != 0:
                        event_name = event_name.replace('Round', 'Combined Round')
                    
                        format_name = 'bo' + str(events['cutoff_number'])
                        cutoff_limit  = events['cutoff']
                        minutes_cutoff, seconds_cutoff = divmod(cutoff_limit, 60)
                        minutes_cutoff = str(minutes_cutoff)
                        seconds_cutoff = str(seconds_cutoff) 
                        if len(seconds_cutoff) < 2:
                            while len(seconds_cutoff) < 2:
                                seconds_cutoff = '0' + str(seconds_cutoff)  
                            
                        format = format_names[format_name] + ' (< ' + minutes_cutoff + ':' + seconds_cutoff + ') / '
                        
                    format += format_names[str(events['format'])]
                    
                    if events['advancing']:
                        format += ' (' + events['advancing'] + ' proceed)'
            round_number = event['event_name'][-1:]
            if round_number == str(round_counter[event['event_id']]) or round_number == '3':
                replace_string = ' Round ' + str(round_number)
                if round_number == '3' and round_counter[event['event_id']] != 3:
                    event_name = event_name.replace(replace_string, ' Semi Final')
                else:
                    event_name = event_name.replace(replace_string, ' Final')
            
            event_name = event_name.replace('Round 1', 'First Round')
            event_name = event_name.replace('Round 2', 'Second Round')
                    
            event_font_size = 12
            box_height = event_font_size + 4
            set_box_height = 0
            if stringWidth(event_name, 'Arial', event_font_size) > 155 or stringWidth(format, 'Arial', event_font_size) > 190:
                double_height = True
                
                set_box_height = box_height
                box_height += box_height
                event_name_string1 = event_name
                event_name_string2 = ''
                format_string1 = format
                format_string2 = ''
                new_string = ''
                if stringWidth(event_name, 'Arial', event_font_size) > 155:
                    event_name_string1 = ''
                    for substring in event_name.split():
                        new_string = event_name_string1 + substring + ' ' 
                        if stringWidth(new_string, 'Arial', event_font_size) < 155:
                            event_name_string1 += substring + ' '
                        else: 
                            break
                    event_name_string2 = event_name.replace(event_name_string1, '')
                if event_name_string1[-2:] == '- ':
                    event_name_string1 = event_name_string1[:-2]
                if event_name_string2[:1] == '-':
                    event_name_string2 = event_name_string2[2:]
                new_string = ''
                if stringWidth(format, 'Arial', event_font_size) > 190:
                    format_string1 = ''
                    for substring in format.split():
                        new_string = format_string1 + substring + ' ' 
                        if stringWidth(new_string, 'Arial', event_font_size) < 155:
                            format_string1 += substring + ' '
                        else: 
                            break
                    format_string2 = format.replace(format_string1, '')
            label.add(shapes.Rect(10,height-195-set_box_height,52, box_height, fillColor=colors.white))
            label.add(shapes.Rect(62,height-195-set_box_height,52, box_height, fillColor=colors.white))
            label.add(shapes.Rect(112,height-195-set_box_height,160, box_height, fillColor=colors.white))
            label.add(shapes.Rect(272,height-195-set_box_height,115, box_height, fillColor=colors.white))
            label.add(shapes.Rect(387,height-195-set_box_height,190, box_height, fillColor=colors.white))
    
            if double_height:
                label.add(shapes.String(192, height-190, event_name_string1, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
                label.add(shapes.String(192, height-190-set_box_height, event_name_string2, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
                label.add(shapes.String(485, height-190, format_string1, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
                label.add(shapes.String(485, height-190-set_box_height, format_string2, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
            else:
                label.add(shapes.String(192, height-190, event_name, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
                label.add(shapes.String(485, height-190, format, fontSize=event_font_size, textAnchor='middle', fontName='Arial'))
            label.add(shapes.String(21, height-190-set_box_height/2, event_start, fontSize=event_font_size, fontName='Arial'))
            label.add(shapes.String(71, height-190-set_box_height/2, event_end, fontSize=event_font_size, fontName='Arial'))
            label.add(shapes.String(330, height-190-set_box_height/2, limit, textAnchor='middle', fontSize=event_font_size, fontName='Arial'))
            
            if double_height:
                height -= (event_font_size + 4) * 2
            else:
                height -= event_font_size + 4

def create_schedule_file(competition_name, competition_name_stripped, full_schedule, event_info, competition_days, competition_start_day, timezone_utc_offset, formats, format_names, round_counter):
    specs_scoresheets = labels.Specification(210, 297, 1, 1, 210, 297)
    
    sheet = labels.Sheet(specs_scoresheets, write_schedule, border=False)
    schedule_file = competition_name + '/' + competition_name.replace(' ', '') + 'Schedule.pdf'
    
    sheet.add_labels((competition_name, competition_name_stripped, full_schedule, event_info, competition_days, competition_start_day, schedule_day, timezone_utc_offset, formats, format_names, round_counter) for schedule_day in range(competition_days))
    sheet.save(schedule_file)
    
