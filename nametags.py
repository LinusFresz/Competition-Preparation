#!/usr/bin/python

'''
Create nametags for all competitors at the competition. For this we're adding 3x3x3 personal bests, competitor roles (organizer and/or delegate) and number of competitions    
'''

import labels
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.graphics import shapes
from reportlab.lib import colors
from information_analysis import *

# select font depending on registration-file format (to avoid errors with special characters) 
if wca_info:
    registerFont(TTFont('Arial', 'Trebuchet.ttf'))
else:
    if os.path.exists('STIXGeneral.ttf'):
        registerFont(TTFont('Arial', 'STIXGeneral.ttf'))
    else:
        print('TrueType font Trebuchet (Trebuchet.ttf) not found, used Arial instead.')
        registerFont(TTFont('Arial', 'Arial.ttf'))

# format information for nametags: usual DIN-A4 layout with 2 rows of 4 nametags each with a size of 85x55mm
specs = labels.Specification(210, 297, 2, 4, 85, 55)

# Actual creation of each nametag
def write_name(label, width, height, name):
    # Write the title.
    label.add(shapes.String(width/2.0, height-20, competition_name, textAnchor='middle', fontSize=15, fontName='Arial'))
                            
    # Measure the width of the name and (possible) competitor roles and shrink the font size until it fits.
    font_size = 30
    text_width = width - 10
    name_width = stringWidth(name['name'], 'Arial', font_size)
    
    while name_width > text_width:
        font_size *= 0.95
        name_width = stringWidth(name['name'], 'Arial', font_size)
    
    role_font_size = 22
    role_width = stringWidth(name['role'], 'Arial', role_font_size)
    if name['role']:
        name_height = height - 53
        while role_width > text_width:
            role_font_size *= 0.95
            role_width = stringWidth(name['role'], 'Arial', role_font_size)
    else:
        name_height = height - 70

    # Write name and role on nametag
    s = shapes.String(width/2.0, name_height, name['name'], fontName='Arial', textAnchor='middle')
    s.fontSize = font_size
    s.fillColor = colors.black
    label.add(s)

    r = shapes.String(width/2.0, height-85, name['role'], fontName='Arial', textAnchor='middle')
    r.fontSize = role_font_size
    r.fillColor = colors.red
    label.add(r)

    # Country
    label.add(shapes.String(width/2.0, height-110, name['country'], textAnchor='middle', fontSize=15, fontName='Arial'))

    # Addition of competition count. String used depending on amount of competitions
    competitions = ''
    if name['comp_count'] != 0:
        count = name['comp_count'] + 1
        if count % 10 == 1 and count != 11:
            competitions = str(count) + 'st Competition'
        elif count % 10 == 2 and count != 12:
            competitions = str(count) + 'nd Competition'
        elif count % 10 == 3 and count  != 13:
            competitions = str(count) + 'rd Competition'
        else:
            competitions = str(count) + 'th Competition'
    label.add(shapes.String(width/2.0, height-130, competitions, textAnchor='middle', fontSize = 12, fontName='Arial'))

    # Ranking
    ranking = ''
    if name['single'] != '0.00':
        ranking = '3x3x3: ' + str(name['single']) + ' (' + str(name['average']) + ')'
    label.add(shapes.String(width/2.0, height-145, ranking, textAnchor='middle', fontSize=12, fontName='Arial'))
