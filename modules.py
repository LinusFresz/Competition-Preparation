### Collection of used modules
# Native modules
import os
import sys
import getpass
import random
import glob
import calendar
import json
import csv
import collections

# Added modules
import ftfy
import requests
import labels
import pytz
import datetime
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.graphics import shapes
from reportlab.lib import colors

# Self made modules
from db import WCA_Database
from error_messages import ErrorMessages

### Initialize font
if not os.path.isfile('Trebuchet.ttf'):
    print("ERROR!! File 'Trebuchet.ttf' does not exist. Please download from \n",
           "https://www.fontpalace.com/font-download/Trebuchet+MS/\n and add to",
           "{}/.".format(os.path.dirname(os.path.abspath(__file__))))
    sys.exit()
registerFont(TTFont('Arial', 'Trebuchet.ttf'))
