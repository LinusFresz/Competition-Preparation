### Lots of functions that do the actual grouping and scrambling in this script

from modules import *

events_ranking_by_speed = (
        '222', '333', '444',
        '333oh', '333bf', '333ft',
        'pyram', 'skewb'
        )

### Grouping for all events with given number of groups
# Grouping is done by ranking for all events in events_ranking_by_speed
# All other events use competitors ordered by last name
def grouping(registration_list, result_string, groups, event_column, event, ranking):
    event_count = competitors_per_event(registration_list, event_column)
    grouping_ranking = registration_list
    result_string_old = result_string

    # Rank competitors by speed for given set of events
    if event in events_ranking_by_speed:
        grouping_ranking, result_string = [], []
        for persons in ranking:
            for competitor in range(0, len(registration_list)):
                if persons[0] == registration_list[competitor][1]:
                    competitor_and_id = registration_list[competitor]
                    grouping_ranking.insert(0, competitor_and_id)
                    result_string.insert(0, result_string_old[competitor])
                    break

    group_size = round(event_count / groups, 0)  # Average number of competitors per group
    actual_group_size = 1
    group_number, counter = 0, 0
    for person in range(0, len(grouping_ranking)):
        if grouping_ranking[person][event_column] == '1':
            if (actual_group_size - 1) % group_size == 0:
                group_number += 1
                if group_number > groups:
                    group_number -= 1
            result_string[counter] += (str(group_number),)  # Adding group number for competitors
            actual_group_size += 1
        else:
            result_string[counter] += ('',)  # Leaving group empty if competitor doesn't compete
        counter += 1
    
    result_string = sorted(sorted(result_string, key=lambda x: x[0]), key=lambda x:x[0].split()[-1])
    return result_string

# Return number of competitors for given event
def competitors_per_event(grouping_list, event_column):
    event_count = 0
    for grouping_id in grouping_list:
        if grouping_id[event_column] == '1':
            event_count += 1
    return event_count

### Collect all rankings from SQL-List for choosen event
def get_event_results(event_ranking, ranking_single, event):
    for ranked_competitor in ranking_single:
        if event == ranked_competitor['eventId']:
            event_ranking.append(ranked_competitor)

### Select correct ranking for choosen event
def rankings(event_ranking, registration_list, ranking, event, event_column, ranking_single, result_string):
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

### Create grouping and select scramblers for each group
def select_scrambler(event, round_number, round_id, scrambler_count, first_place, last_place, groups, scrambling_run_id, result_string, ranking_single, competition_count, event_ids, event_ids_wca, column_ids, row_count, registration_list, scrambler_list, competitor_information, round_counter):
    ranking, event_ranking = [], []
    loop_counter = 1

    # Add correct columnid for events AND create grouping for first rounds
    if round_number == 1:
        if scrambling_run_id == 1:
            event_ids.update({event: row_count})
            row_count += 1

    # Create ranking for event
    for person in registration_list:
        ranking.append((person[1], person[3]))
    
    if scrambling_run_id == 2:
        rankings(event_ranking, registration_list, ranking, event[:3], column_ids[event], ranking_single, result_string)
    else:
        rankings(event_ranking, registration_list, ranking, event, column_ids[event], ranking_single, result_string)
    ranking = sorted(ranking, key=lambda x: x[2])
    if round_number == 1 and scrambling_run_id == 1:
        result_string = grouping(registration_list, result_string, groups, column_ids[event], event, ranking)
    
    max_competitors = competitors_per_event(registration_list, column_ids[event])
    if last_place > max_competitors:
        last_place = max_competitors
    if first_place >= last_place and scrambler_count_list[event] != 0:
        repeat_select_scrambler(event, round_number, round_id, scrambler_count, groups, 0, result_string, ranking_single, competition_count, event_ids, event_ids_wca, column_ids, row_count, registration_list, scrambler_list, round_counter)
        return (result_string, scrambler_list, event_ids, row_count)

    # Actual determination of scramblers happens here
    for group_number in range(1, groups + 1):
        exists = False
        for scrambler in range(0, len(scrambler_list)):
            if scrambler_list[scrambler][0] == round_id  and scrambler_list[scrambler][1] == groups:
                scrambler_list[scrambler] = [round_id, group_number]
                exists = True
        if not exists:
            scrambler_list.append([round_id, group_number])

        for scrambler in range(0, len(scrambler_list)):
            if scrambler_list[scrambler][0] == round_id:  # Only finishes after enough scramblers are in scrambling list for this group
                while len(scrambler_list[scrambler]) < (scrambler_count + 2):
                    random.seed()
                    rank = random.randrange(first_place, last_place)
                    not_double = checking(
                            ranking, event_ids, event, \
                            groups, rank, group_number, \
                            round_number, scrambler, first_place, \
                            last_place, scrambling_run_id, result_string, \
                            competition_count, scrambler_list, competitor_information, \
                            round_counter
                            )
                    
                    if not_double:
                        new_scrambler = ftfy.fix_text(ranking[rank][0])
                        scrambler_list[scrambler].append(new_scrambler)

                    if loop_counter % 10000 == 0:
                        last_place += 5
                        if last_place > max_competitors:
                            last_place = max_competitors
                
                        if loop_counter == 100000:
                            repeat_select_scrambler(event, round_number, round_id, scrambler_count, groups, group_number, result_string, ranking_single, competition_count, event_ids, event_ids_wca, column_ids, row_count, registration_list, scrambler_list, competitor_information, round_counter)
                            break
                    loop_counter += 1
    return (result_string, scrambler_list, event_ids, row_count)

### If not enough scramblers were found, use similar events to determine scramblers
# e.g. use competitors from 333 if not enough scramblers were found for 333bf, 333ft etc.
def repeat_select_scrambler(event, round_number, round_id, scrambler_count, groups, group_number, result_string, ranking_single, competition_count, event_ids, event_ids_wca, column_ids, row_count, registration_list, scrambler_list, competitor_information, round_counter):
    error_string = 'ERROR!! Not enough scramblers found for {}'.format(round_id)
    if group_number > 1:
        error_string = ''.join([error_string, ', Group {} of {} groups'.format(str(group_number), groups)])
    error_string_id = 'no_scramblers_{}'.format(event)
    if event[0].isdigit() and len(event) > 3 and event != '333mbf' and event[:3] in event_ids_wca:
        error_string = ''.join([error_string, ', replaced with competitors from {}.'.format(round_id[:5])])
        select_scrambler(event, round_number, round_id, scrambler_count, 0, 40, groups, 2, result_string, ranking_single, competition_count, event_ids, event_ids_wca, column_ids, row_count, registration_list, scrambler_list, competitor_information, round_counter)
        found_scrambler = True
    ErrorMessages.messages.update({error_string_id: error_string})

### Check if scrambler can be used
# Conditions that a scrambler can NOT be selected:
# - is in same group
# - has no official result in this event
# - is already scrambler for this group
# - competitor has 5 or more competitions
# - person is organizer or delegate
# - competitor already scrambles a lot which is defined by function scrambling_average(): if the competitor scrambles more than (average + 2) he won't be selected this time

# extra conditions for second and third rounds with more than one group:
# - use fast scramblers for first groups (with slower people) and slow scramblers for last groups (faster people)

# extra conditions for finals with only one group:
# - scrambler is in topX of this event

# - special conditions if in previous run not enough scramblers were found (scrambling_run_id == 2):
# - competitor does not compete in event (i.e. persons from 3x3x3 get selected for 3x3x3 Blindfolded)
def checking(ranking, event_ids, event, groups, rank, group_number, round_number, scrambler, first_place, last_place, scrambling_run_id, result_string, competition_count, scrambler_list, competitor_information, round_counter):
    if scrambling_run_id == 2:
        previous_event = event
        event = event[:3]
    # Has result in event
    if ranking[rank][2] == 99999:
        return 0
    # Is not already scrambler for same group
    for scrambling_place in range(2, len(scrambler_list[scrambler])):
        if ftfy.fix_text(ranking[rank][0]) == ftfy.fix_text(scrambler_list[scrambler][scrambling_place]):
            return 0
    # Has more than 5 comps
    for counts in competition_count:
        if ranking[rank][1] == counts['personId']:
            if counts['companzahl'] < 5:
                return 0
    # For consecutive rounds
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
    # Is neither organizer nor delegate of competition
    for person in competitor_information:
        if ranking[rank][1] == person['personId']:
            for role in ('organizer', 'delegate'):
                if role.upper() in person['role']:
                    return 0
    for person in result_string:
        if person[2] == ranking[rank][1]:
            # Does not compete in sub-events (e.g. 3x3x3 for 3x3x3 blindfolded)
            if scrambling_run_id == 2:
                if person[event_ids[previous_event]]:
                    return 0
                else:
                    return 1
            # Is not registered for event
            if not person[event_ids[event]]:
                return 0
            # Is in same group he should scramble
            if person[event_ids[event]] == str(group_number) and round_number in (1, round_counter[event]):
                return 0
    # Scrambles more than average + x
    average = scrambling_average(ranking[rank][1], result_string, scrambler_list)
    if average[0] > (average[1] + 1.5):
        return 0
    return 1

# Part of the checking process: check if scrambler does already scramble more than average
def scrambling_average(personId, result_string, scrambler_list):
    scrambling_count_list = ()
    scramble_count_person = 0
    for persons in result_string:
        scramble_count = 0
        for scrambler in scrambler_list:
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

### Create grouping and scrambling for all events of competition
def run_grouping_and_scrambling(group_list, result_string, registration_list, column_ids, ranking_single, competition_count, event_ids, event_ids_wca, competitor_information, round_counter):
    previous_event = ''
    scrambler_count_list = {}
    scrambler_list = []
    row_count = 3
    
    # Hard coded definition of number of scramblers per event
    for event in ('333fm', '333mbf'):
        scrambler_count_list.update({event: 0})
    for event in ('333bf', '333ft', '444bf', '555bf'):
        scrambler_count_list.update({event: 3})
    for event in ('222', '333', '444', '555', '333oh', 'pyram', 'minx', 'skewb', 'sq1'):
        scrambler_count_list.update({event: 4})
    for event in ('555', '666', '777', 'clock'):
        scrambler_count_list.update({event: 5})
    for rounds in group_list:
        event, round_name, round_number, groups = get_event_round_information(rounds)

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
        
        result_string, scrambler_list, event_ids, row_count = select_scrambler(
                event, round_number, round_name, \
                scrambler_count_list[event], min_scrambler, \
                top_scrambler, groups, 1, \
                result_string, ranking_single, competition_count, \
                event_ids, event_ids_wca, column_ids, \
                row_count, registration_list, scrambler_list, \
                competitor_information, round_counter
                )
        previous_event = event
        advancing_competitors = rounds[3]
        previous_competitors_in_event = competitors_in_event
    return (result_string, scrambler_list)

# Return event name, round name, round number and number of groups for given event
def get_event_round_information(event_rounds):
    return (event_rounds[0], event_rounds[1], int(event_rounds[1][-1:]), event_rounds[2])

# Update event index for given event
def update_event_ids(group_list, event_ids):
    row_count = 3
    for event_rounds in group_list:
        event, round_name, round_number, groups = get_event_round_information(event_rounds)
        advancing_competitors = event_rounds[3]
        if round_number == 1:
            event_ids.update({event: row_count})
            row_count += 1
    return (event_ids)

# Update column index for given event
def update_column_ids(event_list_wca, column_ids):
    event_list = ()
    counter = 0
    for event in event_list_wca:
        if event in column_ids:
            column_ids.update({event: counter + 6})
            event_list += (event,)
            counter += 1
    return(column_ids, event_list)

### If schedule is given, sort scrambling list by this schedule to give it a nice format
def sort_scrambler_by_schedule(full_schedule, scrambler_list, round_counter):
    scrambler_list_sorted_by_schedule = []
    for schedule_event in full_schedule:
        if schedule_event['round_number']:
            for event_scrambler in scrambler_list:
                if schedule_event['event_name'] == event_scrambler[0]:
                    round_name = event_scrambler[0]
                    replace_string = ' Round {}'.format(event_scrambler[0][-1:])
                    if event_scrambler[0][-1:] == '3' and round_counter[schedule_event['event_id']] != 3:
                        round_name = round_name.replace(replace_string, ' Semi Final')
                    elif event_scrambler[0][-1:] == str(round_counter[schedule_event['event_id']]):
                        round_name = round_name.replace(replace_string, ' Final')
                    event_scrambler[0] = round_name
                    
                    scrambler_list_sorted_by_schedule.append(event_scrambler)
    return scrambler_list_sorted_by_schedule

### Use WCA ids of competitors to get their best results for all events of the competition + 333 single and average
def get_results_from_wca_export(event_list, wca_ids, competitor_information, create_only_nametags):
    if not create_only_nametags:
        ranking_single = WCA_Database.query("SELECT * FROM RanksSingle WHERE eventId IN %s", (event_list,)).fetchall()
    competition_count = WCA_Database.query("SELECT res.personId, companzahl FROM Results AS res INNER JOIN (SELECT r.personId, COUNT(DISTINCT r.competitionId) AS companzahl FROM Results AS r WHERE r.personId IN %s GROUP BY r.personId) x ON res.personId = x.personId WHERE res.personId IN %s GROUP BY res.personId", (wca_ids, wca_ids)).fetchall()
    single = WCA_Database.query("SELECT * FROM RanksSingle WHERE eventId = '333' and personId in %s", (wca_ids,)).fetchall()
    average = WCA_Database.query("SELECT * FROM RanksAverage WHERE eventId = '333' and personId in %s", (wca_ids,)).fetchall()

    for person in competitor_information:
        single_result = get_result(person, single)
        average_result = get_result(person, average)

        comp_count = 0
        for id in competition_count:
            if person['personId'] == id['personId']:
                comp_count = id['companzahl']
                break
        person.update({'comp_count': comp_count, 'single': single_result, 'average': average_result})
    return (competitor_information, ranking_single, competition_count)

# Get a specific result
def get_result(person, results_event):
    result = '0.00'
    for id in results_event:
        if person['personId'] == id['personId']:
            result = str(round(id['best'] / 100, 2))
            break

    while len(result.split('.')[1]) < 2:
        result = ''.join([result, '0'])
    return result
