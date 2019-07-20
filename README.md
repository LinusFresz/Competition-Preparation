# Competition-Preparation

## Content
This script creats various things an organizer needs to have for a competition:
- competitor groupings (specified by the amount of groups set on the WCA competition website)
- scrambling list for all events and rounds (except FMC)
- nametags, option to write grouping and scrambling for each event on the back (two-sided nametags)
- registration file for check-in
- create PDF-schedule from WCA website information
- scoresheets for first rounds
- scoresheets for consecutive rounds (using results from cubecomps)
- blank scoresheets (with editable competition and round name)
    
### System information: 
This script was tested on Mac OS 10.13.4/10.14.1 with python 3.7.1
    
## Setup
Make sure to add all event information in the 'Manage events' tab for your competition on the WCA website. Optional: fill in your schedule on the WCA competition website as well (advantages: scrambler list sorted by schedule and extra schedule pdf).
         
### System setup

- `pip install -r requirements.txt`
- `python3 src/main.py` or `python src/main.py`

For further details and support, please contact Linus Frész, linuf95@gmail.com

## Argparse support
### Optional arguments
*  -m <mail address>, --mail <mail address>  
                        WCA account mail address which is used for login
*  -o <option>, --option <option>
                        Input any of the given options of script
*  -wreg, --wca_registration
                        Boolean. Did competition use WCA registration?
*  -nwreg, --no_wca_registration
                        Boolean. Did competition NOT use WCA registration?
*  -c <competition name/ID>, --competition <competition name/ID>
                        Competition name
*  -t, --two_sided       
                        Boolean. Specify, if back of nametags should be created (with grouping and scrambling information)
*  -nt, --no_two_sided   
                        Boolean. Specify, if back of nametags should NOT be created
*  -ssig, --scrambler_signature
                        Boolean. Specify, if scrambler signature field should be put on scoresheets
*  -nssig, --no_scrambler_signature
                        Boolean. Specify, if scrambler signature field should NOT be put on scoresheets
*  -r <registration file name>, --registration_file <registration file name>
                        Name of registration file if WCA registration was not used
*  -g <grouping file name>, --grouping_file <grouping file name>
                        Name of grouping file. For options 5, 7 and 8.
*  -s <scrambling file name>, --scrambling_file <scrambling file name>
                        Name of scrambling file. For option 5.
*  -cu <cubecomps url>, --cubecomps <cubecomps url>
                        Cubecomps link to create scoresheets of consecutive rounds.
