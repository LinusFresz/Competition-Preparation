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
import pycountry
import tqdm

from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.graphics import shapes
from reportlab.lib import colors

# Self made modules
from error_messages import ErrorMessages

# Catch user being in src/ folder instead of main directory
try:
    os.chdir('src/')
    os.chdir('..')
except FileNotFoundError:
    os.chdir('..')

### Initialize font
if not os.path.isfile('src/data/Trebuchet.ttf'):
    print("ERROR!! File 'Trebuchet.ttf' does not exist. Please download from \n",
           "https://www.fontpalace.com/font-download/Trebuchet+MS/\n and add to",
           "{}/.".format(os.path.dirname(os.path.abspath(__file__))))
    sys.exit()
registerFont(TTFont('Arial', 'src/data/Trebuchet.ttf'))
