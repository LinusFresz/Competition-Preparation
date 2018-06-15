#!/usr/bin/python

from wca_registration import *


''' 
    This script creats various things a organizer needs to have for a competition:
    - competitor groupings
    - scrambling list for all events and rounds (except FMC)
    - nametags
    - scoresheets for first rounds
    
    System information: 
    This script was tested on Mac OS 10.13.4 with python 3.5.2
    Please be aware, that you need Chrome to be installed on your device.
    
    HOW TO:
    Make sure to add all event information in the 'Manage events' tab for your competition on the WCA website. To run the script, type into your terminal 'pyton scoresheets.py' and follow the steps shown in the window.
    
    Files that need to be in the same folder:
    - comeptition_preparation_start.py
    - competition_grouping_scrambling.py
    - wca_registration.py
    - information_analysis.py
    - nametags.py
    - scoresheets.py
    - scoresheets_second_rounds.py
    - chromedriver_data.py
    - chromedriver
    
    Please be aware that you need a WCA database connection. All necessary files can be found here: https://github.com/LinusFresz/python-WCA (section 'setup') 
    
    For further details and support, please contact Linus Frész, linuf95@gmail.com
'''


while True:
    program_type = input('Competition preparation (1) or scoresheets for second rounds (2)? ')
    print('')
    if program_type.isdigit() and program_type == '1':
        new_creation = True
        break
    elif program_type.isdigit() and program_type == '2':
        new_creation = False
        break
    else:
        print("Wrong input, please enter '1' or '2'.")
        print('')

# Get necessary information for new competition
if new_creation:
    wca_info = wca_registration_system()
    wca_id, wca_password, competition_name, competition_name_stripped, wcif_file = wca_registration(new_creation)
    file_name, file_name_csv, file_name_txt = competition_information_fetch(wca_info)
    
    store_file = competition_name + '/' + competition_name_stripped + '-grouping.txt'
    wcif_file = get_wca_info(wca_id, wca_password, competition_name, competition_name_stripped, store_file)
    
    print('Saved results, extracting data now.')  

# Get necessary information for scoresheets of a succeeding round
else:
    cubecomps_id = input('Link to previous round: ')
    advancing_competitors = int(input('Number of advancing competitors: '))

    driver.get(cubecomps_id)

    file = driver.find_element_by_xpath('html').text.split('\n')

    competition_name = file[0]
    competition_name_stripped = competition_name.replace(' ', '')
    competitors_start = False
    counter, competitor = 0, 0
    competitors = []

    event_dict = {'333': '3x3x3', '222': '2x2x2', '444': '4x4x4', '555': '5x5x5', '666': '6x6x6', '777': '7x7x7', '333bf': '3x3x3 Blindfolded', '333fm': '3x3x3 Fewest Moves', '333oh': '3x3x3 One-Handed', '333ft': '3x3x3 With Feet', 'clock': 'Clock', 'minx': 'Megaminx', 'pyram': 'Pyraminx', 'skewb': 'Skewb', 'sq1': 'Square-1', '444bf': '4x4x4 Blindfolded', '555bf': '5x5x5 Blindfolded', '333mbf': '3x3x3 Multi-Blindfolded'}

    for line in file:
        if ' - ' in line: 
            event_round_name = line

        if competitors_start:
            if counter % 4 == 1 and competitor < advancing_competitors:
                competitors.append({'name': line, 'ranking': competitor+1})
                competitor += 1
            counter += 1
        if '#' in line:
            competitors_start = True

    event_2 = event_round_name.split(' - ')[0].replace(' Cube', '')
    for name in event_dict:
        if event_2 == event_dict[name]:
            event_2 = name
    current_round_number = event_round_name.split(' - ')[1].replace('Round', '').replace('Combined', 'Round').replace('Final', '').replace('First', '-r1').replace('Second', '-r2').replace('Semi', '-r3').replace(' ', '')[-1:]
    if current_round_number.isdigit():
        round_number = int(current_round_number) + 1
    else:
        print('Please open next round before using script. Script aborted.')
        sys.exit()

    next_round_name = event_round_name.split(' - ')[0].replace(' Cube', '') + ' -' + event_round_name.split(' - ')[1].replace('First', '').replace('Second', '').replace('Semi', '').replace('Combined ', ' Round') + ' ' + str(round_number)
    event_round_name = next_round_name

    wca_id, wca_password = wca_registration(new_creation)
    wca_info = wca_registration_system()
    file_name, file_name_csv, file_name_txt = competition_information_fetch(wca_info)

    wcif_file = get_wca_info(wca_id, wca_password, competition_name, competition_name_stripped, file)
