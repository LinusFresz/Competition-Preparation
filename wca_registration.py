### Multiple functions to log in on the WCA website and catch all necessary competition and competitor registration information

from modules import *

### Error handling for WCA website login errors
def error_handling_wcif(competition_name, competition_page):
    if 'Not logged in' in competition_page:
        print('ERROR!!')
        print('While logging into WCA website, either WCA ID or password was wrong. Aborted script, please retry.')
        sys.exit()
    elif 'Competition with id' in competition_page:
        print('ERROR!!')
        print('Competition with name {} not found on WCA website.'.format(competition_name))
        sys.exit()
    elif 'Not authorized to manage' in competition_page:
        print('ERROR!!')
        print('You are not authorized to manage this competition. Please only select your competitions.')
        sys.exit()
    elif "The page you were looking for doesn't exist." in competition_page:
        print('ERROR!!')
        print('Misstiped competition link, please enter correct link.')
        sys.exit()
    else:
        if not os.path.exists(competition_name):
            os.makedirs(competition_name)

### Functions for handling WCA website related operations
# Get file names for registration and grouping file if only scoresheets or nametags are created
def competition_information_fetch(wca_info, only_scoresheets, two_sided_nametags, new_creation):
    file_name, grouping_file_name = '', ''
    if not wca_info:
        file_name = get_file_name('registration')
    if two_sided_nametags or only_scoresheets:
        grouping_file_name = get_file_name('grouping')
    return (file_name, grouping_file_name)

# Get user input for wca login (mail-address, password and competition name)
# All try-except cases were implemented for simple development and will not change the normal user input
def wca_registration(new_creation):
    print('')
    print('To get the competition information (such as events and schedule), please enter your WCA login credentials.')
    while True:
        try:
            wca_mail = credentials.mail_address
        except:
            wca_mail = input('Your WCA mail address: ')
        # Validation if correct mail address was entered
        if '@' not in wca_mail:
            if wca_mail[:4].isdigit() and wca_mail[8:].isdigit():
                print('Please enter your WCA account email address instead of WCA ID.')
            else:
                print('Please enter valid email address.')
        else:
            break
    try:
        wca_password = credentials.password
    except:
        wca_password = getpass.getpass('Your WCA password: ')
    
    if new_creation:
        try:
            competition_name = credentials.competition_name_input
        except:
            competition_name = input('Competition name: ')
        create_competition_folder(competition_name)
        competition_name_stripped = competition_name.replace(' ', '')
        return (wca_password, wca_mail, competition_name, competition_name_stripped)
    return (wca_password, wca_mail)

### WCA API
# Use given input from function wca_registration to access competition WCIF
# Further information can be found here:
# https://github.com/thewca/worldcubeassociation.org/wiki/OAuth-documentation-notes
def get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped):
    print('Fetching information from WCA competition website...')
    url1 = 'https://www.worldcubeassociation.org/oauth/token'
    url2 = 'https://www.worldcubeassociation.org/api/v0/competitions/' + competition_name_stripped + '/wcif'
    
    wca_headers = {'grant_type':'password', 'username':wca_mail, 'password':wca_password, 'scope':'public manage_competitions'}
    wca_request_token = requests.post(url1, data=wca_headers)
    try:
        wca_access_token = json.loads(wca_request_token.text)['access_token']
    except KeyError:
        print('ERROR!! Failed to get competition information.\n\n Given error message: {}\n Message:{}\n\nScript aborted.'.format(json.loads(wca_request_token.text)['error'], json.loads(wca_request_token.text)['error_description']))
        sys.exit()
    wca_authorization = 'Bearer ' + wca_access_token
    wca_headers2 = {'Authorization': wca_authorization}
    competition_wcif_info = requests.get(url2, headers=wca_headers2)

    # Error handling for wrong WCA website information and file-save if successful information fetch
    error_handling_wcif(competition_name, competition_wcif_info.text)
    
    return competition_wcif_info.text
    
def get_wca_competitor(wca_id):
    url = 'https://www.worldcubeassociation.org/api/v0/persons/' + wca_id
    competitor_info = requests.get(url)    
    try:
        competitor_info = json.loads(competitor_info.text)
    except KeyError:
        print('Competitor ' + wca_id + 'not found.')
    return competitor_info

### Cubecomps API
# API to collect competitor information
# Mostly used to update registration id for all competitors
def get_competitor_information_from_cubecomps(cubecomps_id, competition_name):
    competitors_api = []
    try:
        cubecomps_id.split('?')[1].split('&')[0].split('=')[1]
    except IndexError:
        print('ERROR! Not a valid cubecomps link, script continues without cubecomps.com information.')
        return ([], False)

    comp_id = split_cubecomps_id(cubecomps_id, 1, 0, 1)
    cubecomps_api_url = 'https://m.cubecomps.com/api/v1/competitions/{}'.format(comp_id)
    cubecomps_api = requests.get(cubecomps_api_url).json()
            
    if cubecomps_api['name'] != competition_name and cubecomps_api['name'] != competition_name.replace(' ', ''):
        print('Cubecomps link does not match given competition name. Script uses fallback to registration ids from WCA website!')
        use_cubecomps_ids = False
    else:
        for competitor in cubecomps_api['competitors']:
            competitors_api.append({'name': competitor['name'], 'competitor_id': int(competitor['id'])})
        use_cubecomps_ids = True
    return (competitors_api, use_cubecomps_ids)

# API to collect information for one round to determine next rounds' competitors
def get_round_information_from_cubecomps(cubecomps_id):
    advancing_competitors_next_round = 0
    competitors_api = []
    try:
        print('Get round information from cubecomps.com...')
        print('')
        comp_id = split_cubecomps_id(cubecomps_id, 1, 0, 1)
        event_id = split_cubecomps_id(cubecomps_id, 1, 1, 1)
        round_id = split_cubecomps_id(cubecomps_id, 1, 2, 1)
    except IndexError:
        print('ERROR! Not a valid cubecomps link, script aborted.')
        sys.exit()
    
    cubecomps_api_url = 'https://m.cubecomps.com/api/v1/competitions/{}/events/{}/rounds/{}'.format(comp_id, event_id, round_id)
    cubecomps_api = requests.get(cubecomps_api_url).json()
    competition_name = cubecomps_api['competition_name']
    competition_name_stripped = competition_name.replace(' ', '')
    create_competition_folder(competition_name)
    event_round_name = '{} - {}'.format(cubecomps_api['event_name'], cubecomps_api['round_name']) 
    
    for competitor in cubecomps_api['results']:
        if competitor['top_position']:
            advancing_competitors_next_round += 1
            competitors_api.append({'name': competitor['name'], 'competitor_id': int(competitor['competitor_id']), 'ranking': int(competitor['position'])})
    return(cubecomps_api, competitors_api, event_round_name, advancing_competitors_next_round, competition_name, competition_name_stripped)

def split_cubecomps_id(cubecomps_id, ind1, ind2, ind3):
    return cubecomps_id.split('?')[ind1].split('&')[ind2].split('=')[ind3]

# Return if certain information should be used or not (by using y/n choice)
def get_information(information_string):
    print(information_string)
    while True:
        input_information = input('')
        if input_information.upper() in ('N', 'Y'):
            break
        else:
            print("Wrong input, please enter 'y' or 'n'.")
            print('')

    if input_information.upper() == 'Y':
        return True
    else:
        return False

# Get registration/grouping/scrambling file if it is in .csv. or .txt format
def get_file_name(id):
    while True:
        file_name = input('Enter {}-file name: '.format(id))
        file_name = file_name.replace('.csv', '').replace('.txt', '')
        file_name_csv = '{}.csv'.format(file_name)
        file_name_txt = '{}.txt'.format(file_name)
        if not os.path.isfile(file_name_csv) and not os.path.isfile(file_name_txt):
            print('File {} or {} not found. Please enter valid file name.'.format(file_name_txt, file_name_csv))
        else:
            break
    if os.path.isfile(file_name_txt):
        return file_name_txt
    else:
        return file_name_csv

def create_competition_folder(competition_name):
    if not os.path.exists(competition_name):
        os.makedirs(competition_name)
