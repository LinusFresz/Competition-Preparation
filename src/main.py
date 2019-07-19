'''
    Please read the README.md to get further information.
'''

### Module import
from modules import *
import helpers.helpers as helper
import apis
import information_analysis as analysis
import grouping_scrambling_functions as grouping_scrambling
import pdf_file_generation as pdf_files

### Parser
# Parser arguments that can be added during script start
parser = argparse.ArgumentParser(description='Give input to script to skip steps during run time')
parser.add_argument('-m', '--mail', help='WCA account mail address')
parser.add_argument('-o', '--option', help='Input any of the given options of script')
parser.add_argument('-wreg', '--wca_registration', action='store_true', help='Did competition use WCA registration?')
parser.add_argument('-nwreg', '--no_wca_registration', action='store_false', help='Did competition NOT use WCA registration?')
parser.add_argument('-c', '--competition', help='Competition name')
parser.add_argument('-t', '--two_sided', action='store_true', help='Specify, if back of nametags should be created (with grouping and scrambling information)')
parser.add_argument('-nt', '--no_two_sided', action='store_false', help='Specify, if back of nametags should NOT be created')
parser.add_argument('-ssig', '--scrambler_signature', action='store_true', help='Specify, if scrambler signature field should be put on scoresheets')
parser.add_argument('-nssig', '--no_scrambler_signature', action='store_false', help='Specify, if scrambler signature field should NOT be put on scoresheets')
parser.add_argument('-r', '--registration_file', help='Name of registration file if WCA registration was not used')
parser.add_argument('-g', '--grouping_file', help='Name of grouping file. For options 5, 7 and 8.')
parser.add_argument('-s', '--scrambling_file', help='Name of scrambling file. For option 5.')
parser.add_argument('-cu', '--cubecomps', help='Cubecomps link to create scoresheets of consecutive rounds.')

parser_args = parser.parse_args()

# catch input errors
if parser_args.two_sided and not parser_args.no_two_sided:
    print('Creating and not creating back of nametags was selected. Setting default to false.')
    parser_args.two_sided = False
    
if parser_args.scrambler_signature and not parser_args.no_scrambler_signature:
    print('Putting scrambler signature fields on scoresheets was selected for true AND false. Setting default to true.')
    parser_args.no_scrambler_signature = True
    
if parser_args.wca_registration and not parser_args.no_wca_registration:
    print('Use of WCA registration was selected as true AND false. Resetting values.')
    parser_args.wca_registration = None
    parser_args.no_wca_registration = None

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
    if parser_args.option and int(parser_args.option) in range(1,9):
        program_type = parser_args.option
    else:
        if parser_args.option:
            print('Input for script options was wrong in parser, please select correct option manually.')
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

    print('Wrong input, please enter one of the available options.\n')


### Evaluation of script selection and initialization
# Get necessary information for new competition
if new_creation or create_only_nametags:
    if parser_args.wca_registration or not parser_args.no_wca_registration:
        wca_info = parser_args.wca_registration
    else:
        wca_info = apis.get_information('Used WCA registration for this competition? (y/n) ')
    if wca_info:
        print('Using WCA registration information.')
    wca_password, wca_mail, competition_name, competition_name_stripped = apis.wca_registration(True, parser_args)
    if not create_only_registration_file:
        if parser_args.two_sided or not parser_args.no_two_sided:
            two_sided_nametags = parser_args.two_sided
        else:
            two_sided_nametags = apis.get_information('Create two-sided nametags? (grouping (and scrambling) information on the back) (y/n)')
        if two_sided_nametags:
            print('Using WCA registration and event information for competition {}.'.format(competition_name))
            
        competitors_api, cubecomps_id, use_cubecomps_ids = apis.get_cubecomps_competition(create_only_nametags, competition_name, competition_name_stripped)
            
        if not create_only_nametags:
            if parser_args.scrambler_signature or not parser_args.no_scrambler_signature:
                scrambler_signature = parser_args.scrambler_signature
            else:
                scrambler_signature = apis.get_information('Add scrambler signature field to scorecards? (y/n)')

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
                print('Wrong input, please enter \'y\' or \'n\'.')
                print('')

        if nametag_scrambling.upper() == 'Y':
            reading_scrambling_list_from_file = True
            scrambling_file_name = apis.get_file_name('scrambling', parser_args.scrambling_file)

    file_name, grouping_file_name = apis.competition_information_fetch(wca_info, False, create_only_nametags and two_sided_nametags, new_creation, parser_args)

    if create_only_nametags and not two_sided_nametags and not wca_info:
        pass
    else:
        competition_wcif_file = apis.get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped)

    print('Saved registration information from WCA website, extracting data now and collect relevant information...')

# Create blank scoresheets
elif blank_sheets:
    if parser_args.scrambler_signature or not parser_args.no_scrambler_signature:
        scrambler_signature = parser_args.scrambler_signature
    else:
        scrambler_signature = apis.get_information('Add scrambler signature field to scorecards? (y/n)')
    competition_name = input('Competition name or ID: (leave empty if not wanted) ')
    blank_sheets_round_name = input('Round name: (leave empty if not needed) ')

# Select grouping file if only nametags should be generated
elif reading_grouping_from_file_bool:
    if parser_args.wca_registration or not parser_args.no_wca_registration:
        wca_info = parser_args.wca_registration
    else:
        wca_info = apis.get_information('Used WCA registration for this competition? (y/n) ')
    if wca_info:
        print('Using WCA website information.')
    wca_password, wca_mail, competition_name, competition_name_stripped = apis.wca_registration(bool, parser_args)
    if parser_args.scrambler_signature or not parser_args.no_scrambler_signature:
        scrambler_signature = parser_args.scrambler_signature
    else:
        scrambler_signature = apis.get_information('Add scrambler signature field to scorecards? (y/n)')
    if only_one_competitor:
        scoresheet_competitor_name = input('Competitor name or WCA ID: ')
        try:
            scoresheet_competitor_api = apis.get_wca_competitor(scoresheet_competitor_name)
            if scoresheet_competitor_api:
                scoresheet_competitor_name = scoresheet_competitor_api['person']['name']
        except KeyError:
            pass
    file_name, grouping_file_name = apis.competition_information_fetch(wca_info, True, False, new_creation, parser_args)
    competition_wcif_file = apis.get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped)
    
    competitors_api, cubecomps_id, use_cubecomps_ids = apis.get_cubecomps_competition(create_only_nametags, competition_name, competition_name_stripped)

# Create schedule from wca website information
elif create_only_schedule:
    if parser_args.wca_registration or not parser_args.no_wca_registration:
        wca_info = parser_args.wca_registration
    else:
        wca_info = apis.get_information('Used WCA registration for this competition? (y/n) ')
    if wca_info:
        print('Using WCA website information.')

    wca_password, wca_mail, competition_name, competition_name_stripped = apis.wca_registration(True, parser_args)
    two_sided_nametags = False
    
    file_name, grouping_file_name = apis.competition_information_fetch(wca_info, False, two_sided_nametags, new_creation, parser_args)
    competition_wcif_file = apis.get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped)

# Create scoresheets for seconds rounds by using cubecomps.com information
elif create_scoresheets_second_rounds_bool:
    use_cubecomps_ids = True
    if parser_args.cubecomps:
        cubecomps_id = parser_args.cubecomps
    else:
        cubecomps_id = input('Link to previous round: ')
    cubecomps_api, competitors, event_round_name, advancing_competitors_next_round, competition_name, competition_name_stripped = apis.get_round_information_from_cubecomps(cubecomps_id)
    
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

    wca_password, wca_mail = apis.wca_registration(new_creation, parser_args)
    if parser_args.wca_registration or not parser_args.no_wca_registration:
        wca_info = parser_args.wca_registration
    else:
        wca_info = apis.get_information('Used WCA registration for this competition? (y/n) ')
    if wca_info:
        print('Using WCA website information.')
    if parser_args.scrambler_signature or not parser_args.no_scrambler_signature:
        scrambler_signature = parser_args.scrambler_signature
    else:
        scrambler_signature = apis.get_information('Add scrambler signature field to scorecards? (y/n)')
    file_name, grouping_file_name = apis.competition_information_fetch(wca_info, False, False, new_creation, parser_args)

    competition_wcif_file = apis.get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped)

### Get all information from wca competition (using WCIF) and collection information from WCA database export
if get_registration_information:
    # Extract data from WCIF file
    wca_json = json.loads(competition_wcif_file)
    
    # Registration
    competitor_information_wca = analysis.get_registrations_from_wcif(
            wca_json, create_scoresheets_second_rounds_bool, \
            use_cubecomps_ids, competitors, competitors_api, \
            only_one_competitor, scoresheet_competitor_name \
            )
    
    # Events
    event_ids_wca, group_list, event_info, event_counter_wca, minimal_scramble_set_count, round_counter, event_list_wca = analysis.get_events_from_wcif(wca_json, event_dict)

    # Schedule
    full_schedule, competition_days, competition_start_day, timezone_utc_offset, events_per_day = analysis.get_schedule_from_wcif(wca_json)

    # Evaluate collected information
    if wca_info:
        competitor_information = competitor_information_wca
        
        wca_ids, registration_list_wca = analysis.prepare_registration_for_competitors(competitor_information, event_list_wca, len(event_list_wca))
        
        if not registration_list_wca:
            print('')
            print('ERROR!! WCA registration not used for this competition. Please select registration file for import. Script aborted.')
            sys.exit()
        registration_list_wca = sorted(sorted(registration_list_wca, key=lambda x: x[1]), key=lambda x: x[1].split()[-1])
    
        analysis.column_ids, event_list = grouping_scrambling.update_column_ids(event_list_wca, analysis.column_ids)
    if group_list:
        print('WCA information sucessfully imported.')
    else:
        print('An error occured while importing the rounds and groups information from the WCIF file, script aborted.')
        print('Please make sure to enter all necessary information in the "Manage events" tab on the WCA competition page.')
        sys.exit()
    if minimal_scramble_set_count == 1:
        continue_script = apis.get_information('It looks like all your events only have one set of scrambles. Do you still want to continue running this script? (y/n)')
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
        if not competitors_api:
            competitors_api = competitors
        analysis.column_ids, event_list, event_counter, competitor_information, all_data, wca_ids = analysis.get_registration_from_file(wca_json, file_name, new_creation, reading_grouping_from_file_bool, use_csv_registration_file, analysis.column_ids, competitor_information_wca, competitors, use_cubecomps_ids, competitors_api)

        registration_list = sorted(sorted(all_data, key= lambda x: x[1]), key=lambda x: x[1].split()[-1])
        
        if event_counter != event_counter_wca:
            print('ERROR!! Number of events from WCA Website does not match number of events in registration data. Please use correct registration file. Abort script.')
            sys.exit()

    if wca_info:
        registration_list = registration_list_wca

### Parse registration file
if read_only_registration_file:
    use_csv_registration_file = False
    analysis.column_ids, event_list, event_counter, competitor_information, all_data, wca_ids = analysis.get_registration_from_file(wca_json, file_name, new_creation, reading_grouping_from_file_bool, use_csv_registration_file, analysis.column_ids, event_counter, competitor_information_wca, competitors, use_cubecomps_ids, competitors_api)

### Create schedule (if exists on WCA website)
if create_schedule and full_schedule:
    full_schedule = sorted(sorted(full_schedule, key=lambda x: x['event_name']), key=lambda x: x['startTime'])
    
    # Use schedule to determine the days each competitor registered for
    for schedule_event in full_schedule:
        events_per_day = analysis.get_events_per_day(schedule_event, events_per_day)

    registration_list = analysis.get_competitor_events_per_day(registration_list, analysis.column_ids, events_per_day)

    # Create schedule PDF
    if create_schedule:
        pdf_files.create_schedule_file(
                competition_name, competition_name_stripped, full_schedule,
                event_info, competition_days, competition_start_day,
                timezone_utc_offset, analysis.formats, analysis.format_names,
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
    output_registration = '{}/{}Registration.csv'.format(competition_name_stripped, competition_name_stripped)
    pdf_files.create_registration_file(output_registration, registration_list, analysis.column_ids)

    print('Registration file successfully created.')
    print('')

    if create_only_registration_file:
        sys.exit()

### Create blank scoresheets if wanted
if blank_sheets:
    print('Creating blank sheets...')
    pdf_files.create_blank_sheets(competition_name, scrambler_signature, blank_sheets_round_name)

### Create scoresheets for consecutive rounds and exit script
if create_scoresheets_second_rounds_bool:
    print('Creating scoresheets for {} ...'.format(event_round_name))
    pdf_files.create_scoresheets_second_rounds(
            competition_name, competitor_information, \
            advancing_competitors_next_round, event_round_name, event_info, \
            event_2, next_round_name, scrambler_signature \
            )

### Create new string for grouping and add name + DOB
if registration_list:
    result_string = helper.initiate_result_string(registration_list)
        
### Check for matching registration and grouping information
if create_only_nametags:
    if two_sided_nametags:
        result_string, event_ids = analysis.get_grouping_from_file(grouping_file_name, event_dict, event_ids, only_one_competitor, scoresheet_competitor_name)
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
        competitor_information, ranking_single, competition_count = grouping_scrambling.get_competitor_results_from_wcif(event_list, wca_ids, competitor_information, create_only_nametags, wca_info)

# Run grouping and scrambling
if new_creation:
    print('')
    print('Running grouping and scrambling...')
    result_string, scrambler_list = grouping_scrambling.run_grouping_and_scrambling(group_list, result_string, registration_list, analysis.column_ids, ranking_single, competition_count, event_ids, event_ids_wca, competitor_information, round_counter)

    # Add dummy columns for events with < 5 scramblers
    for scrambler_id in range(0, len(scrambler_list)):
        while len(scrambler_list[scrambler_id]) < 7:
            scrambler_list[scrambler_id].append('dummy name')

    scrambler_list_sorted_by_schedule = grouping_scrambling.sort_scrambler_by_schedule(full_schedule, scrambler_list, round_counter)
    if scrambler_list_sorted_by_schedule:
        scrambler_list = scrambler_list_sorted_by_schedule
    print('Grouping and scrambling done.')

# Get scrambler list from file if needed for nametags
if reading_scrambling_list_from_file: 
    with open(scrambling_file_name, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        scrambler_list = list(reader)
    del scrambler_list[0:2]
    scrambler_list = helper.update_scrambler_list(scrambler_list)
        
### Save all results to separate files
if new_creation or blank_sheets or create_only_nametags:
    print('')
    print('Create nametags...')
    output_scrambling = '{}/{}Scrambling.csv'.format(competition_name_stripped, competition_name_stripped)
    output_grouping = '{}/{}Grouping.csv'.format(competition_name_stripped, competition_name_stripped)
    
    # Nametag file
    sheet = pdf_files.create_nametag_file(
            competitor_information, competition_name, competition_name_stripped, \
            two_sided_nametags, create_only_nametags, result_string, \
            event_ids, scrambler_list, event_dict, \
            round_counter, group_list
            )
    print('')
    print('Create scrambling and grouping file...')

    # Grouping file
    pdf_files.create_grouping_file(output_grouping, event_ids, event_dict, result_string)
    
    # Scrambling file
    pdf_files.create_scrambling_file(output_scrambling, competition_name, scrambler_list)
    print('Scrambling and grouping successfully saved. Nametags compiled into PDF: {0:d} label(s) output on {1:d} page(s).'.format(sheet.label_count, sheet.page_count))
    print('')

# Scoresheet file
#EXCEPTION: no scoresheets created for 3x3x3 Fewest Moves
if new_creation or reading_grouping_from_file_bool:
    if reading_grouping_from_file_bool: 
        result_string, events_ids = analysis.get_grouping_from_file(
                grouping_file_name, event_dict, event_ids, \
                only_one_competitor, scoresheet_competitor_name
                )
    
    print('Creating scoresheets...')
    pdf_files.create_scoresheets(
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

    print('Please see folder {} for files.'.format(competition_name_stripped))
    print('')
