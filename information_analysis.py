########
# Data extraction of WCIF and registration file (if used).

import pytz
import datetime
import ftfy
from pdf_file_generation import format_minutes_and_seconds

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

def get_registrations_from_wcif(wca_json, countries, create_scoresheets_second_rounds_bool, use_cubecomps_ids, competitors, competitors_api):
    registration_id = 1   
    all_events = () 
    competitor_information_wca = []
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
    return (competitor_information_wca, all_events)

def get_events_from_wcif(wca_json, event_dict):
    minimal_scramble_set_count = 1
    event_counter_wca = 0
    group_list = []
    event_ids_wca = ()
    event_info = []
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
    return (event_ids_wca, group_list, event_info, event_counter_wca, minimal_scramble_set_count)
    
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
