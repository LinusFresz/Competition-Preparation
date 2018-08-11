#!/usr/bin/python

import random
import labels
from information_analysis import *
from nametags import *
from scoresheets_second_rounds import *

error_messages = {}

def competitors_per_event(grouping_list, event_column):
    event_count = 0
    for k in grouping_list:
        if k[event_column] == '1':
            event_count += 1
    return event_count

### Grouping for all events with given number of groups ###
def grouping(registration_list, groups, event_column):
    event_count = competitors_per_event(registration_list, event_column)

    group_size = round(event_count / groups, 0)  # Average number of competitors per group
    l = 1
    m = 0  # Count of groups
    counter = 0
    for k in range(0, len(registration_list)):
        if registration_list[k][event_column] == '1':
            if (l - 1) % group_size == 0:
                m += 1
                if m > groups:
                    m -= 1
            result_string[counter] += (m,)  # Adding group number for competitors
            l += 1
        else:
            result_string[counter] += ('',)  # Leaving group empty if competitor doesn't compete
        counter += 1


### Collects all rankings from SQL-string for choosen event ###
def get_event_results(event_ranking, rows, event):
    for k in rows:
        if event == k['eventId']:
            event_ranking.append(k)


### Selects correct ranking for choosen event ###
def rankings(event_ranking, result_string, ranking, event):
    get_event_results(event_ranking, rows, event)
    for k in range(0, len(result_string)):
        true = 0
        for l in event_ranking:
            if result_string[k][2] == l['personId']:
                if result_string[k][event_ids[event]]:
                    ranking[k] += (l['best'],)
                    true = 1
                    break
        if not true:
            ranking[k] += (99999,)


### Create new string for grouping and add name + DOB ###
result_string = []

for k in registration_list:
    result_string.append((k[1], k[2], k[3]))


def repeat_selectscrambler(event, round_number, round_id, scrambler_count, groups):
    error_string = 'ERROR!! Not enough scramblers found for ' + event + ', ' + round_id
    error_string_id = 'no_scramblers_' + event
    if event[0].isdigit() and len(event) > 3 and event != '333mbf' and event[:3] in event_ids_wca:
        error_string = 'Not enough scramblers found for ' + round_id + ', replaced with competitors from ' + round_id[:5] + '.'
        selectscrambler(event, round_number, round_id, scrambler_count, 0, 40, groups, 2)
    error_messages.update({error_string_id: error_string})


scramblerlist = []
rowcount = 3  # first column with grouping-data

event_ids = {'333': 999, '222': 999, '444': 999, '555': 999, '666': 999, '777': 999, '333bf': 999, '333fm': 999, '333oh': 999, '333ft': 999, 'minx': 999, 'pyram': 999, 'clock': 999, 'skewb': 999, 'sq1': 999, '444bf': 999, '555bf': 999, '333mbf': 999} 

### Select scramblers for each group and creates grouping ###
def selectscrambler(event, round_number, round_id, scrambler_count, first_place, last_place, groups, scrambling_run_id):
    global rowcount
    ranking = []
    event_ranking = []
    loop_counter = 1

    if event not in event_ids:
        error_string = 'ERROR!! Event ' + event + ', ' + round_id, ' does not exist. Please choose correct Event-Id.'
        error_string_id = event + round_id
        error_messages.update({error_string_id: error_string})
        return

    # Adds correct columnid for events AND creates grouping for first rounds
    if round_number == 1:
        if scrambling_run_id == 1:
            event_ids.update({event: rowcount})
        grouping(registration_list, groups, column_ids[event])
        rowcount += 1

    for k in registration_list:
        ranking.append((k[1], k[3]))
    
    if scrambling_run_id == 2:
        rankings(event_ranking, result_string, ranking, event[:3])
    else:
        rankings(event_ranking, result_string, ranking, event)
    ranking = sorted(ranking, key=lambda x: x[2])

    max_competitors = competitors_per_event(registration_list, column_ids[event])
    if last_place > max_competitors:
        last_place = max_competitors

    if first_place >= last_place and scrambler_count_list[event] != 0:
        repeat_selectscrambler(event, round_number, round_id, scrambler_count, groups)
        return 0

    # Actual grouping happens here
    for group_number in range(1, groups + 1):
        exists = False
        for scrambler in range(0, len(scramblerlist)):
            if scramblerlist[scrambler][0] == round_id  and scramblerlist[scrambler][1] == groups:
                scramblerlist[scrambler] = [round_id, group_number]
                exists = True
        if not exists:
            scramblerlist.append([round_id, group_number])

        for scrambler in range(0, len(scramblerlist)):
            if scramblerlist[scrambler][0] == round_id:  # Only finishes after enough scramblers are in list
                while len(scramblerlist[scrambler]) < (scrambler_count + 2):
                    rank = random.randint(first_place, last_place)

                    not_double = checking(ranking, event_ids, event, groups, rank, group_number, round_number, scrambler, first_place, last_place, scrambling_run_id)

                    if not_double:
                        new_scrambler = unicodedata.normalize('NFKD', ranking[rank][0])
                        scramblerlist[scrambler].append(new_scrambler)

                    if loop_counter % 10000 == 0:
                        last_place += 5
                        if last_place > max_competitors:
                            last_place = max_competitors
                
                        if loop_counter == 100000:
                            repeat_selectscrambler(event, round_number, round_id, scrambler_count, groups)
                            break
                    loop_counter += 1

# Part of the checking process: check if scrambler already scrambles more than average
def scrambling_average(personId):
    scrambling_count_list = ()
    scramble_count_person = 0
    for persons in result_string:
        scramble_count = 0
        for k in scramblerlist:
            if persons[0] in k:
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


### Check if scrambler can be used ###
# Conditions so that scrambler can NOT be selected:
# - is in same group
# - has no official result in this event
# - is already scrambler for this group
# - competitor has 5 or more competitions
# - person is organizer or delegate
# - competitor already scrambles a lot which defined by function scrambling_average(): if the competitor scrambles more than (average + 2) he won't be selected this time

# extra conditions for second and third rounds with more than one group:
# - use fast scramblers for first groups (with slower people) and slow scramblers for last groups (faster people)

# extra conditions for finals with only one group:
# - scrambler is in top16 of this event

# - Special conditions if in previous run not enough scramblers were found (scrambling_run_id == 2):
# - competitor does not compete in event (i.e. persons from 3x3x3 get selected for 3x3x3 Blindfolded)
def checking(ranking, event_ids, event, groups, rank, group_number, round_number, scrambler, first_place, last_place, scrambling_run_id):
    
    if scrambling_run_id == 2:
        previous_event = event
        event = event[:3]
    
    if ranking[rank][2] == 99999:
        return 0
    
    for m in range(0, len(scramblerlist[scrambler])):
        if ranking[rank][0] == scramblerlist[scrambler][m]:
            return 0  
    
    for m in competition_count:
        if ranking[rank][1] == m['personId']:
            if m['companzahl'] < 5:
                return 0   

    if round_number != 1 and round_number != round_counter[event]:
        if groups == 1:
            if rank not in range(first_place, last_place):
                return 0
        if groups > 1:
            if group_number == 1:
                if rank >= round(0.8 * last_place / groups, 0):
                    return 0
            elif group_number == groups:
                if rank < round(1.2 * last_place / groups, 0):
                    return 0
            elif group_number > 1 and group_number < groups:
                if rank < round(1.1 * group_number * last_place / groups, 0) and rank > round(0.9 * (group_number - 1) * last_place / groups, 0):
                    return 0

    for person in competitor_information:
        if ranking[rank][1] == person['personId']:
            for role in ('organizer', 'delegate'):
                if role.upper() in person['role']:
                    return 0 

    for k in result_string:            
        if k[2] == ranking[rank][1]:
            if scrambling_run_id == 2:
                if k[event_ids[previous_event]]:
                    return 0
                else:
                    return 1
        
            if not k[event_ids[event]]:         
                return 0
            if k[event_ids[event]] == group_number and round_number in (1, round_counter[event]):
                return 0

    average = scrambling_average(ranking[rank][1])
    if average[0] > (average[1] + 2):
        return 0

    return 1


### Selection of necessary information from WCA database export. Information include: ###
# - Rankings for all events at competition
# - Competition count per competitor
# - Single and average rankings for 3x3x3 for each competitior
print('Get necessary results from WCA Export, this may take a few seconds...')

cur.execute("SELECT * FROM RanksSingle WHERE eventId IN %s", (event_list,))

rows = cur.fetchall()

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


print('Running grouping and scrambling...')

### Create scrambling and Grouping ###
# Syntax of grouping and scrambling function: 
# selectscrambler(event, roundnumber, eventid, scrambler, firstscrambler, lastscrambler, groups)

# - definition of # scramblers per event
scrambler_count_list = {}
for event in ('333fm', '333mbf'):
    scrambler_count_list.update({event: 0})
for event in ('222', '333bf', '333ft', '333oh', '444bf', '555bf', 'pyram', 'skewb'):
    scrambler_count_list.update({event: 3})
for event in ('333', '444', '555', 'minx', 'sq1'):
    scrambler_count_list.update({event: 4})
for event in ('555', '666', '777', 'clock'):
    scrambler_count_list.update({event: 5})

if new_creation:
    for rounds in group_list:
        event = rounds[0]
        round_name = rounds[1]
        round_number = int(rounds[1][-1:])
        groups = rounds[2]
    
        if round_number == round_counter[event]:
            replace_string = ' Round ' + str(round_number)
            if round_number == 3 and round_counter[event] != 3:
                round_name = round_name.replace(replace_string, ' Semi Final')
            else:
                round_name = round_name.replace(replace_string, ' Final')

        if groups > 1:
            competitor_count = competitors_per_event(registration_list, column_ids[event])
            top_scrambler = int(round(0.5 * competitor_count, 0))
            min_scrambler = 0
        else:
            min_scrambler = 12
            if top_scrambler < 12:
                top_scrambler = competitors_per_event(registration_list, column_ids[event])

        selectscrambler(event, round_number, round_name, scrambler_count_list[event], min_scrambler, top_scrambler, groups, 1)


    print('Grouping and scrambling done.')
    print('Saving files...')

# Add columns for events with < 5 scramblers
    for k in range(0, len(scramblerlist)):
        while len(scramblerlist[k]) < 7:
            scramblerlist[k].append('dummy name')

### Save results to files ###
# Write grouping and scrambling in separate files
output_registration = competition_name + '/registration.csv'
output_scrambling = competition_name + '/scrambling.csv'
output_grouping = competition_name + '/grouping.csv'

os.remove(wcif_file.name)

competitor_information_nametags = sorted(competitor_information, key=lambda x: x['name'])
result_string_nametags = sorted(result_string, key=lambda x: x[0])

sheet = labels.Sheet(specs, write_name, border=True)
sheet.add_labels(name for name in competitor_information_nametags)
nametag_file = competition_name + '/' + competition_name_stripped + '-nametags.pdf'
sheet.save(nametag_file)

if len(result_string_nametags) % 2 == 1:
    result_string_nametags.append(('', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',),)
for person in range(0, len(result_string_nametags)):
    if person % 2 == 0:
        swapping_id = person + 1
        swapping_person = result_string_nametags[swapping_id]
        result_string_nametags[swapping_id] = result_string_nametags[person]
        result_string_nametags[person] = swapping_person

sheet = labels.Sheet(specs, write_grouping, border=True)
sheet.add_labels((name, result_string_nametags, event_ids, scramblerlist) for name in result_string_nametags)
grouping_nametag_file = competition_name + '/' + competition_name_stripped + '-nametags-grouping.pdf'
sheet.save(grouping_nametag_file)

if two_sided_nametags:
    pdf_splitter(grouping_nametag_file)
    pdf_splitter(nametag_file)

    paths1 = glob.glob(competition_name + '/' + competition_name_stripped + '-nametags_*.pdf')
    paths2 = glob.glob(competition_name + '/' + competition_name_stripped + '-nametags-grouping_*.pdf')
    paths = paths1 + paths2
    paths = sorted(paths, key=lambda x: x.split('_')[2])

    merger(nametag_file, paths)
    os.remove(grouping_nametag_file)


for file_name in (output_registration, output_scrambling, output_grouping):
    if os.path.exists(file_name):
        print('File ' + file_name + ' already exists, backed up!')
        backup_name = file_name.split('/')[0] + '/' + '#' + file_name.split('/')[1]
        os.rename(file_name, backup_name)

# registration file
with open(output_registration, 'w') as registration_file:
    print('Name, Country, WCA ID, Date of Birth, Gender, Guests, Comment, Check Box', file=registration_file)
    for competitor in registration_list:
        competitor_info = ''
        for column in range(1, column_ids[min(column_ids, key=column_ids.get)]):
            competitor_info += competitor[column] + ','
        if competitor[0].isdigit():
            competitor_info += competitor[0] + ','
        else:
            competitor_info += '0,'
        if not competitor[3]:
            competitor_info += 'Newcomer (Check identification!)'
        competitor_info += ','
        print(competitor_info, file=registration_file)

# scrambling file
with open(output_scrambling, 'w') as scrambling_file:
    header = 'Event, Group, Scrambler 1, Scrambler 2, Scrambler 3, Scrambler 4, Scrambler 5'

    print('Scrambling List ' + competition_name, file = scrambling_file)

    print(header, file = scrambling_file)

    for k in scramblerlist:
        if 'Fewest Moves' not in k[0]:
            scramblers_clean = ()
            scramblers = (k[2], k[3], k[4], k[5], k[6])
            sorted_scramblers = sorted(scramblers, key=lambda x: x.split()[-1])
            for m in range(0, len(scramblers)):
                scramblers_clean += (sorted_scramblers[m].replace('dummy name', ''),)
            print(k[0], ',', k[1], ',', scramblers_clean[0], ',', scramblers_clean[1], ',', scramblers_clean[2], ',', scramblers_clean[3], ',', scramblers_clean[4], file = scrambling_file)

# grouping file
with open(output_grouping, 'w') as grouping_file:
    header = ', Name'
    for event in ('333', '222', '444', '555', '666', '777', '333bf', '333fm', '333oh', '333ft', 'minx', 'pyram', 'clock', 'skewb', 'sq1', '444bf', '555bf', '333mbf'):
        if event in event_ids and event_ids[event] != 999:
            header += ',' + event_dict[event]

    print(header, file = grouping_file)

    l = 0
    for k in result_string:
        l += 1
        grouping_list = str(l) + ',' + k[0]
        
        for event in ('333', '222', '444', '555', '666', '777', '333bf', '333fm', '333oh', '333ft', 'minx', 'pyram', 'clock', 'skewb', 'sq1', '444bf', '555bf', '333mbf'):
                if event in event_ids and event_ids[event] != 999:
                    grouping_list += ',' + str(k[event_ids[event]])

        print(grouping_list, file = grouping_file)

        if l % 32 == 0:
            print(header, file = grouping_file)
            print(header, file = grouping_file)


print('')
print('Scrambling and grouping successfully saved. Registration-sheet created. Nametags compiled into PDF: {0:d} label(s) output on {1:d} page(s).'.format(sheet.label_count, sheet.page_count))
print('')

