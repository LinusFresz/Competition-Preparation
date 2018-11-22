#!/usr/bin/python

'''
    This file contains:
    - grouping
    - selection of scramblers
    - nametags
    - scoresheets
'''

from information_analysis import *
from scoresheets_functions import *

if blank_sheets:
    print('Creating blank sheets...')
    create_blank_sheets(write_blank_sheets, competition_name, scrambler_signature, blank_sheets_round_name)
    
if create_scoresheets_second_rounds_bool:
    print('Creating scoresheets for ' + event_round_name + '...')
    create_scoresheets_second_rounds(write_scoresheets_second_round, competition_name, competitor_information, advancing_competitors_next_round, event_round_name, event_info, event_2, next_round_name, event, scrambler_signature)

error_messages = {}

scramblerlist, result_string, scramblerlist_sorted_by_schedule = [], [], []
rowcount = 3

event_ids = {'333': 999, '222': 999, '444': 999, '555': 999, '666': 999, '777': 999, '333bf': 999, '333fm': 999, '333oh': 999, '333ft': 999, 'minx': 999, 'pyram': 999, 'clock': 999, 'skewb': 999, 'sq1': 999, '444bf': 999, '555bf': 999, '333mbf': 999} 
events_ranking_by_speed = ('222', '333', '444', '333oh', '333bf', '333ft', 'pyram', 'skewb')

### Create new string for grouping and add name + DOB
if registration_list:
    for person in registration_list:
        result_string.append((person[1], person[2], person[3]))
        
### Check for matching registration and grouping information
if create_only_nametags:
    result_string = get_grouping_from_file(grouping_file_name, event_dict, event_ids, only_one_competitor, scoresheet_competitor_name)
    new_result_string = []
    new_competitor_information = []
    if len(competitor_information) != len(result_string):
        print('')
        print('ERROR! Count of registrations in grouping file and WCA website does not match.')
        for registered_competitor in competitor_information:
            for competitor_grouping in result_string:
                if ftfy.fix_text(registered_competitor['name']) == ftfy.fix_text(competitor_grouping[0]):
                    new_result_string.append(competitor_grouping)
                    new_competitor_information.append(registered_competitor)
                    break
    
    if len(new_competitor_information) <= len(competitor_information):
        print('Using only information that were found on both platforms.')
        print('')
        competitor_information = new_competitor_information
        result_string = new_result_string
    else:
        print('ERROR!!')

def competitors_per_event(grouping_list, event_column):
    event_count = 0
    for grouping_id in grouping_list:
        if grouping_id[event_column] == '1':
            event_count += 1
    return event_count

### Grouping for all events with given number of groups
def grouping(registration_list, result_string, groups, event_column, event, ranking):
    event_count = competitors_per_event(registration_list, event_column)
    
    grouping_ranking = registration_list
    result_string_old = result_string

    if event in events_ranking_by_speed:
        #for events in round_counter:
        #    if event == events and round_counter[events] == 1:
        grouping_ranking = []
        result_string = []
        for persons in ranking:
            for competitor in range(0, len(registration_list)):
                if persons[0] == registration_list[competitor][1]:
                    competitor_and_id = registration_list[competitor]
                    grouping_ranking.insert(0, competitor_and_id)
                    result_string.insert(0, result_string_old[competitor])
                    break

    group_size = round(event_count / groups, 0)  # average number of competitors per group
    actual_group_size = 1
    group_number, counter = 0, 0
    for person in range(0, len(grouping_ranking)):
        if grouping_ranking[person][event_column] == '1':
            if (actual_group_size - 1) % group_size == 0:
                group_number += 1
                if group_number > groups:
                    group_number -= 1
            result_string[counter] += (str(group_number),)  # adding group number for competitors
            actual_group_size += 1
        else:
            result_string[counter] += ('',)  # leaving group empty if competitor doesn't compete
        counter += 1
    
    result_string = sorted(sorted(result_string, key=lambda x: x[0]), key=lambda x:x[0].split()[-1])

    return result_string

### Collect all rankings from SQL-string for choosen event
def get_event_results(event_ranking, ranking_single, event):
    for ranked_competitor in ranking_single:
        if event == ranked_competitor['eventId']:
            event_ranking.append(ranked_competitor)

### Select correct ranking for choosen event
def rankings(event_ranking, registration_list, ranking, event, event_column):
    get_event_results(event_ranking, ranking_single, event)
    for person in range(0, len(result_string)):
        has_ranking = False
        for person_event in event_ranking:
            if registration_list[person][3] == person_event['personId']:
                if registration_list[person][event_column]:
                    ranking[person] += (person_event['best'],)
                    has_ranking = True
                    break
        if not has_ranking:
            ranking[person] += (99999,)

def repeat_selectscrambler(event, round_number, round_id, scrambler_count, groups, result_string):
    error_string = 'ERROR!! Not enough scramblers found for ' + round_id
    error_string_id = 'no_scramblers_' + event
    if event[0].isdigit() and len(event) > 3 and event != '333mbf' and event[:3] in event_ids_wca:
        error_string = 'Not enough scramblers found for ' + round_id + ', replaced with competitors from ' + round_id[:5] + '.'
        selectscrambler(event, round_number, round_id, scrambler_count, 0, 40, groups, 2, result_string)
        found_scrambler = True
    error_messages.update({error_string_id: error_string})

### Select scramblers for each group and creates grouping
def selectscrambler(event, round_number, round_id, scrambler_count, first_place, last_place, groups, scrambling_run_id, result_string):
    global rowcount
    ranking = []
    event_ranking = []
    loop_counter = 1

    # add correct columnid for events AND create grouping for first rounds
    if round_number == 1:
        if scrambling_run_id == 1:
            event_ids.update({event: rowcount})
            rowcount += 1

    # create ranking for event
    for person in registration_list:
        ranking.append((person[1], person[3]))
    
    if scrambling_run_id == 2:
        rankings(event_ranking, registration_list, ranking, event[:3], column_ids[event])
    else:
        rankings(event_ranking, registration_list, ranking, event, column_ids[event])
    ranking = sorted(ranking, key=lambda x: x[2])
    
    if round_number == 1 and scrambling_run_id == 1:
        result_string = grouping(registration_list, result_string, groups, column_ids[event], event, ranking)    
    
    max_competitors = competitors_per_event(registration_list, column_ids[event])
    if last_place > max_competitors:
        last_place = max_competitors

    if first_place >= last_place and scrambler_count_list[event] != 0:
        repeat_selectscrambler(event, round_number, round_id, scrambler_count, groups, result_string)
        return result_string

    # actual determination of scramblers happens here
    for group_number in range(1, groups + 1):
        exists = False
        for scrambler in range(0, len(scramblerlist)):
            if scramblerlist[scrambler][0] == round_id  and scramblerlist[scrambler][1] == groups:
                scramblerlist[scrambler] = [round_id, group_number]
                exists = True
        if not exists:
            scramblerlist.append([round_id, group_number])

        for scrambler in range(0, len(scramblerlist)):
            if scramblerlist[scrambler][0] == round_id:  # only finishes after enough scramblers are in list
                while len(scramblerlist[scrambler]) < (scrambler_count + 2):
                    random.seed()
                    rank = random.randrange(first_place, last_place)

                    not_double = checking(ranking, event_ids, event, groups, rank, group_number, round_number, scrambler, first_place, last_place, scrambling_run_id, result_string)
                    
                    if not_double:
                        new_scrambler = unicodedata.normalize('NFKD', ranking[rank][0])
                        scramblerlist[scrambler].append(new_scrambler)

                    if loop_counter % 10000 == 0:
                        last_place += 5
                        if last_place > max_competitors:
                            last_place = max_competitors
                
                        if loop_counter == 100000:
                            repeat_selectscrambler(event, round_number, round_id, scrambler_count, groups, result_string)
                            break
                    loop_counter += 1

    return result_string

# part of the checking process: check if scrambler already scrambles more than average
def scrambling_average(personId):
    scrambling_count_list = ()
    scramble_count_person = 0
    for persons in result_string:
        scramble_count = 0
        for scrambler in scramblerlist:
            if persons[0] in scrambler:
                scramble_count += 1
        if persons[2] == personId:
            scramble_count_person = scramble_count
        if scramble_count > 0:
            scrambling_count_list += (scramble_count,)

    if len(scrambling_count_list) > 0:
        average_scrambling = sum(scrambling_count_list) / len(scrambling_count_list)
    else:
        average_scrambling = 0
    return scramble_count_person, average_scrambling


### Check if scrambler can be used
# conditions so that scrambler can NOT be selected:
# - is in same group
# - has no official result in this event
# - is already scrambler for this group
# - competitor has 5 or more competitions
# - person is organizer or delegate
# - competitor already scrambles a lot which is defined by function scrambling_average(): if the competitor scrambles more than (average + 2) he won't be selected this time

# extra conditions for second and third rounds with more than one group:
# - use fast scramblers for first groups (with slower people) and slow scramblers for last groups (faster people)

# extra conditions for finals with only one group:
# - scrambler is in top16 of this event

# - special conditions if in previous run not enough scramblers were found (scrambling_run_id == 2):
# - competitor does not compete in event (i.e. persons from 3x3x3 get selected for 3x3x3 Blindfolded)
def checking(ranking, event_ids, event, groups, rank, group_number, round_number, scrambler, first_place, last_place, scrambling_run_id, result_string):
    if scrambling_run_id == 2:
        previous_event = event
        event = event[:3]
    
    # has result in event
    if ranking[rank][2] == 99999:
        return 0

    # is not already scrambler for same group
    for scrambling_place in range(2, len(scramblerlist[scrambler])):
        if ftfy.fix_text(ranking[rank][0]) == ftfy.fix_text(scramblerlist[scrambler][scrambling_place]):
            return 0  
    
    # has more than 5 comps
    for counts in competition_count:
        if ranking[rank][1] == counts['personId']:
            if counts['companzahl'] < 5:
                return 0   

    # for consecutive rounds
    if round_number != 1:
        if groups == 1:
            if rank not in range(first_place, last_place):
                return 0
        else:
            if group_number == 1:
                if rank >= round(0.8 * last_place / groups, 0):
                    return 0
            elif group_number == groups:
                if rank < round(1.2 * last_place / groups, 0):
                    return 0
            elif group_number > 1 and group_number < groups:
                if rank < round(1.1 * group_number * last_place / groups, 0) and rank > round(0.9 * (group_number - 1) * last_place / groups, 0):
                    return 0

    # is neither organizer nor delegate of competition
    for person in competitor_information:
        if ranking[rank][1] == person['personId']:
            for role in ('organizer', 'delegate'):
                if role.upper() in person['role']:
                    return 0 

    for person in result_string:            
        if person[2] == ranking[rank][1]:
            # does not compete in sub-events (e.g. 3x3x3 for 3x3x3 blindfolded)
            if scrambling_run_id == 2:
                if person[event_ids[previous_event]]:
                    return 0
                else:
                    return 1
            
            # is not registered for event
            if not person[event_ids[event]]:         
                return 0

            # is in same group he should scramble
            if person[event_ids[event]] == str(group_number) and round_number in (1, round_counter[event]):
                return 0

    # scrambles more than average + x
    average = scrambling_average(ranking[rank][1])
    if average[0] > (average[1] + 1.5):
        return 0

    return 1

### Selection of necessary information from WCA database export. Information include:
# - rankings for all events at competition
# - competition count per competitor
# - single and average rankings for 3x3x3 for each competitior
if new_creation or create_only_nametags:
    if wca_ids and event_list:
        print('Get necessary results from WCA Export, this may take a few seconds...')
        
        if not create_only_nametags:
            cur.execute("SELECT * FROM RanksSingle WHERE eventId IN %s", (event_list,))
            ranking_single = cur.fetchall()

        cur.execute("SELECT res.personId, companzahl FROM Results AS res INNER JOIN (SELECT r.personId, COUNT(DISTINCT r.competitionId) AS companzahl FROM Results AS r WHERE r.personId IN %s GROUP BY r.personId) x ON res.personId = x.personId WHERE res.personId IN %s GROUP BY res.personId", (wca_ids, wca_ids))
        competition_count = cur.fetchall()

        cur.execute("SELECT * FROM RanksSingle WHERE eventId = '333' and personId in %s", (wca_ids,))
        single = cur.fetchall()

        cur.execute("SELECT * FROM RanksAverage WHERE eventId = '333' and personId in %s", (wca_ids,))
        average = cur.fetchall()

        for person in competitor_information:
            single_results = '0.00'
            for id in single:
                if person['personId'] == id['personId']:
                    single_results = str(round(id['best'] / 100, 2))

            while len(single_results.split('.')[1]) < 2:
                single_results += '0'
            average_result = '0.00'
            for id in average:
                if person['personId'] == id['personId']:
                    average_result = str(round(id['best'] / 100, 2))

            while len(average_result.split('.')[1]) < 2:
                average_result += '0'
            comp_count = 0
            for id in competition_count:
                if person['personId'] == id['personId']:
                    comp_count = id['companzahl']

            person.update({'comp_count': comp_count, 'single': single_results, 'average': average_result})

### Create scrambling and Grouping
# syntax of grouping and scrambling function: 
# selectscrambler(event, roundnumber, eventid, scrambler, firstscrambler, lastscrambler, groups)
# - definition of # scramblers per event
scrambler_count_list = {}
for event in ('333fm', '333mbf'):
    scrambler_count_list.update({event: 0})
for event in ('333bf', '333ft', '444bf', '555bf'):
    scrambler_count_list.update({event: 3})
for event in ('222', '333', '444', '555', '333oh', 'pyram', 'minx', 'skewb', 'sq1'):
    scrambler_count_list.update({event: 4})
for event in ('555', '666', '777', 'clock'):
    scrambler_count_list.update({event: 5})

if reading_grouping_from_file:
    for rounds in group_list:
        event = rounds[0]
        round_name = rounds[1]
        round_number = int(rounds[1][-1:])
        groups = rounds[2]
        advancing_competitors = rounds[3]
        if round_number == 1:
            event_ids.update({event: rowcount})
            rowcount += 1

previous_event = ''
advancing_competitors = ''
if new_creation:
    print('')
    print('Running grouping and scrambling...')
    for rounds in group_list:
        event = rounds[0]
        round_name = rounds[1]
        round_number = int(rounds[1][-1:])
        groups = rounds[2]
        
        if round_number == 1:
            competitors_in_event = competitors_per_event(registration_list, column_ids[event])
        else:
            competitors_in_event = previous_competitors_in_event
        
        if event != previous_event:
            advancing_competitors = ''
            
        if groups > 1:
            competitor_count = competitors_in_event
            top_scrambler = int(round(0.5 * competitor_count, 0))
            min_scrambler = 0
            if '%' in advancing_competitors:
                competitors_in_event = int(0.75 * competitors_in_event)
        else:
            if advancing_competitors.isdigit():
                min_scrambler = int(round(int(advancing_competitors) * 1.2, 0))
            else: 
                min_scrambler = int(round(0.8 * competitors_in_event, 0))
            if top_scrambler < min_scrambler:
                top_scrambler = competitors_in_event
        
        result_string = selectscrambler(event, round_number, round_name, scrambler_count_list[event], min_scrambler, top_scrambler, groups, 1, result_string)
        previous_event = event
        advancing_competitors = rounds[3]
        previous_competitors_in_event = competitors_in_event

    # Add dummy columns for events with < 5 scramblers
    for scrambler_id in range(0, len(scramblerlist)):
        while len(scramblerlist[scrambler_id]) < 7:
            scramblerlist[scrambler_id].append('dummy name')

    for schedule_event in full_schedule:
        if schedule_event['round_number']:
            for event_scrambler in scramblerlist:
                if schedule_event['event_name'] == event_scrambler[0]:
                    round_name = event_scrambler[0]
                    replace_string = ' Round ' + event_scrambler[0][-1:]
                    if event_scrambler[0][-1:] == '3' and round_counter[schedule_event['event_id']] != 3:
                        round_name = round_name.replace(replace_string, ' Semi Final')
                    elif event_scrambler[0][-1:] == str(round_counter[schedule_event['event_id']]):
                        round_name = round_name.replace(replace_string, ' Final')
                    event_scrambler[0] = round_name
                    
                    scramblerlist_sorted_by_schedule.append(event_scrambler)

    if scramblerlist_sorted_by_schedule:
        scramblerlist = scramblerlist_sorted_by_schedule
        
    print('Grouping and scrambling done.')

if reading_scrambling_list_from_file: 
    import csv
    with open(scrambling_file_name, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        scramblerlist = list(reader)
    del scramblerlist[0:2]

    for person in range(0, len(scramblerlist)):
        scramblerlist[person][1] = int(scramblerlist[person][1])
        
### Save results to files
if new_creation or blank_sheets or create_only_nametags:
    # write grouping and scrambling in separate files
    print('')
    print('Create nametags...')
    output_scrambling = competition_name + '/' + competition_name_stripped + 'Scrambling.csv'
    output_grouping = competition_name + '/' + competition_name_stripped + 'Grouping.csv'

    if new_creation:
        if os.path.exists(wcif_file):
            os.remove(wcif_file)
    
    sheet = create_nametag_file(competitor_information, competition_name, competition_name_stripped, two_sided_nametags, create_only_nametags, result_string, event_ids, scramblerlist, grouping_file_name, event_dict, only_one_competitor, round_counter, group_list, scoresheet_competitor_name)

    print('')
    print('Create scrambling and grouping file...')

    # grouping and scrambling file
    create_scrambling_file(output_scrambling, competition_name, scramblerlist)
    create_grouping_file(output_grouping, event_ids, event_dict, result_string)

    print('Scrambling and grouping successfully saved. Nametags compiled into PDF: {0:d} label(s) output on {1:d} page(s).'.format(sheet.label_count, sheet.page_count))
    print('')


### Loop to create all remaining files: grouping and scrambling
#EXCEPTION: no scoresheets created for 3x3x3 Fewest Moves
if new_creation or blank_sheets or reading_grouping_from_file:
    if reading_grouping_from_file: 
        result_string = get_grouping_from_file(grouping_file_name, event_dict, event_ids, only_one_competitor, scoresheet_competitor_name)
    
    print('Creating scoresheets...')
    create_scoresheets(competition_name, competition_name_stripped, result_string, event_ids, event_info, event_dict, only_one_competitor, round_counter, competitor_information, event, write_scoresheets, scoresheet_competitor_name, scrambler_signature, events_ranking_by_speed)
    
    # error handling for entire script
    if error_messages:
        print('')
        print('Notable errors while creating grouping and scrambling:')
        for errors in error_messages:
            print(error_messages[errors])
    else:
        print('')
        print('No errors while creating files.')

    print("Please see folder '" + competition_name + "' for files.")
    print('')

    if reading_grouping_from_file:
        quit_program(wcif_file)
