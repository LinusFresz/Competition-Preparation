'''
Multiple functions to log in on the WCA website and catch all necessary competition and competitor registration information
'''


from pdf_file_generation import *
#from chromedriver_data import *
from db import WCA_Database

### Error handling for WCA website login errors
def error_handling_wcif(competition_name, store_file, competition_page):
    if 'Not logged in' in competition_page:
        print('ERROR!!')
        print('While logging into WCA website, either WCA ID or password was wrong. Aborted script, please retry.')
        sys.exit()
    elif 'Competition with id' in competition_page:
        print('ERROR!!')
        print('Competition with name ' + competition_name + ' not found on WCA website.')
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

### 5 functions for login and saving necessary information from WCA website
def wca_registration_system():
    while True:
        registration_information_format = input('Use WCA website information? (y/n) ')
        print('')
        if registration_information_format.upper() in ('N', 'Y'):
            break
        else:   
            print("Wrong input, please enter 'y' or 'n'.")
            print('')

    if registration_information_format.upper() == 'Y':
        print('Using WCA website information.')
        return True
    else:
        return False

def get_file_name(id):
    while True:
        file_name = input('Enter ' + id + '-file name: ')
        file_name = file_name.replace('.csv', '').replace('.txt', '')
        file_name_csv = file_name + '.csv'
        file_name_txt = file_name + '.txt'
        if not os.path.isfile(file_name_csv) and not os.path.isfile(file_name_txt):
            print('File ' + file_name_txt + ' or ' + file_name_csv + ' not found. Please enter valid file name.')
        else:
            break
    if os.path.isfile(file_name_txt):
        return file_name_txt
    else:
        return file_name_csv
                
def competition_information_fetch(wca_info, only_scoresheets, two_sided_nametags, new_creation):
    file_name, grouping_file_name = '', ''
    if wca_info:
        if (two_sided_nametags and not new_creation) or only_scoresheets:
            grouping_file_name = get_file_name('grouping')
    
    if not wca_info:
        while True:
            file_name = input('Enter registration-file name: ')
            file_name = file_name.replace('.csv', '').replace('.txt', '')
            file_name_csv = file_name + '.csv'
            file_name_txt = file_name + '.txt'
            if not os.path.isfile(file_name_csv) and not os.path.isfile(file_name_txt):
                print('File ' + file_name_txt + ' or ' + file_name_csv + ' not found. Please enter valid file name.')
            else:
                break
        if os.path.isfile(file_name_txt):
            file_name = file_name_txt
        else:
            file_name = file_name_csv
        if only_scoresheets or (not new_creation and two_sided_nametags):
            grouping_file_name = get_file_name('grouping')
    return (file_name, grouping_file_name)

def wca_registration(new_creation):
    while True:
        wca_mail = input('Your WCA mail address: ')
        if '@' not in wca_mail:
            if wca_mail[:4].isdigit() and wca_mail[8:].isdigit():
                print('Please enter your WCA account email address instead of WCA ID.')
            else:
                print('Please enter valid email address.')
        else:
            break
    wca_password = getpass.getpass('Your WCA password: ')
    
    if new_creation:
        competition_name = input('Competition name: ')
        create_competition_folder(competition_name)
        competition_name_stripped = competition_name.replace(' ', '')
        wcif_file = competition_name + '/' + competition_name_stripped + '-grouping.txt'
        return (wca_password, wca_mail, competition_name, competition_name_stripped, wcif_file)
    return (wca_password, wca_mail)

def get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped, file):
    print('Fetching information from WCA competition website...')
    url1 = 'https://www.worldcubeassociation.org/oauth/token'
    url2 = 'https://www.worldcubeassociation.org/api/v0/competitions/' + competition_name_stripped + '/wcif'
    wcif_file = competition_name + '/wcif_information.txt'
    
    wca_headers = {'grant_type':'password', 'username':wca_mail, 'password':wca_password, 'scope':'public manage_competitions'}
    wca_request_token = requests.post(url1, data=wca_headers)
    wca_access_token = json.loads(wca_request_token.text)['access_token']

    wca_authorization = 'Bearer ' + wca_access_token
    wca_headers2 = {'Authorization': wca_authorization}
    competition_wcif_info = requests.get(url2, headers=wca_headers2)

    # error handling for wrong WCA website information and file-save if successful information fetch
    error_handling_wcif(competition_name, wcif_file, competition_wcif_info.text)
    
    return (wcif_file, competition_wcif_info.text)
    
def get_information(which_information):
    print(which_information)
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

def create_competition_folder(competition_name):
    if not os.path.exists(competition_name):
        os.makedirs(competition_name)
