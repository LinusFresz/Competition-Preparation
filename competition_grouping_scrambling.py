'''
    Please read the README.md to get further information.
'''

### Module import
from modules import *
from helpers.helpers import initiate_result_string, update_scrambler_list
from wca_registration import get_file_name, competition_information_fetch, wca_registration, get_wca_info, get_information, get_competitor_information_from_cubecomps, get_round_information_from_cubecomps
from information_analysis import column_ids, formats, format_names, get_registration_from_file, get_registrations_from_wcif, get_events_from_wcif, get_schedule_from_wcif, get_events_per_day, get_competitor_events_per_day, prepare_registration_for_competitors, get_grouping_from_file
from grouping_scrambling_functions import run_grouping_and_scrambling, update_event_ids, update_column_ids, sort_scrambler_by_schedule, get_competitor_results_from_wcif
from pdf_file_generation import create_blank_sheets, create_scoresheets, create_scoresheets_second_rounds, create_registration_file, create_schedule_file, create_nametag_file, create_scrambling_file, create_grouping_file

### Collection of booleans and variables for various different options from this script
# Most of these are used globally
blank_sheets, create_only_nametags, new_creation, reading_scrambling_list_from_file, create_scoresheets_second_rounds_bool, reading_grouping_from_file_bool, only_one_competitor, create_registration_file_bool, create_only_registration_file, read_only_registration_file, create_schedule, create_only_schedule, scrambler_signature, use_cubecomps_ids = (False for i in range(14))
get_registration_information, two_sided_nametags, valid_cubecomps_link = (True for i in range(3))
scoresheet_competitor_name, cubecomps_id, competitors = '', '', ''
competitors_api, scrambler_list, result_string = [], [], []

event_dict = {
        '333': '3x3x3', '222': '2x2x2', '444': '4x4x4', '555': '5x5x5',
        '666': '6x6x6', '777': '7x7x7', '333bf': '3x3x3 Blindfolded',
        '333fm': '3x3x3 Fewest Moves', '333oh': '3x3x3 One-Handed',
        '333ft': '3x3x3 With Feet', 'clock': 'Clock', 'minx': 'Megaminx',
        'pyram': 'Pyraminx', 'skewb': 'Skewb', 'sq1': 'Square-1',
        '444bf': '4x4x4 Blindfolded', '555bf': '5x5x5 Blindfolded',
        '333mbf': '3x3x3 Multi-Blindfolded'
        }
event_ids = {
        '333': 999, '222': 999, '444': 999, '555': 999,
        '666': 999, '777': 999, '333bf': 999, '333fm': 999,
        '333oh': 999, '333ft': 999, 'minx': 999, 'pyram': 999,
        'clock': 999, 'skewb': 999, 'sq1': 999, '444bf': 999,
        '555bf': 999, '333mbf': 999
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
            reading_grouping_from_file_bool = True
            break
        elif program_type == '6':
            create_schedule = True
            create_only_schedule = True
            break
        elif program_type == '7':
            reading_grouping_from_file_bool = True
            break
        elif program_type == '8':
            reading_grouping_from_file_bool = True
            only_one_competitor = True
            break
        elif program_type == '9':
            print('Quitting programm.')
            sys.exit()

    print("Wrong input, please enter one of the available options.\n")

### Evaluation of script selection and initialization
# Get necessary information for new competition
if new_creation or create_only_nametags:
    wca_info = get_information('Used WCA registration for this competition? (y/n) ')
    if wca_info:
        print('Using WCA registration information.')
    wca_password, wca_mail, competition_name, competition_name_stripped = wca_registration(True)
    if not create_only_registration_file:
        two_sided_nametags = get_information('Create two-sided nametags? (grouping (and scrambling) information on the back) (y/n)')
        if two_sided_nametags:
            print('Using WCA registration and event information.')
        if not create_only_nametags:
            scrambler_signature = get_information('Add scrambler signature field to scorecards? (y/n)')
        
            print('Please enter cubecomps link to competition: (leave blank if not needed)')
            print('If provided, the script will use registration ids from cubecomps for scoresheets. This ensures to have matching ids on all scoresheets and in cubecomps (which eases scoretaking a lot!). The registrations from the competition must be uploaded to cubecomps before using this option.')
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

    print('Saved registration information from WCA website, extracting data now.')

# Create blank scoresheets
elif blank_sheets:
    scrambler_signature = get_information('Add scrambler signature field to scorecards? (y/n)')
    competition_name = input('Competition name or ID: (leave empty if not wanted) ')
    blank_sheets_round_name = input('Round name: (leave empty if not needed) ')

# Select grouping file if only nametags should be generated
elif reading_grouping_from_file_bool:
    wca_info = get_information('Use WCA website information? (y/n) ')
    if wca_info:
        print('Using WCA website information.')
    wca_password, wca_mail, competition_name, competition_name_stripped = wca_registration(bool)
    scrambler_signature = get_information('Add scrambler signature field to scorecards? (y/n)')
    if only_one_competitor:
        scoresheet_competitor_name = input('Competitor name: ')
    file_name, grouping_file_name = competition_information_fetch(wca_info, True, False, new_creation)
    competition_wcif_file = get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped)

    if not create_only_nametags:        
        print('Please enter cubecomps link to competition: (leave blank if not needed)')
        cubecomps_id = input()
    if cubecomps_id:
        competitors_api, use_cubecomps_ids = get_competitor_information_from_cubecomps(cubecomps_id, competition_name)

# Create schedule from wca website information
elif create_only_schedule:
    wca_info = get_information('Use WCA website information? (y/n) ')
    if wca_info:
        print('Using WCA website information.')
    if not wca_info:
        print('ERROR!! Schedule can only be generated from WCA website data. Script aborted.')
        sys.exit()
    wca_password, wca_mail, competition_name, competition_name_stripped = wca_registration(True)
    two_sided_nametags = False
    
    file_name, grouping_file_name = competition_information_fetch(wca_info, False, two_sided_nametags, new_creation)
    
    competition_wcif_file = get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped)

# Create scoresheets for seconds rounds by using cubecomps.com information
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
    wca_info = get_information('Use WCA website information? (y/n) ')
    if wca_info:
        print('Using WCA website information.')
    scrambler_signature = get_information('Add scrambler signature field to scorecards? (y/n)')
    file_name, grouping_file_name = competition_information_fetch(wca_info, False, False, new_creation)

    competition_wcif_file = get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped)

### Get all information from wca competition (using WCIF) and collection information from WCA database export
if get_registration_information:
    # Extract data from WCIF file
    wca_json = json.loads(competition_wcif_file)
    
    # Registration
    competitor_information_wca = get_registrations_from_wcif(
            wca_json, create_scoresheets_second_rounds_bool, \
            use_cubecomps_ids, competitors, competitors_api \
            )
    
    # Events
    event_ids_wca, group_list, event_info, event_counter_wca, minimal_scramble_set_count, round_counter, event_list_wca = get_events_from_wcif(wca_json, event_dict)

    # Schedule
    full_schedule, competition_days, competition_start_day, timezone_utc_offset, events_per_day = get_schedule_from_wcif(wca_json)

    # Evaluate collected information
    if wca_info:
        competitor_information = competitor_information_wca
        
        wca_ids, registration_list_wca = prepare_registration_for_competitors(competitor_information, event_list_wca, len(event_list_wca))
        
        if not registration_list_wca:
            print('')
            print('ERROR!! WCA registration not used for this competition. Please select registration file for import. Script aborted.')
            sys.exit()
        registration_list_wca = sorted(sorted(registration_list_wca, key=lambda x: x[1]), key=lambda x: x[1].split()[-1])
    
        column_ids, event_list = update_column_ids(event_list_wca, column_ids)
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
    if not wca_info:
        print('Open registration file...')
        use_csv_registration_file = True
        column_ids, event_list, event_counter, competitor_information, all_data, wca_ids = get_registration_from_file(file_name, new_creation, reading_grouping_from_file_bool, use_csv_registration_file, column_ids, competitor_information_wca, competitors)

        registration_list = sorted(sorted(all_data, key= lambda x: x[1]), key=lambda x: x[1].split()[-1])
        
        if event_counter != event_counter_wca:
            print('ERROR!! Number of events from WCA Website does not match number of events in registration data. Please use correct registration file. Abort script.')
            sys.exit()

    if wca_info:
        registration_list = registration_list_wca

### Parse registration file
if read_only_registration_file:
    use_csv_registration_file = False
    column_ids, event_list, event_counter, competitor_information, all_data, wca_ids = get_registration_from_file(file_name, new_creation, reading_grouping_from_file_bool, use_csv_registration_file, column_ids, event_counter, competitor_information_wca, competitors)

### Create schedule (if exists on WCA website)
if create_schedule and full_schedule:
    full_schedule = sorted(sorted(full_schedule, key=lambda x: x['event_name']), key=lambda x: x['startTime'])
    
    # Use schedule to determine the days each competitor registered for
    for schedule_event in full_schedule:
        events_per_day = get_events_per_day(schedule_event, events_per_day)

    registration_list = get_competitor_events_per_day(registration_list, column_ids, events_per_day)

    # Create schedule PDF
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
    create_registration_file(output_registration, registration_list, column_ids)

    print('Registration file successfully created.')
    print('')

    if create_only_registration_file:
        sys.exit()

### Create blank scoresheets if wanted
if blank_sheets:
    print('Creating blank sheets...')
    create_blank_sheets(competition_name, scrambler_signature, blank_sheets_round_name)

### Create scoresheets for consecutive rounds and exit script
if create_scoresheets_second_rounds_bool:
    print('Creating scoresheets for {} ...'.format(event_round_name))
    create_scoresheets_second_rounds(
            competition_name, competitor_information, \
            advancing_competitors_next_round, event_round_name, event_info, \
            event_2, next_round_name, scrambler_signature \
            )

### Create new string for grouping and add name + DOB
if registration_list:
    result_string = initiate_result_string(registration_list)
        
### Check for matching registration and grouping information
if create_only_nametags:
    if two_sided_nametags:
        result_string, event_ids = get_grouping_from_file(grouping_file_name, event_dict, event_ids, only_one_competitor, scoresheet_competitor_name)
        new_result_string, new_competitor_information = [], []
        if len(competitor_information) != len(result_string):
            print('')
            print('ERROR! Count of registrations in grouping file and WCA website does not match.')
            for registered_competitor in competitor_information:
                for competitor_grouping in result_string:
                    if ftfy.fix_text(registered_competitor['name']) == ftfy.fix_text(competitor_grouping[0]):
                        new_result_string.append(competitor_grouping)
                        new_competitor_information.append(registered_competitor)
                        break
    
        if len(new_competitor_information) <= len(competitor_information) and len(new_competitor_information) != 0:
            print('Using only information that were found on both platforms.')
            print('')
            competitor_information = new_competitor_information
            result_string = new_result_string

### Selection of necessary information from WCA database export. Information include:
# - rankings for all events at competition
# - competition count per competitor
# - single and average rankings for 3x3x3 for each competitior
if new_creation or create_only_nametags:
    if wca_ids and event_list:
        print('Get necessary results from WCA website, this may take a few seconds...')
        competitor_information, ranking_single, competition_count = get_competitor_results_from_wcif(event_list, wca_ids, competitor_information, create_only_nametags, wca_info)

# Run grouping and scrambling
if new_creation:
    print('')
    print('Running grouping and scrambling...')
    result_string, scrambler_list = run_grouping_and_scrambling(group_list, result_string, registration_list, column_ids, ranking_single, competition_count, event_ids, event_ids_wca, competitor_information, round_counter)

    # Add dummy columns for events with < 5 scramblers
    for scrambler_id in range(0, len(scrambler_list)):
        while len(scrambler_list[scrambler_id]) < 7:
            scrambler_list[scrambler_id].append('dummy name')

    scrambler_list_sorted_by_schedule = sort_scrambler_by_schedule(full_schedule, scrambler_list, round_counter)
    if scrambler_list_sorted_by_schedule:
        scrambler_list = scrambler_list_sorted_by_schedule
    print('Grouping and scrambling done.')

# Get scrambler list from file if needed for nametags
if reading_scrambling_list_from_file: 
    with open(scrambling_file_name, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        scrambler_list = list(reader)
    del scrambler_list[0:2]
    scrambler_list = update_scrambler_list(scrambler_list)
        
### Save all results to separate files
if new_creation or blank_sheets or create_only_nametags:
    print('')
    print('Create nametags...')
    output_scrambling = '{}/{}Scrambling.csv'.format(competition_name, competition_name_stripped)
    output_grouping = '{}/{}Grouping.csv'.format(competition_name, competition_name_stripped)
    
    # Nametag file
    sheet = create_nametag_file(
            competitor_information, competition_name, competition_name_stripped, \
            two_sided_nametags, create_only_nametags, result_string, \
            event_ids, scrambler_list, event_dict, \
            round_counter, group_list
            )
    print('')
    print('Create scrambling and grouping file...')

    # Grouping file
    create_grouping_file(output_grouping, event_ids, event_dict, result_string)
    
    # Scrambling file
    create_scrambling_file(output_scrambling, competition_name, scrambler_list)
    print('Scrambling and grouping successfully saved. Nametags compiled into PDF: {0:d} label(s) output on {1:d} page(s).'.format(sheet.label_count, sheet.page_count))
    print('')

# Scoresheet file
#EXCEPTION: no scoresheets created for 3x3x3 Fewest Moves
if new_creation or reading_grouping_from_file_bool:
    if reading_grouping_from_file_bool: 
        result_string, events_ids = get_grouping_from_file(
                grouping_file_name, event_dict, event_ids, \
                only_one_competitor, scoresheet_competitor_name
                )
    
    print('Creating scoresheets...')
    create_scoresheets(
            competition_name, competition_name_stripped, result_string, \
            event_ids, event_info, event_dict, \
            only_one_competitor, round_counter, competitor_information, \
            scoresheet_competitor_name, scrambler_signature
            )
    
    ### Throw error messages for entire script if errors were thrown
    if ErrorMessages.messages:
        print('')
        print('Notable errors while creating grouping and scrambling:')
        for errors in ErrorMessages.messages:
            print(ErrorMessages.messages[errors])
    else:
        print('')
        print('No errors while creating files.')

    print('Please see folder {} for files.'.format(competition_name))
    print('')
