# Competition-Preparation

## What
This script creats various things an organizer needs to have for a competition:
- competitor groupings
- scrambling list for all events and rounds (except FMC)
- nametags, option to write grouping and scrambling for each event on the back (two-sided nametags)
- registration file for check-in
- create PDF-schedule from WCA website information
- scoresheets for first rounds
- scoresheets for consecutive rounds
- blank scoresheets (with editable competition and round name)
    
### System information: 
This script was tested on Mac OS 10.13.4/10.14.1 with python 3.5.2 and 3.7.1
    
## Setup
Make sure to add all event information in the 'Manage events' tab for your competition on the WCA website. Optional: fill in your schedule on the WCA competition website as well (advantages: scrambler list sorted by schedule and extra schedule pdf).
    
**Additional files needed**
- Trebuchet.ttf ([TrueType font](https://www.fontpalace.com/font-download/Trebuchet+MS/))

This must be downloaded and added to the same folder.
    
Please be aware that you need a WCA database connection. The credentials must be added to `static/config.py`. Else the script won't run.
    
### System setup

- `pip install -r requirements.txt`
- `python3 competition_grouping_scrambling.py` or `python competition_grouping_scrambling.py`

For further details and support, please contact Linus Frész, linuf95@gmail.com
