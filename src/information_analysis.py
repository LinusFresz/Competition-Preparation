### Data extraction of WCIF and registration file (if used).

from modules import *

import helpers.helpers as helper
import apis

# initialize various variables for parsing and analysis
registration_list, competitor_information = [], []
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

### Get registration from file if WCA registration is not used
def get_registration_from_file(file_name, new_creation, reading_grouping_from_file, use_csv_registration_file, column_ids, competitor_information_wca, competitors):
    file = open(file_name)
    all_data = []
    wca_ids, event_list = (), ()
    line_count = 0
    event_counter = 0
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

### Read in grouping file if needed for nametags/scoresheets
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
            return ([grouping_competitor], event_ids)
        else:
            print('')
            print("ERROR!! Competitor '{}' not found.".format(scoresheet_competitor_name))
            sys.exit()
    return (result_string, event_ids)

### WCA WCIF
# Get competitor information: name, WCA ID, date of birth, gender, country, competition roles (organizer, delegate) and events registered for                
def get_registrations_from_wcif(wca_json, create_scoresheets_second_rounds_bool, use_cubecomps_ids, competitors, competitors_api, only_one_competitor, scoresheet_competitor_name):
    registration_id = 1   
    competitor_information_wca = []
    
    # Check if WCA registration was actually used
    try:
        wca_json['persons'][0]['registration']
        if not wca_json['persons'][0]['registration']: 
            return []
    except KeyError:
        return []
        
    with open('src/data/WCA_export_Countries.tsv', 'r') as country_file:
        countries = list(csv.reader(country_file, delimiter='\t'))[1:]
        
    for registrations in tqdm.tqdm(wca_json['persons']):
        registered_events = ()
        competitor_role = ''
        single = '0.00'
        average = '0.00'
        
        for country in countries:
            if country[3] == registrations['countryIso2']:
                comp_country = country[0]

        if registrations['roles']:
            for role in registrations['roles']:
                competitor_role = ''.join([competitor_role, role.replace('delegate', 'WCA DELEGATE').upper(), ','])
            competitor_role = competitor_role[:-1]
        for competitor_events in registrations['registration']['eventIds']:
            registered_events += (competitor_events,)
        for event_records in registrations['personalBests']:
            if (event_records['eventId'] == '333'):
                if(event_records['type'] == 'single'):
                    single = round(event_records['best'] / 100, 2)
                    if single >= 60:
                        single = helper.format_result(single)
                else:
                    average = round(event_records['best'] / 100, 2)
                    if average >= 60:
                        average = helper.format_result(average)
            
        information = {
                'name': registrations['name'].split(' (')[0].strip(), 
                'personId': registrations['wcaId'], 
                'dob': registrations['birthdate'], 
                'gender': registrations['gender'], 
                'country': comp_country, 
                'role': competitor_role, 
                'guests': str(registrations['registration']['guests']), 
                'registered_events': registered_events, 
                'registration_id': registration_id,
                'single': str(single),
                'average': str(average),
                'comp_count': 0
                }
                
        # Make this exception to use WCA /persons API only if needed (i.e. for everything except 
        # scoresheets for consecutive rounds
        if not create_scoresheets_second_rounds_bool:
            if registrations['wcaId']:
                if not only_one_competitor:
                    comp_count = apis.get_wca_competitor(registrations['wcaId'])['competition_count']
                    information.update(
                            {
                            'comp_count': comp_count,
                            'personal_bests': registrations['personalBests']
                            }
                        )
                if only_one_competitor and registrations['wcaId'] == scoresheet_competitor_name:
                    comp_count = apis.get_wca_competitor(registrations['wcaId'])['competition_count']
                    information.update(
                            {
                            'comp_count': comp_count,
                            'personal_bests': registrations['personalBests']
                            }
                        )
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
            
    return competitor_information_wca

# Parse information about event_id, round_number, # groups, format, cutoff, time limit and (possible) cumulative limits for each event
def get_events_from_wcif(wca_json, event_dict):
    minimal_scramble_set_count = 1
    group_list = []
    event_ids_wca = ()
    all_events = ()
    event_info = []
    for wca_events in wca_json['events']:
        all_events += (wca_events['id'],)
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
                    minutes, seconds = helper.format_minutes_and_seconds(wca_rounds['advancementCondition']['level'] / 100)
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
    round_counter = collections.Counter(event_ids_wca)
    event_list_wca = sorted(collections.Counter(all_events))
    event_counter_wca = len(event_list_wca)
    return (event_ids_wca, group_list, event_info, event_counter_wca, minimal_scramble_set_count, round_counter, event_list_wca)

# Get schedule information from WCIF
# Used for sorting of scrambler_list + creating a PDF containing the schedule
def get_schedule_from_wcif(wca_json):
    full_schedule, events_per_day, competing_day = [], [], []
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
    return (full_schedule, competition_days, competition_start_day, timezone_utc_offset, events_per_day)

# Group events by days to determin the competing days of each competitor
def get_events_per_day(schedule_event, events_per_day):
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
    return events_per_day

def get_competitor_events_per_day(registration_list, column_ids, events_per_day):
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

    return registration_list

# Update competitor information and collect all WCA ids
def prepare_registration_for_competitors(competitor_information, event_list_wca, number_events):
    registration_index = 0
    wca_ids = ()
    registration_list_wca = []
    
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
    return (wca_ids, registration_list_wca)

# Return useful format of the schedule times
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
