'''
Data extraction of WCIF and registration file (if used). Not too interesting, mainly a lot of parsing in .txt files (registration file and/or wcif file).    
'''

from competition_preparation_start import *

# initialize various variables for parsing and analysis
events, events_now, persons, accepted, roles, cumulative_rounds, schedule = (False for i in range(7))
registered_events, final_registration_list, all_events, event_ids_wca = (() for i in range(4)) 
registration_list, registration_list_wca, group_list, competitor_information, competitor_information_wca, event_info, full_schedule, events_per_day, competing_day = ([] for i in range(9))
event_id, round_id, competitor_role, guests, cumulative, advancing_competitiors, advancing_type = ('' for i in range(7))
event_counter, event_counter_wca, group_count, cutoff_number, cutoff, round_counter, competition_days = (0 for i in range(7))
registration_id = 1

column_ids = {
        '333': 999, '222': 999, '444': 999, '555': 999, '666': 999, 
        '777': 999, '333bf': 999, '333fm': 999, '333oh': 999, '333ft': 999, 
        'minx': 999, 'pyram': 999, 'clock': 999, 'skewb': 999, 'sq1': 999, 
        '444bf': 999, '555bf': 999, '333mbf': 999
        }
formats = {
        'a': 'ao5', 'm': 'mo3', '1': 'bo1', 
        '2': 'bo2', '3': 'bo3'
        }
format_names = {
        'bo3': 'Best of 3', 'bo2': 'Best of 2', 'bo1': 
        'Best of 1', 'mo3': 'Mean of 3', 'ao5': 'Average of 5'
        }

def get_registration_from_file(file_name, new_creation, reading_grouping_from_file, use_csv_registration_file, column_ids, event_counter, competitor_information_wca, competitors):
    file = open(file_name)
    all_data = []
    wca_ids, event_list = (), ()
    line_count = 0
    registration_id = 1
    for row in file:
            row_list = row.split(',')
            row_list[1] = row_list[1].split(' (')[0]
            last_entry = len(row_list) - 1
            row_list[last_entry] = row_list[last_entry].replace('\n', '')
            if line_count == 0:
                if (new_creation and not row.startswith('Status')) or (reading_grouping_from_file and not 'Name' in row):
                    print('')
                    print('ERROR!! Missing header-line in registration file, script aborted.')
                    sys.exit()
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
                if use_csv_registration_file:
                    if row_list[3]:
                        for person in competitor_information_wca:
                            if row_list[3] == person['personId']:
                                if person['role']:
                                    role = person['role']
                    if new_creation or reading_grouping_from_file:
                        competitor_information.append(
                                    {
                                    'name': row_list[1],
                                    'country': row_list[2],
                                    'role': role,
                                    'personId': row_list[3],
                                    'registration_id': registration_id
                                    }
                                )
                    else:
                        for comp in competitors:
                            if row_list[1] == comp['name'].split(' (')[0]:
                                competitor_information.append(
                                            {
                                            'name': row_list[1],
                                            'personId': row_list[3],
                                            'ranking': comp['ranking'],
                                            'registration_id': registration_id
                                            }
                                        )
                else:
                    competitor_information.append(
                        {
                        'name': row_list[1],
                        'country': row_list[2],
                        'role': role,
                        'personId': row_list[3],
                        'registration_id': registration_id,
                        'comp_count': 0,
                        'single': '0.00',
                        'average': '0.00'
                        }
                    )
                
                if row_list[3]:
                    wca_ids += (str(row_list[3]),)
                registration_id += 1
            line_count += 1
    return (column_ids, event_list, event_counter, competitor_information, all_data, wca_ids)

def format_schedule_time(schedule_event_time_utc, timezone_utc_offset):
    schedule_event_time = '{}T'.format(schedule_event_time_utc.split('T')[0])
    if (int(schedule_event_time_utc.split('T')[1].split(':')[0]) + timezone_utc_offset) < 10:
        schedule_event_time = ''.join(
                [
                schedule_event_time, '0', 
                str(int(schedule_event_time_utc.split('T')[1].split(':')[0]) + timezone_utc_offset)
                ]
            )
    else:
        schedule_event_time = ''.join(
                [
                schedule_event_time, 
                str(int(schedule_event_time_utc.split('T')[1].split(':')[0]) + timezone_utc_offset)
                ]
            )
    schedule_event_time = ''.join(
            [
            schedule_event_time, ':', 
            schedule_event_time_utc.split('T')[1].split(':')[1], ':', 
            schedule_event_time_utc.split('T')[1].split(':')[2]
            ]
        )
    return schedule_event_time

cur = WCA_Database.query("SELECT * FROM Countries")

if get_registration_information:
    countries = cur.fetchall()

    # Extract data from WCIF file
    wca_json = json.loads(competition_wcif_file)
    
    ########## REGISTRATION ##########
        # get competitor information: name, WCA ID, date of birth, gender, country, competition roles (organizer, delegate) and events registered for
    registration_id = 1    
    for registrations in wca_json['persons']:
        registered_events = ()
        competitor_role = ''
        
        for country in countries:
            if country['iso2'] == registrations['countryIso2']:
                comp_country = country['id']
        if registrations['roles']:
            for role in registrations['roles']:
                competitor_role = ''.join([competitor_role, role.replace('delegate', 'WCA DELEGATE').upper(), ','])
            competitor_role = competitor_role[:-1]
        for competitor_events in registrations['registration']['eventIds']:
            all_events += (competitor_events,)
            registered_events += (competitor_events,)
            
        information = {
                'name': registrations['name'].split(' (')[0].strip(), 
                'personId': registrations['wcaId'], 
                'dob': registrations['birthdate'], 
                'gender': registrations['gender'], 
                'country': comp_country, 
                'role': competitor_role, 
                'guests': str(registrations['registration']['guests']), 
                'registered_events': registered_events, 
                'registration_id': registration_id
                }
        if not registrations['wcaId']:
            information.update({'personId': ''})
        if registrations['registration']['status'] == 'accepted':
            if create_scoresheets_second_rounds_bool:
                for comp in competitors:
                    if registrations['name'].split(' (')[0].strip() == ftfy.fix_text(comp['name']).split(' (')[0]:
                        information.update(
                                    {
                                    'ranking': comp['ranking'], 
                                    'registration_id': comp['competitor_id']
                                    }
                                )
                        competitor_information_wca.append(information)
                        break
            elif use_cubecomps_ids:
                for comp in competitors_api:
                    if registrations['name'].split(' (')[0].strip() == ftfy.fix_text(comp['name']).split(' (')[0]:
                        information.update(
                                    {
                                    'registration_id': comp['competitor_id']
                                    }
                                )
                        competitor_information_wca.append(information)
                        break
            else:
                competitor_information_wca.append(information)
            registration_id += 1

    ########## EVENTS ##########
    # For every event parse information about event_id, round_number, # groups, format, cutoff, time limit, (possible) cumulative limits
    minimal_scramble_set_count = 1
    for wca_events in wca_json['events']:
        event_counter_wca += 1
        for wca_rounds in wca_events['rounds']:
            cutoff_number, cutoff, limit = 0, 0, 0
            advancing_competitors, advancing_competitors, cumulative = '', '', ''

            if wca_rounds['cutoff']:
                if 'numberOfAttempts' in wca_rounds['cutoff']:
                    cutoff_number = wca_rounds['cutoff']['numberOfAttempts']
                if 'attemptResult' in wca_rounds['cutoff']:
                    cutoff = int(wca_rounds['cutoff']['attemptResult'] / 100)
            if 'timeLimit' in wca_rounds:
                if wca_rounds['timeLimit']:
                    limit = int(wca_rounds['timeLimit']['centiseconds'] / 100)
                    if wca_rounds['timeLimit']['cumulativeRoundIds']:
                        for cumulative_event in wca_rounds['timeLimit']['cumulativeRoundIds']:
                            cumulative = ''.join([cumulative, event_dict[cumulative_event[:-3]], ', '])
                        cumulative = cumulative[:-2]
                else:
                    limit = 3600
            if wca_rounds['advancementCondition']:
                if wca_rounds['advancementCondition']['type'] == 'percent':
                    advancing_competitors = str(wca_rounds['advancementCondition']['level']) + '%'
                elif wca_rounds['advancementCondition']['type'] == 'attemptResult':
                    minutes, seconds = format_minutes_and_seconds(wca_rounds['advancementCondition']['level'] / 100)
                    advancing_competitors = '<{}:{}'.format(minutes, seconds)
                else:
                    advancing_competitors = str(wca_rounds['advancementCondition']['level'])
            
            wca_event_infos = {
                    'event': wca_events['id'], 
                    'round': wca_rounds['id'][-1:], 
                    'format': formats[wca_rounds['format']], 
                    'cutoff_number': cutoff_number, 
                    'cutoff': cutoff, 
                    'limit': limit, 
                    'cumulative': cumulative, 
                    'advancing': advancing_competitors
                    }
            event_info.append(wca_event_infos)
            event_ids_wca += (wca_events['id'],)
            
            group_list.append(
                        (
                        wca_events['id'], 
                        ''.join([event_dict[wca_events['id']], wca_rounds['id'][-3:].replace('-r', ' - Round ')]),
                        wca_rounds['scrambleSetCount'], 
                        advancing_competitors
                        )
                    )
            
            if wca_rounds['scrambleSetCount'] > minimal_scramble_set_count:
                minimal_scramble_set_count = wca_rounds['scrambleSetCount'] 

    ########## SCHEDULE ##########
    # get schedule information from wca website
    # used for sorting of scramblerlist + creating a PDF containing the schedule 
    if wca_json['schedule']['venues']:   
        timezone_competition = wca_json['schedule']['venues'][0]['timezone']
        competition_days = wca_json['schedule']['numberOfDays']
        competition_start_day = wca_json['schedule']['startDate']
        year = int(competition_start_day.split('-')[0])
        month = int(competition_start_day.split('-')[1])
        day = int(competition_start_day.split('-')[2])
        for schedule_events in wca_json['schedule']['venues'][0]['rooms'][0]['activities']:
            schedule_round_id = ''
            if schedule_events['name'][-1:].isdigit():
                schedule_round_id = str(schedule_events['name'][-1:])
            schedule_event_start_utc = schedule_events['startTime']
            if not full_schedule:
                timezone_localize = pytz.timezone(timezone_competition)
                timezone_utc_offset = int(str(timezone_localize.localize(datetime.datetime(year, month, day, int(schedule_event_start_utc.split('T')[1].split(':')[0]), 0, 0))).split('+')[1].split(':')[0]) 
            schedule_event_start = format_schedule_time(schedule_event_start_utc, timezone_utc_offset)

            schedule_event_end_utc = schedule_events['endTime']
            schedule_event_end = format_schedule_time(schedule_event_end_utc, timezone_utc_offset)
            
            wca_event_information = {
                    'id': str(schedule_events['id']), 
                    'round_number': schedule_round_id, 
                    'event_id': schedule_events['activityCode'].split('-')[0], 
                    'event_name': schedule_events['name'].replace(',', ' -').replace(' Cube', ''), 
                    'acitivityCode': schedule_events['activityCode'], 
                    'startTime': schedule_event_start, 
                    'endTime': schedule_event_end
                    }
            full_schedule.append(wca_event_information)
    else:
        print('No schedule found on WCA website.')


    if wca_info and not create_only_schedule:
        competitor_information = competitor_information_wca
    
        event_list_wca = sorted(collections.Counter(all_events))
        number_events = len(event_list_wca)
        registration_index = 0
        wca_ids = ()
    
        for person in competitor_information:
            event_string = [
                    person['guests'], 
                    ftfy.fix_text(person['name']), 
                    person['country'], 
                    person['personId'], 
                    person['dob'], 
                    person['gender']
                    ]
            if person['personId']:
                wca_ids += (person['personId'],)
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
            sys.exit()
        registration_list_wca = sorted(sorted(registration_list_wca, key=lambda x: x[1]), key=lambda x: x[1].split()[-1])
    
        event_list = ()
        counter = 0

        for event in event_list_wca:
            if event in column_ids:
                new_id = {event: counter + 6}
                column_ids.update(new_id)
                event_list += (event,)
                counter += 1

    round_counter = collections.Counter(event_ids_wca)

    if group_list:
        print('WCA information sucessfully imported.')
    else:
        print('An error occured while importing the rounds and groups information from the WCIF file, script aborted.')
        print('Please make sure to enter all necessary information in the "Manage events" tab on the WCA competition page.')
        sys.exit()
    if minimal_scramble_set_count == 1:
        continue_script = get_information('It looks like all your events only have one set of scrambles. Do you still want to continue running this script? (y/n)')
        if not continue_script:
            print('')
            print('Please edit the group information in the competition event tab  before running this script again.')
            print('Script aborted.')
            sys.exit()
        else:
            print('Continue script. Please be reminded, that there is a high possibility of not finding any scramblers!')

    ### Get data from csv-export
    # same as for the WCA registration, get competitor information from registration file (if used): name, WCA ID, date of birth, gender, country and events registered for
    registration_id = 1
    if not wca_info:
        print('Open registration file...')
        use_csv_registration_file = True
        column_ids, event_list, event_counter, competitor_information, all_data, wca_ids = get_registration_from_file(file_name, new_creation, reading_grouping_from_file, use_csv_registration_file, column_ids, event_counter, competitor_information_wca, competitors)

        registration_list = sorted(sorted(all_data, key= lambda x: x[1]), key=lambda x: x[1].split()[-1])
    
        if event_counter != event_counter_wca:
            print('ERROR!! Number of events from WCA Website does not match number of events in registration data. Please use correct registration file. Abort script.')
            sys.exit()

    if wca_info:
        registration_list = registration_list_wca

### Parse registration file
if read_only_registration_file:
    use_csv_registration_file = False
    column_ids, event_list, event_counter, competitor_information, all_data, wca_ids = get_registration_from_file(file_name, new_creation, reading_grouping_from_file, use_csv_registration_file, column_ids, event_counter, competitor_information_wca, competitors)
    
### Create schedule (if exists on WCA website)
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
            events_per_day.append(
                        {
                        'day': event_day_name, 
                        'day_id': event_day_id, 
                        'events': [schedule_event['event_id']]
                        }
                    )

    for competitor in registration_list:
        competing_day, competing_per_day_list = [], []
        for event_column in column_ids:
            if column_ids[event_column] != 999:
                if competitor[column_ids[event_column]] == '1':
                    for days in events_per_day:
                        if event_column in days['events']:
                            competing_day.append(days['day_id'])

        competing_per_day = collections.Counter(competing_day)
        competing_day = sorted(set(competing_day))
        counter = 0
        for day in competing_day:
            competing_day[counter] = calendar.day_name[day][:3]
            competing_per_day_list.append(competing_per_day[day])
            counter += 1
        competitor.append(competing_day)
        competitor.append(competing_per_day_list)
    
    if create_schedule:
        create_schedule_file(
                competition_name, competition_name_stripped, full_schedule, 
                event_info, competition_days, competition_start_day, 
                timezone_utc_offset, formats, format_names, 
                round_counter
                )
        if create_only_schedule:
            sys.exit()
            
elif create_schedule:
    print('')
    print('ERROR!! No schedule found on WCA website. Script continues without creating schedule.')

### Create registration file (.csv)
if create_registration_file_bool:
    print('')
    print('Create registration file...')
    output_registration = '{}/{}Registration.csv'.format(competition_name, competition_name_stripped)
    create_registration_file(
            output_registration, registration_list, 
            column_ids, competition_days
            )

    print('Registration file successfully created.')
    print('')

    if create_only_registration_file:
        sys.exit()
