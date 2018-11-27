''' 
    Please read the README.md to get further information.
'''

from wca_registration import *

# collection of booleans and variables for various different options from this script
blank_sheets, create_only_nametags, new_creation, reading_scrambling_list_from_file, create_scoresheets_second_rounds_bool, reading_grouping_from_file, only_one_competitor, create_registration_file_bool, create_only_registration_file, read_only_registration_file, create_schedule, create_only_schedule, scrambler_signature, use_cubecomps_ids = (False for i in range(14))
get_registration_information, two_sided_nametags, valid_cubecomps_link = (True for i in range(3))
scoresheet_competitor_name, cubecomps_id = '', ''

event_dict = {
        '333': '3x3x3', '222': '2x2x2', '444': '4x4x4', '555': '5x5x5', 
        '666': '6x6x6', '777': '7x7x7', '333bf': '3x3x3 Blindfolded', 
        '333fm': '3x3x3 Fewest Moves', '333oh': '3x3x3 One-Handed', 
        '333ft': '3x3x3 With Feet', 'clock': 'Clock', 'minx': 'Megaminx', 
        'pyram': 'Pyraminx', 'skewb': 'Skewb', 'sq1': 'Square-1', 
        '444bf': '4x4x4 Blindfolded', '555bf': '5x5x5 Blindfolded', 
        '333mbf': '3x3x3 Multi-Blindfolded'
        }

### Selection of script functions
while True:
    print('Please select: ')
    print('1. Competition preparation (grouping, scrambling, scoresheets, nametags, schedule, registration file)')
    print('2. Scoresheets for consecutive rounds')
    print('3. Blank scoresheets')
    print('4. Registration information')    
    print('5. Nametags')
    print('6. Schedule')
    print('7. Scoresheets from grouping-file (all)')
    print('8. Scoresheets from grouping-file (for one person)')
    print('9. Quit')
    program_type = input('')
    print('')
    if program_type.isdigit():
        if program_type == '1':
            new_creation = True
            create_registration_file_bool = True
            create_schedule = True
            break
        elif program_type == '2':
            create_scoresheets_second_rounds_bool = True
            break
        elif program_type == '3':
            blank_sheets = True
            get_registration_information = False
            break
        elif program_type == '4':
            create_registration_file_bool = True
            create_only_registration_file = True
            new_creation = True
            break
        elif program_type == '5':
            create_only_nametags = True
            reading_grouping_from_file = True
            break
        elif program_type == '6':
            create_schedule = True
            create_only_schedule = True
            break
        elif program_type == '7':
            reading_grouping_from_file = True
            break
        elif program_type == '8':
            reading_grouping_from_file = True
            only_one_competitor = True
            break
        elif program_type == '9':
            print('Quitting programm.')
            sys.exit()
    
    print("Wrong input, please enter one of the available options.")
    print('')

### Evaluation of selection and initialization 
# get necessary information for new competition
if new_creation or create_only_nametags:
    bool = True
    wca_info = wca_registration_system()
    wca_password, wca_mail, competition_name, competition_name_stripped = wca_registration(bool)
    if not create_only_registration_file:
        two_sided_nametags = get_information('Create two-sided nametags? (grouping (and scrambling) information on the back) (y/n)')
        if two_sided_nametags:
            print('Using WCA registration and event information.')
        if not create_only_nametags:
            scrambler_signature = get_information('Add scrambler signature field to scorecards? (y/n)')
        
            print('Please enter cubecomps link to competition: (leave blank if not needed)')
            cubecomps_id = input()
        if cubecomps_id:
            competitors_api, use_cubecomps_ids = get_competitor_information_from_cubecomps(cubecomps_id, competition_name)
        
    if create_only_nametags and not two_sided_nametags and not wca_info:
        get_registration_information = False
        read_only_registration_file = True
        
    if create_only_nametags and two_sided_nametags:
        while True:
            print('Use scrambling-list for nametags? (y/n)')
            nametag_scrambling = input('')
            if nametag_scrambling.upper() in ('N', 'Y'):
                break
            else:   
                print("Wrong input, please enter 'y' or 'n'.")
                print('')

        if nametag_scrambling.upper() == 'Y':
            reading_scrambling_list_from_file = True
            scrambling_file_name = get_file_name('scrambling')

    file_name, grouping_file_name = competition_information_fetch(wca_info, False, create_only_nametags and two_sided_nametags, new_creation)

    if create_only_nametags and not two_sided_nametags and not wca_info:
        True
    else:
        competition_wcif_file = get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped)
    
    print('Saved results, extracting data now.')  
    
# create blank scoresheets
elif blank_sheets:
    scrambler_signature = get_information('Add scrambler signature field to scorecards? (y/n)')
    competition_name = input('Competition name: (leave empty if not wanted) ')
    blank_sheets_round_name = input('Round name: (leave empty if not needed) ')
    
# select grouping file if only nametags should be generated
elif reading_grouping_from_file:
    wca_info = wca_registration_system()
    wca_password, wca_mail, competition_name, competition_name_stripped = wca_registration(bool)
    scrambler_signature = get_information('Add scrambler signature field to scorecards? (y/n)')
    if only_one_competitor:
        scoresheet_competitor_name = input('Competitor Name: ')
    file_name, grouping_file_name = competition_information_fetch(wca_info, True, False, new_creation)
    competition_wcif_file = get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped)

# create schedule from wca website information
elif create_only_schedule:
    wca_info = wca_registration_system()
    if not wca_info:
        print('ERROR!! Schedule can only be generated from WCA website data. Script aborted.')
        sys.exit()
    wca_password, wca_mail, competition_name, competition_name_stripped = wca_registration(True)
    two_sided_nametags = False
    
    file_name, grouping_file_name = competition_information_fetch(wca_info, False, two_sided_nametags, new_creation)
    
    competition_wcif_file = get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped)
    
# create scoresheets for seconds rounds by using cubecomps.com information
elif create_scoresheets_second_rounds_bool:
    cubecomps_id = input('Link to previous round: ')
    cubecomps_api, competitors, event_round_name, advancing_competitors_next_round, competition_name, competition_name_stripped = get_round_information_from_cubecomps(cubecomps_id)
    
    event_2 = event_round_name.split(' - ')[0].replace(' Cube', '')
    event_2 = list(event_dict.keys())[list(event_dict.values()).index(event_2)]
    
    current_round_number = event_round_name.split(' - ')[1] \
            .replace('Round', '') \
            .replace('Combined', 'Round') \
            .replace('Final', '') \
            .replace('First', '-r1') \
            .replace('Second', '-r2') \
            .replace('Semi', '-r3') \
            .replace(' ', '')[-1:]
    if current_round_number.isdigit():
        round_number = int(current_round_number) + 1
    else:
        print('Please open next round before using script. Script aborted.')
        sys.exit()

    next_round_name = '{} -{} {}'.format(
            event_round_name.split(' - ')[0].replace(' Cube', ''), 
            event_round_name.split(' - ')[1] \
                    .replace('First', '') \
                    .replace('Second', '') \
                    .replace('Semi', '') \
                    .replace('Combined ', ' Round'), 
            str(round_number)
            )
    
    event_round_name = next_round_name.replace(' 4', '')

    wca_password, wca_mail = wca_registration(new_creation)
    wca_info = wca_registration_system()
    scrambler_signature = get_information('Add scrambler signature field to scorecards? (y/n)')
    file_name, grouping_file_name = competition_information_fetch(wca_info, False, False, new_creation)

    competition_wcif_file = get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped)
