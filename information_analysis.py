#!/usr/bin/python

'''
Data extraction of WCIF and registration file (if used). Not too interesting, mainly a lot of parsing in .txt files (registration file and/or wcif file).    
'''

import ftfy
from collections import Counter
from competition_preparation_start import *
from db import WCA_Database
import unicodedata

events, events_now, persons, accepted, roles, cumulative_rounds = False, False, False, False, False, False

registered_events, final_registration_list, all_events, event_ids_wca = (), (), (), ()

registration_list_wca, group_list, competitor_information, competitor_information_wca, event_info = [], [], [], [], []

event_id, round_id, competitor_role, guests, cumulative = '', '', '', '', ''

event_counter_wca, group_count, cutoff_number, cutoff = 0, 0, 0, 0
registration_id = 1

event_dict = {'333': '3x3x3', '222': '2x2x2', '444': '4x4x4', '555': '5x5x5', '666': '6x6x6', '777': '7x7x7', '333bf': '3x3x3 Blindfolded', '333fm': '3x3x3 Fewest Moves', '333oh': '3x3x3 One-Handed', '333ft': '3x3x3 With Feet', 'clock': 'Clock', 'minx': 'Megaminx', 'pyram': 'Pyraminx', 'skewb': 'Skewb', 'sq1': 'Square-1', '444bf': '4x4x4 Blindfolded', '555bf': '5x5x5 Blindfolded', '333mbf': '3x3x3 Multi-Blindfolded'}
column_ids = {'333': 999, '222': 999, '444': 999, '555': 999, '666': 999, '777': 999, '333bf': 999, '333fm': 999, '333oh': 999, '333ft': 999, 'minx': 999, 'pyram': 999, 'clock': 999, 'skewb': 999, 'sq1': 999, '444bf': 999, '555bf': 999, '333mbf': 999}
formats = {'a': 5, 'm': 3}

if not blank_sheets:
    cur = WCA_Database.query("SELECT * FROM Countries")
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
         
        if events:
            if 'id' in line and (len(line) < 15 or '"333mbf"' in line):
                event_id = line[7:-2]
                event_counter_wca += 1
            elif 'id' in line and len(line) < 23:
                round_id = line[7:-2]
                for name in event_dict:
                    if round_id[:-3] == name:
                        round_id = round_id.replace(name, event_dict[name])
                round_id = round_id.replace('-r', ' - Round ')
            if 'scrambleGroupCount' in line:
                group_count = int(line[21:-1])

            if 'format' in line:
                if line[11:-2].isdigit():
                    format = int(line[11:-2])
                else:
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
                        line = line.replace(name, event_dict[name])
                line = line.replace('-r1', '')
                cumulative += line
            if 'cumulativeRoundIds' in line:
                cumulative_rounds = True
        if round_id != '' and group_count > 0:
            group_list.append((event_id, round_id, group_count))
            if event_id == '333mbf':
                limit = 3600
            event_infos = {'event': event_id, 'round': round_id[-1:], 'format': format, 'cutoff_number': cutoff_number, 'cutoff': cutoff, 'limit': limit, 'cumulative': cumulative}
            event_info.append(event_infos)
            event_ids_wca = event_ids_wca + (event_id,)
            cutoff_number, cutoff, group_count = 0, 0, 0
            cumulative, round_id = '', ''
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
                    if new_creation:
                        competitor_information_wca.append(information)
                    else:
                        for comp in competitors:
                            if name == ftfy.fix_text(comp['name']).split(' (')[0]:
                                information.update({'ranking': comp['ranking']})
                                competitor_information_wca.append(information)
                    registration_id += 1

                accepted = False
                competitor_role = ''

        if line.find('"persons":') != -1:
            persons = True

    if wca_info:
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
            os.remove(wcif_file.name)
            sys.exit()
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
        print('An error occured while importing the rounds and grouping information from the WCIF file, script aborted.')
        print('Please make sure to enter all necessary information in the "Manage events" tab on the WCA competition page.')
        os.remove(wcif_file.name)
        sys.exit()

    # Get data from csv-export
    # Same as for the WCA registration, get competitor information from registration file (if used): name, WCA ID, date of birth, gender, country and events registered for
    event_counter = 0
    registration_id = 1

    if not wca_info:
        print('Open registration file...')
        if os.path.isfile(file_name_txt):
            file = open(file_name_txt)
        else:
            file = open(file_name_csv)
    
        all_data = []
        wca_ids = ()
        event_list = ()
    
        l = 0
    
        for row in file:
            list = row.split(',')
            list[1] = list[1].split(' (')[0]
            last_entry = len(list) - 1
            list[last_entry] = list[last_entry].replace('\n', '')
            if l == 0:
                if not row.startswith('Status'):
                    print('')
                    print('ERROR!! Missing header-line in registration file, script aborted.')
                    os.remove(wcif_file.name)
                    sys.exit()
                counter = 0
                for event in list:
                    if event in column_ids:
                        new_id = {event: counter}
                        column_ids.update(new_id)
                        event_list += (event,)
                        event_counter += 1
                    counter += 1
        
            else:
                all_data.append(list)
                role = ''
                if list[3]:
                    for person in competitor_information_wca:
                        if list[3] == person['personId']:
                            if person['role']:
                                role = person['role']
                if new_creation:
                    competitor_information.append({'name': list[1], 'country': list[2], 'role': role, 'personId': list[3], 'registration_id': registration_id})
                else:
                    for comp in competitors:
                        if list[1] == comp['name'].split(' (')[0]:
                            competitor_information.append({'name': list[1], 'personId': list[3], 'ranking': comp['ranking'], 'registration_id': registration_id})    
                if list[3]:
                    wca_ids += (str(list[3]),)
                registration_id += 1
            l += 1
    
        registration_list = sorted(sorted(all_data, key= lambda x: x[1]), key=lambda x: x[1].split()[-1])
    
        if event_counter != event_counter_wca:
            print('ERROR!! Number of events from WCA Website does not match number of events in registration data. Please use correct registration file. Abort script.')
            os.remove(wcif_file.name)
            sys.exit()

    if wca_info:
        registration_list = registration_list_wca
