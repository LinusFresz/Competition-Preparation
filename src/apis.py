### Multiple functions to log in on the WCA website and catch all necessary competition and competitor registration information

from modules import *

### Error handling for WCA website login errors
def error_handling_wcif(competition_name, competition_page):
    competition_name_stripped = competition_name.replace(' ', '')
    if 'Not logged in' in competition_page:
        print('ERROR!!')
        print('While logging into WCA website, either WCA ID or password was wrong. Aborted script, please retry.')
    elif 'Competition with id' in competition_page:
        print('ERROR!!')
        print('Competition with name {} not found on WCA website.'.format(competition_name))
    elif 'Not authorized to manage' in competition_page:
        print('ERROR!!')
        print('You are not authorized to manage this competition. Please only select your competitions.')
    elif "The page you were looking for doesn't exist." in competition_page:
        print('ERROR!!')
        print('Misstiped competition link, please enter correct link.')
    else:
        if not os.path.exists(competition_name_stripped):
            os.makedirs(competition_name_stripped)
        return None
    sys.exit()

### Functions for handling WCA website related operations
# Get file names for registration and grouping file if only scoresheets or nametags are created
def competition_information_fetch(wca_info, only_scoresheets, two_sided_nametags, new_creation, parser):
    file_name, grouping_file_name = '', ''
    if not wca_info:
        file_name = get_file_name('registration', parser.registration_file)
    if two_sided_nametags or only_scoresheets:
        grouping_file_name = get_file_name('grouping', parser.grouping_file)
    return (file_name, grouping_file_name)

# Get user input for wca login (mail-address, password and competition name)
# All try-except cases were implemented for simple development and will not change the normal user input
def wca_registration(new_creation, parser):
    print('')
    print('To get the competition information (such as events and schedule), please enter your WCA login credentials.')
    if not parser.use_access_token:
        while True:
            if parser.mail and "@" in parser.mail:
                wca_mail = parser.mail
            else:
                if parser.mail and "@" not in parser.mail:
                    print('')
                    print('Input for mail was wrong in parser options. Please enter correct mail address manually.')
                wca_mail = input('Your WCA mail address: ')
            # Validation if correct mail address was entered
            if '@' not in wca_mail:
                if wca_mail[:4].isdigit() and wca_mail[8:].isdigit():
                    print('Please enter your WCA account email address instead of WCA ID.')
                else:
                    print('Please enter valid email address.')
            else:
                break
        wca_password = getpass.getpass('Your WCA password: ')
    
    if new_creation:
        print('Getting upcoming competitions from WCA website...')
        if not parser.use_access_token:
            upcoming_competitions = sorted(json.loads(get_upcoming_wca_competitions(wca_password, wca_mail)), key=lambda x:x['start_date'])
        else:
            upcoming_competitions = sorted(json.loads(get_upcoming_wca_competitions(parser.access_token)), key=lambda x:x['start_date'])
        counter = 1
        if upcoming_competitions:
            print('Please select competition (by number) or enter competition name:')
            for competition in upcoming_competitions:
                print('{}. {}'.format(counter, competition['name']))
                counter += 1
        not_valid_competition_name = True
        while not_valid_competition_name:
            if parser.competition:
                competition_name = parser.competition
            else:
                competition_name = input('Competition name or ID: ')
            if competition_name.isdigit():
                if int(competition_name) < len(upcoming_competitions):
                    competition_name = upcoming_competitions[int(competition_name)-1]['name'].replace('-', ' ')
                    not_valid_competition_name = False
                else:
                    print('Wrong input, please select number or enter competition name/ID.')
            else:
                try:
                    get_wca_competition(competition_name)['name']
                    not_valid_competition_name = False
                except KeyError:
                    print('Competition {} not found on WCA website, please enter valid competition name.'.format(competition_name))
                    parser.competition = ''

        create_competition_folder(competition_name)
        competition_name_stripped = competition_name.replace(' ', '')
        if not parser.use_access_token:
            return (wca_password, wca_mail, competition_name, competition_name_stripped)
        else:
            return (competition_name, competition_name_stripped)
    return (wca_password, wca_mail)

### WCA API
# Use given input from function wca_registration to access competition WCIF
# Further information can be found here:
# https://github.com/thewca/worldcubeassociation.org/wiki/OAuth-documentation-notes
def get_wca_info(competition_name, competition_name_stripped, *args):
    print('Fetching information from WCA competition website...')
    url = 'https://www.worldcubeassociation.org/api/v0/competitions/{}/wcif'.format(competition_name_stripped)
    
    if len(args) == 2:
        wca_password = args[0]
        wca_mail = args[1]
    
        competition_wcif_info = wca_api(url, wca_mail, wca_password)
    else:
        access_token = args[0]
        competition_wcif_info = wca_api(url, access_token)
        
    # Error handling for wrong WCA website information and file-save if successful information fetch
    error_handling_wcif(competition_name, competition_wcif_info.text)
    
    return competition_wcif_info.text

# Simple request to get information about one competitor
def get_wca_competitor(wca_id):
    url = 'https://www.worldcubeassociation.org/api/v0/persons/{}'.format(wca_id)
    competitor_info = ''
    api_info = requests.get(url)
    try:
        competitor_info = json.loads(api_info.text)
    except KeyError:
        pass
    except json.decoder.JSONDecodeError:
        pass
    return competitor_info

# The WCA API provides the option to get up to 100 WCA at the same time. This improves performance a lot.
def get_wca_competitors(wca_ids):
    competitors_info = []
    
    # Split WCA IDs up into batches of 100 each time and request information from WCA API
    for competitors in range(0,math.ceil(len(wca_ids)/100)):
        wca_ids_partial = wca_ids[competitors*100:(competitors+1)*100]
        url = 'https://www.worldcubeassociation.org/api/v0/persons?wca_ids={}&per_page=150'.format(','.join(wca_ids_partial))
    
        api_info = requests.get(url)

        try:
            competitors_info.extend(json.loads(api_info.text))
        except KeyError:
            print('ERROR! Something went wrong while communication with the WCA website, please restart script.')
            sys.exit()
        except json.decoder.JSONDecodeError:
            print('ERROR! Something went wrong while communication with the WCA website, please restart script.')
            sys.exit()

    return competitors_info

# Simple request to get information about input competition name
def get_wca_competition(competition_name):
    url = 'https://www.worldcubeassociation.org/api/v0/competitions/{}'.format(competition_name.replace(' ', ''))

    competition_info = ''
    api_info = requests.get(url)
    try:
        competition_info = json.loads(api_info.text)
    except KeyError:
        return ''
    return competition_info

# Get upcoming competitions of user
def get_upcoming_wca_competitions(*args):
    start_date = str(datetime.datetime.today()).split()[0]
    url = 'https://www.worldcubeassociation.org/api/v0/competitions?managed_by_me=true&start={}'.format(start_date)
    
    if len(args) == 2:
        wca_password = args[0]
        wca_mail = args[1]
        competition_wcif_info = wca_api(url, wca_mail, wca_password)
    else:
        access_token = args[0]
        competition_wcif_info = wca_api(url, access_token)
    
    return competition_wcif_info.text

# Function to actually talk to WCA API and collect response information
def wca_api(request_url, *args):
    grant_url = 'https://www.worldcubeassociation.org/oauth/token'
    
    if len(args) == 2:
        wca_password = args[1]
        wca_mail = args[0]
        wca_headers = {'grant_type':'password', 'username':wca_mail, 'password':wca_password, 'scope':'public manage_competitions'}
        wca_request_token = requests.post(grant_url, data=wca_headers)
        try:
            wca_access_token = json.loads(wca_request_token.text)['access_token']
            wca_refresh_token = json.loads(wca_request_token.text)['refresh_token']
            with open('.secret', 'w') as secret:
                print(str(datetime.datetime.now()) + ' token:' + wca_access_token + ' refresh_token:' + wca_refresh_token, file=secret)
        except KeyError:
            print('ERROR!! Failed to get competition information.\n\n Given error message: {}\n Message:{}\n\nScript aborted.'.format(json.loads(wca_request_token.text)['error'],  json.loads(wca_request_token.text)['error_description']))
            sys.exit()
    else:
        wca_access_token = args[0]
    
    wca_authorization = 'Bearer ' + wca_access_token
    wca_headers2 = {'Authorization': wca_authorization}
    competition_wcif_info = requests.get(request_url, headers=wca_headers2)

    return competition_wcif_info
    
def wca_api_get_new_token(refresh_token):
    grant_url = 'https://www.worldcubeassociation.org/oauth/token'
    wca_headers = {'grant_type':'refresh_token', 'refresh_token':refresh_token, 'scope':'public manage_competitions'}
    wca_request_token = requests.post(grant_url, data=wca_headers)
    
    try:
        wca_access_token = json.loads(wca_request_token.text)['access_token']
        wca_refresh_token = json.loads(wca_request_token.text)['refresh_token']
        with open('.secret', 'w') as secret:
            print(str(datetime.datetime.now()) + ' token:' + wca_access_token + ' refresh_token:' + wca_refresh_token, file=secret)
    except KeyError:
        print('ERROR!! Failed to get competition information.\n\n Given error message: {}\n Message:{}\n\nScript aborted.'.format(json.loads(wca_request_token.text)['error'], json.loads(wca_request_token.text)['error_description']))

### Cubecomps API
# API to collect competitor information
# Mostly used to update registration id for all competitors
def get_competitor_information_from_cubecomps(cubecomps_id, competition_name):
    cubecomps_id = 'http://cubecomps.com/live.php?cid={}'.format(cubecomps_id)
    competitors_api = []
    try:
        cubecomps_id.split('?')[1].split('&')[0].split('=')[1]
    except IndexError:
        print('ERROR! Not a valid cubecomps link, script continues without cubecomps.com information.')
        return ([], False)

    comp_id = split_cubecomps_id(cubecomps_id, 1, 0, 1)
    cubecomps_api_url = 'https://m.cubecomps.com/api/v1/competitions/{}'.format(comp_id)
    cubecomps_api = requests.get(cubecomps_api_url).json()

    if cubecomps_api['name'].replace('-', ' ') != competition_name and cubecomps_api['name'].replace('-', '') != competition_name.replace(' ', '').replace('-', ' '):
        print('Cubecomps link does not match given competition name/ID. Script uses fallback to registration ids from WCA website!')
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
    
# Get all competitions from cubecomps
def get_cubecomps_competitions():
    url = 'https://m.cubecomps.com/api/v1/competitions'
    url_past = 'https://m.cubecomps.com/api/v1/competitions/past'
    current_competitions = requests.get(url).json()
    past_competitions = requests.get(url_past).json()
    compbined_competitions = current_competitions.copy()
    compbined_competitions.update(past_competitions)
    return compbined_competitions

# Find cubecomps competition
def get_cubecomps_competition(create_only_nametags, competition_name, competition_name_stripped):
    cubecomps_id = ''
    competitors_api = []
    use_cubecomps_ids = False
    
    if not create_only_nametags:    
        competitions_cubecomps = get_cubecomps_competitions()
        for dates in competitions_cubecomps: 
            for competition in competitions_cubecomps[dates]:
                if competition_name_stripped[:-4] == competition['name'].replace(' ', '').replace('-', '') and competition_name_stripped[-4:] in competition['date']:
                    cubecomps_id = competition['id'].replace('-', '')
                    break
    if cubecomps_id:
        competitors_api, use_cubecomps_ids = get_competitor_information_from_cubecomps(cubecomps_id, competition_name)
        if not competitors_api:
            use_cubecomps_ids = False
            print('')
            print('INFO! The competition was found on cubecomps. However, no registration information was uploaded. Uploading them before using this script ensures to have matching ids on all scoresheets and in cubecomps (which eases scoretaking a lot!).')
            print('')
        else:
            use_cubecomps_ids = True
            print('')
            print('INFO! Script found registration information on cubecomps.com. These registration ids will be used for scoresheets.')
            print('')
    else:
        print('')
        print('INFO! Competition was not found on cubecomps. Using this script and upload registration information afterwards might cause faulty registration ids on scoresheets. Use on own risk.')
        print('')
    return (competitors_api, cubecomps_id, use_cubecomps_ids) 

# Return if certain information should be used or not (by using y/n choice)
def get_information(information_string):
    print(information_string)

    while True:
        input_information = input('')
        if input_information.upper() in ('N', 'Y'):
            break
        else:
            print('Wrong input, please enter \'y\' or \'n\'.')
            print('')

    if input_information.upper() == 'Y':
        return True
    else:
        return False

# Get registration/grouping/scrambling file if it is in .csv. or .txt format
def get_file_name(id, file_name_parser):
    while True:
        if file_name_parser:
            file_name = file_name_parser
        else:
            file_name = input('Enter {}-file name: '.format(id))
        file_name = file_name.replace('.csv', '').replace('.txt', '')
        file_name_csv = '{}.csv'.format(file_name)
        file_name_txt = '{}.txt'.format(file_name)
        if not os.path.isfile(file_name_csv) and not os.path.isfile(file_name_txt):
            print('File {} or {} not found. Please enter valid file name.'.format(file_name_txt, file_name_csv))
            if file_name_parser:
                print('False input in parser. Please enter file name manually.')
                file_name_parser = ''
        else:
            break
    if os.path.isfile(file_name_txt):
        return file_name_txt
    else:
        return file_name_csv

def create_competition_folder(competition_name):
    competition_name_stripped = competition_name.replace(' ', '')
    if not os.path.exists(competition_name_stripped):
        os.makedirs(competition_name_stripped)
