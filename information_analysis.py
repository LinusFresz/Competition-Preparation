#!/usr/bin/python

'''
Data extraction of WCIF and registration file (if used). Not too interesting, mainly a lot of parsing in .txt files (registration file and/or wcif file).    
'''


from competition_preparation_start import *

events, events_now, persons, accepted, roles, cumulative_rounds, schedule = (False for i in range(7))

registered_events, final_registration_list, all_events, event_ids_wca = (() for i in range(4)) 

registration_list, registration_list_wca, group_list, competitor_information, competitor_information_wca, event_info, full_schedule, events_per_day, competing_day = ([] for i in range(9))

event_id, round_id, competitor_role, guests, cumulative, advancing_competitiors, advancing_type = ('' for i in range(7))

event_counter, event_counter_wca, group_count, cutoff_number, cutoff, round_counter, competition_days = (0 for i in range(7))
registration_id = 1

column_ids = {'333': 999, '222': 999, '444': 999, '555': 999, '666': 999, '777': 999, '333bf': 999, '333fm': 999, '333oh': 999, '333ft': 999, 'minx': 999, 'pyram': 999, 'clock': 999, 'skewb': 999, 'sq1': 999, '444bf': 999, '555bf': 999, '333mbf': 999}
formats = {'a': 'ao5', 'm': 'mo3', '1': 'bo1', '2': 'bo2', '3': 'bo3'}
format_names = {'bo3': 'Best of 3', 'bo2': 'Best of 2', 'bo1': 'Best of 1', 'mo3': 'Mean of 3', 'ao5': 'Average of 5'}

cur = WCA_Database.query("SELECT * FROM Countries")

if get_registration_information:
    countries = cur.fetchall()

    # Extract data from WCIF file
    wcif_file = open(wcif_file, 'r', encoding='utf-8')
    lines = wcif_file.readlines()
    wcif_file.close()

    for line in lines:
        line = line.strip()
        
        ########## GROUPING ##########
        # For every event pars information about event_id, round_number, # groups, format, cutoff, time limit, (possible) cumulative limits
        if line.find('"schedule":') != -1:
            events = False
            schedule = True
         
        if events:
            if 'id' in line and (len(line) < 15 or '"333mbf"' in line):
                event_id = line[7:-2]
                event_counter_wca += 1
            elif 'id' in line and len(line) < 23:
                round_id = line[7:-2]
                round_id = event_dict[round_id[:-3]] + round_id[-3:]
                round_id = round_id.replace('-r', ' - Round ')
            if 'scrambleGroupCount' in line:
                group_count = int(line[21:-1])
            if 'type' in line:
                advancing_type = line[9:-2]
            if 'level' in line:
                advancing_competitiors = line[9:]
                if advancing_type == 'percent':
                    advancing_competitiors += '%'
            if 'format' in line:
                '''
                if line[11:-2].isdigit():
                    format = int(line[11:-2])
                else:
                    format = formats[line[11:-2]]
                '''
                format = formats[line[11:-2]]
            if 'centiseconds' in line:
                limit = int(int(line[16:-1]) / 100)
            if 'numberOfAttempts' in line:
                cutoff_number = int(line[20:-1])
            if 'attemptResult' in line and 'type' not in line:
                cutoff = int(int(line[17:]) / 100)

            if cumulative_rounds and ']' in line:
                cumulative_rounds = False
            if cumulative_rounds and line[1:-1]:
                if cumulative:
                    cumulative += ', '
                line = line.replace(',', '')
                line = line[1:-1]
                for name in event_dict:
                    if line[:-3] == name:
                        line = event_dict[name]
                cumulative += line
            if 'cumulativeRoundIds' in line:
                cumulative_rounds = True
        if round_id != '' and group_count > 0:
            group_list.append((event_id, round_id, group_count))
            if event_id == '333mbf':
                limit = 3600
            event_infos = {'event': event_id, 'round': round_id[-1:], 'format': format, 'cutoff_number': cutoff_number, 'cutoff': cutoff, 'limit': limit, 'cumulative': cumulative, 'advancing': advancing_competitiors}
            event_info.append(event_infos)
            event_ids_wca = event_ids_wca + (event_id,)
            cutoff_number, cutoff, group_count = 0, 0, 0
            cumulative, round_id, advancing_type, advancing_competitiors = '', '', '', ''
            limit = 600
    
        if line.find('"events":') != -1:
            events = True
            persons = False


        ########## REGISTRATION ##########
        # get competitor information: name, WCA ID, date of birth, gender, country, competition roles (organizer, delegate) and events registered for
        if persons:
            if 'name' in line:
                name = line[9:-2]
                name = name.split(' (')[0]
                for number in range(0, 3):
                    if name[-1:] == ' ':
                        name = name[:-1]
            if 'wcaId' in line:
                if 'null' not in line:
                    wca_id = line[10:-2]
                else:
                    wca_id = ''
            if 'birthdate' in line:
                dob = line[14:-2]
            if 'gender' in line:
                gender = line[11:-2]
            if 'country' in line:
                iso = line[16:-2]
                comp_country = ""
                for country in countries:
                    if iso == country['iso2']:
                        comp_country = country['id']
            if 'guests' in line:
                guests = line[10:-1]
            if events_now and ']' in line:
                events_now = False
            if events_now:
                line = line.replace(',', '')
                event = line[1:-1]
                all_events += (event,)
                registered_events += (event,)
            if 'eventIds' in line:
                events_now = True
            if roles and ']' in line:
                roles = False
            if roles:
                line = line.replace(',', '')
                if line:
                    if competitor_role:
                        competitor_role += ', '
                    if 'delegate' in line:
                        role = 'WCA ' + line[1:-1].upper()
                    else:
                        role = line[1:-1].upper()
                    competitor_role += role
            if 'roles' in line:
                roles = True
            if 'status' in line:
                if 'accepted' in line:
                    accepted = True
            if 'personalBests' in line:
                information = {'name': name, 'personId': wca_id, 'dob': dob, 'gender': gender, 'country': comp_country, 'role': competitor_role, 'guests': guests, 'registered_events': registered_events, 'registration_id': registration_id}
                registered_events = ()
                if accepted or not wca_info:
                    if create_scoresheets_second_rounds_bool:
                        for comp in competitors:
                            if name == ftfy.fix_text(comp['name']).split(' (')[0]:
                                information.update({'ranking': comp['ranking']})
                                competitor_information_wca.append(information)
                    else:
                        competitor_information_wca.append(information)
                    registration_id += 1

                accepted = False
                competitor_role = ''

        if line.find('"persons":') != -1:
            persons = True
            
        if schedule:
            if 'startDate' in line:
                competition_start_day = line[14:-2]
                year = int(competition_start_day.split('-')[0])
                month = int(competition_start_day.split('-')[1])
                day = int(competition_start_day.split('-')[2])
            if 'numberOfDays' in line:
                competition_days = int(line[16:-1])
            if 'timezone' in line:
                timezone_competition = line[13:-2] 
            if 'id' in line:
                schedule_id = line[6:-1]
            if 'name' in line:
                schedule_event_name = line[9:-2].replace(',', ' -').replace(' Cube', '')
            if 'activityCode' in line:
                schedule_activity_code = line[17:-2]
            if 'startTime' in line:
                schedule_event_start_utc = line[14:-2]
                if not full_schedule:
                    timezone_localize = pytz.timezone(timezone_competition)
                    timezone_utc_offset = int(str(timezone_localize.localize(datetime.datetime(year, month, day, int(schedule_event_start_utc.split('T')[1].split(':')[0]), 0, 0))).split('+')[1].split(':')[0]) 
                
                schedule_event_start = schedule_event_start_utc.split('T')[0] + 'T'
                if (int(schedule_event_start_utc.split('T')[1].split(':')[0]) + timezone_utc_offset) < 10:
                    schedule_event_start += '0' + str(int(schedule_event_start_utc.split('T')[1].split(':')[0]) + timezone_utc_offset)
                else:
                    schedule_event_start += str(int(schedule_event_start_utc.split('T')[1].split(':')[0]) + timezone_utc_offset)
                schedule_event_start += ':' + schedule_event_start_utc.split('T')[1].split(':')[1] + ':' + schedule_event_start_utc.split('T')[1].split(':')[2]
            if 'endTime' in line:
                schedule_event_end_utc = line[12:-2]
                
                schedule_event_end = schedule_event_end_utc.split('T')[0] + 'T'
                if (int(schedule_event_end_utc.split('T')[1].split(':')[0]) + timezone_utc_offset) < 10:
                    schedule_event_end += '0' + str(int(schedule_event_end_utc.split('T')[1].split(':')[0]) + timezone_utc_offset)
                else:
                    schedule_event_end += str(int(schedule_event_end_utc.split('T')[1].split(':')[0]) + timezone_utc_offset)
                schedule_event_end += ':' + schedule_event_end_utc.split('T')[1].split(':')[1] + ':' + schedule_event_end_utc.split('T')[1].split(':')[2]
            if 'childActivities' in line:
                schedule_event_id = schedule_activity_code.split('-')[0]
                if schedule_event_name[-1:].isdigit():
                    schedule_round_id = schedule_event_name[-1:]
                else:
                    schedule_round_id = ''
                event_information = {'id': schedule_id, 'round_number': schedule_round_id, 'event_id': schedule_event_id, 'event_name': schedule_event_name, 'acitivityCode': schedule_activity_code, 'startTime': schedule_event_start, 'endTime': schedule_event_end}
                full_schedule.append(event_information)

    if wca_info and not create_only_schedule:
        competitor_information = competitor_information_wca
    
        event_list_wca = sorted(Counter(all_events))
        number_events = len(event_list_wca)
        registration_index = 0
        wca_ids = ()
    
        for person in competitor_information:
            event_string = [person['guests'], unicodedata.normalize('NFKD', person['name']), person['country'], person['personId'], person['dob'], person['country']]
            if person['personId']:
                wca_ids = wca_ids + (person['personId'],)
            for index in range(0, number_events):
                event_string.append('0')
            registration_list_wca.append(event_string)

            for event in event_list_wca:
                if event in person['registered_events']:
                    id = event_list_wca.index(event) + 6
                    registration_list_wca[registration_index][id] = '1'

            registration_index += 1

        if not registration_list_wca:
            print('')
            print('ERROR!! WCA registration not used for this competition. Please select registration file for import. Script aborted.')
            quit_program(wcif_file)
        registration_list_wca = sorted(sorted(registration_list_wca, key=lambda x: x[1]), key=lambda x: x[1].split()[-1])
    
        event_list = ()
        counter = 0

        for event in event_list_wca:
            if event in column_ids:
                new_id = {event: counter + 6}
                column_ids.update(new_id)
                event_list = event_list + (event,)
                counter += 1

    round_counter = Counter(event_ids_wca)

    if group_list:
        print('Grouping sucessfully imported.')
    else:
        print('An error occured while importing the rounds and groups information from the WCIF file, script aborted.')
        print('Please make sure to enter all necessary information in the "Manage events" tab on the WCA competition page.')
        quit_program(wcif_file)

    # Get data from csv-export
    # Same as for the WCA registration, get competitor information from registration file (if used): name, WCA ID, date of birth, gender, country and events registered for
    registration_id = 1

    if not wca_info:
        print('Open registration file...')
        file = open(file_name)
    
        all_data = []
        wca_ids = ()
        event_list = ()
    
        line_count = 0
    
        for row in file:
            row_list = row.split(',')
            row_list[1] = row_list[1].split(' (')[0]
            last_entry = len(row_list) - 1
            row_list[last_entry] = row_list[last_entry].replace('\n', '')
            if line_count == 0:
                if (new_creation and not row.startswith('Status')) or (reading_grouping_from_file and not 'Name' in row):
                    print('')
                    print('ERROR!! Missing header-line in registration file, script aborted.')
                    quit_program(wcif_file)
                counter = 0
                for event in row_list:
                    if event in column_ids:
                        new_id = {event: counter}
                        column_ids.update(new_id)
                        event_list += (event,)
                        event_counter += 1
                    counter += 1
        
            else:
                all_data.append(row_list)
                role = ''
                if row_list[3]:
                    for person in competitor_information_wca:
                        if row_list[3] == person['personId']:
                            if person['role']:
                                role = person['role']
                if new_creation or reading_grouping_from_file:
                    competitor_information.append({'name': row_list[1], 'country': row_list[2], 'role': role, 'personId': row_list[3], 'registration_id': registration_id})
                else:
                    for comp in competitors:
                        if row_list[1] == comp['name'].split(' (')[0]:
                            competitor_information.append({'name': row_list[1], 'personId': row_list[3], 'ranking': comp['ranking'], 'registration_id': registration_id})    
                if row_list[3]:
                    wca_ids += (str(row_list[3]),)
                registration_id += 1
            line_count += 1
    
        registration_list = sorted(sorted(all_data, key= lambda x: x[1]), key=lambda x: x[1].split()[-1])
        
        if event_counter != event_counter_wca:
            print('ERROR!! Number of events from WCA Website does not match number of events in registration data. Please use correct registration file. Abort script.')
            quit_program(wcif_file)

    if wca_info:
        registration_list = registration_list_wca

if read_only_registration_file:
    file = open(file_name)
    
    all_data = []
    wca_ids = ()
    event_list = ()
    
    line_count = 0
    
    for row in file:
        row_list = row.split(',')
        row_list[1] = row_list[1].split(' (')[0]
        last_entry = len(row_list) - 1
        row_list[last_entry] = row_list[last_entry].replace('\n', '')
        if line_count == 0:
            if not row.startswith('Status') or not 'Name' in row:
                print('')
                print('ERROR!! Missing header-line in registration file, script aborted.')
                quit_program(wcif_file)
            counter = 0
            for event in row_list:
                if event in column_ids:
                    new_id = {event: counter}
                    column_ids.update(new_id)
                    event_list += (event,)
                    event_counter += 1
                counter += 1
        
        else:
            all_data.append(row_list)
            role = ''
            competitor_information.append({'name': row_list[1], 'country': row_list[2], 'role': role, 'personId': row_list[3], 'registration_id': registration_id, 'comp_count': 0, 'single': '0.00', 'average': '0.00'})
            if row_list[3]:
                wca_ids += (str(row_list[3]),)
        line_count += 1
    
if full_schedule:
    full_schedule = sorted(sorted(full_schedule, key=lambda x: x['event_name']), key=lambda x: x['startTime'])
    for schedule_event in full_schedule:
        day_exists = False
        event_day = schedule_event['startTime'].split('T')[0]
        event_day_id = datetime.datetime(int(event_day.split('-')[0]), int(event_day.split('-')[1]), int(event_day.split('-')[2])).weekday()
        event_day_name = calendar.day_name[event_day_id]
        for day in events_per_day:
            if day['day'] == event_day_name:
                day_exists = True
        if day_exists:
            if schedule_event['event_id'] not in day['events']:
                day['events'].append(schedule_event['event_id'])
        else:
            events_per_day.append({'day': event_day_name, 'day_id': event_day_id, 'events': [schedule_event['event_id']]})

    for competitor in registration_list:
        competing_day, competing_per_day_list = [], []
        for event_column in column_ids:
            if column_ids[event_column] != 999:
                if competitor[column_ids[event_column]] == '1':
                    for days in events_per_day:
                        if event_column in days['events']:
                            competing_day.append(days['day_id'])

        competing_per_day = Counter(competing_day)
        competing_day = sorted(set(competing_day))
        counter = 0
        for day in competing_day:
            competing_day[counter] = calendar.day_name[day][:3]
            competing_per_day_list.append(competing_per_day[day])
            counter += 1
        competitor.append(competing_day)
        competitor.append(competing_per_day_list)
    
# registration file
if create_registration_file_bool:
    output_registration = competition_name + '/registration.csv'
    create_registration_file(output_registration, registration_list, column_ids, competition_days)

    print('Registration file successfully created')

    if create_only_registration_file:
        quit_program(wcif_file)

if create_schedule:
    if full_schedule:
        create_schedule_file(competition_name, competition_name_stripped, full_schedule, event_info, competition_days, competition_start_day, timezone_utc_offset, formats, format_names, round_counter)
    else:
        print('')
        print('ERROR!! No schedule found on WCA website. Script continues without creating schedule.')
        print('')
    if create_only_schedule:
        quit_program(wcif_file)

