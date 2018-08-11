#!/usr/bin/python

'''
Create nametags for all competitors at the competition. For this we're adding 3x3x3 personal bests, competitor roles (organizer and/or delegate) and number of competitions  
Additionally all groups (as competitor/scrambler) are added to the back of the nametags)  
'''

import os, glob, ftfy
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
import labels
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.graphics import shapes
from reportlab.lib import colors
from information_analysis import *


if reading_scrambling_list_from_file: 
    import csv
    with open('scrambling.csv', 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        scramblerlist = list(reader)

    for k in range(0, len(scramblerlist)):
        scramblerlist[k][1] = int(scramblerlist[k][1])

registerFont(TTFont('Arial', 'Trebuchet.ttf'))

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
    
def calculate_event_width(name, min, limit, result_string_nametags, event_ids):
    max_event_width = 0
    counter = 0
    if limit > len(name):
        limit = len(name)
    for person in result_string_nametags:
        if name[0] == person[0]:
            for group_event in range(3, len(name)):
                if counter == limit:
                    return max_event_width
                if name[group_event]:
                    for events in event_ids:
                        if event_ids[events] == group_event:
                            event_width = stringWidth(event_dict[events], 'Arial', 10)
                            if event_width > max_event_width and counter >= min:
                                max_event_width = event_width
                            counter += 1
    return max_event_width
    
def write_grouping(label, width, height, information):
    name = information[0]
    result_string_nametags = information[1]
    event_ids = information[2]
    scramblerlist = information[3]
    if not name[0]:
        return
    text_width = width - 12 - stringWidth('s = Scrambler', 'Arial', 9)
    width -= 235
    height -= 20
    name_and_id = ftfy.fix_text(name[0])
    if name[2]:
        name_and_id += ', ' + name[2]
    fontsize = 11
    name_width = stringWidth(name_and_id, 'Arial', fontsize)
    while name_width > text_width:
        fontsize *= 0.95
        name_width = stringWidth(name_and_id, 'Arial', fontsize)
    label.add(shapes.String(width, height, name_and_id, fontSize = fontsize, fontName='Arial'))
    
    indent = 20
    height -= 30
    top_line = height
    
    counter = 0
    max_event_width = 0
    max_event_width = calculate_event_width(name, 0, 9, result_string_nametags, event_ids)
    
    header = 'Event '
    header_width = stringWidth('Event ', 'Arial', 10) + stringWidth('Group', 'Arial', 10)
    while header_width < (indent + max_event_width - stringWidth('Group', 'Arial', 10)):
        header += ' '
        header_width = stringWidth(header, 'Arial', 10)
    header += 'Groups'
    header_height = height
    label.add(shapes.String(width, height+15, header, fontSize = 10, fontName='Arial'))
    does_scramble = False
    for group_event in range(3, len(name)):
        scrambling = []
        if name[group_event]:
        
            if counter == 9:
                width += max_event_width + 40
                height = top_line
                max_event_width = calculate_event_width(name, 9, 18, result_string_nametags, event_ids)
                header = 'Event '
                header_width = stringWidth('Event ', 'Arial', 10) + stringWidth('Group', 'Arial', 10)
                while header_width < (indent + max_event_width - stringWidth('Group', 'Arial', 10)):
                    header += ' '
                    header_width = stringWidth(header, 'Arial', 10)
                header += 'Groups'

                label.add(shapes.String(width, height+15, header, fontSize = 10, fontName='Arial'))
            for event in event_ids:
                if event_ids[event] == group_event:
                    event_name = event_dict[event]
                    current_event = event
                    label.add(shapes.String(width, height, event_name, fontSize = 9, fontName='Arial'))
                    
                    for event_scrambler in scramblerlist:
                        scrambling_event = event_scrambler[0].split(' - ')[0]
                        if event_scrambler[0][-1:] == '1' or round_counter[current_event] == 1:
                            for event in event_dict:
                                if scrambling_event == event_dict[event]:
                                    scrambling_event = event
                            for scrambler in event_scrambler:
                                if current_event == scrambling_event:
                                    scrambler = str(scrambler)
                                    if name[0] == scrambler: 
                                        scrambling.append(event_scrambler[1])
            
            group_string = ''
            group_number = name[group_event]
            for event_infos in group_list:
                if event_infos[0] == current_event and event_infos[1][-1:] == '1':
                    group_count = event_infos[2]
            if scrambling: 
                does_scramble = True
                for rounds in range(1,group_count+1):
                    if rounds != group_number and rounds in scrambling:
                        group_string += 's' + str(rounds) + ','
                    elif rounds == group_number:
                        group_string += str(group_number) + ','

                group_string = group_string[:-1]
            else:
                group_string = str(group_number)

            label.add(shapes.String(width+5+max_event_width, height, group_string, fontSize = 9, fontName='Arial'))
            height -= 11
            counter += 1
    if does_scramble:
        label.add(shapes.String(180, 140, 's = Scrambler', fontSize = 8, fontName='Arial'))

def pdf_splitter(path):
    fname = os.path.splitext(os.path.basename(path))[0]
 
    pdf = PdfFileReader(path)
    for page in range(pdf.getNumPages()):
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf.getPage(page))
 
        output_filename = competition_name + '/{}_page_{}.pdf'.format(
            fname, page+1)
 
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)
            
def merger(output_path, input_paths):
    pdf_merger = PdfFileMerger()
    file_handles = []
 
    for path in input_paths:
        pdf_merger.append(path)
        os.remove(path)
 
    with open(output_path, 'wb') as fileobj:
        pdf_merger.write(fileobj)


'''        
######

competitor_information_nametags = sorted(competitor_information, key=lambda x: x['name'])
result_string_nametags = sorted(result_string, key=lambda x: x[0])

sheet = labels.Sheet(specs, write_name, border=True)
sheet.add_labels(name for name in competitor_information_nametags)
nametag_file = competition_name + '/' + competition_name_stripped + '-nametags.pdf'
sheet.save(nametag_file)

if len(result_string_nametags) % 2 == 1:
    result_string_nametags.append(('', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',),)
for person in range(0, len(result_string_nametags)):
    if person % 2 == 0:
        swapping_id = person + 1
        swapping_person = result_string_nametags[swapping_id]
        result_string_nametags[swapping_id] = result_string_nametags[person]
        result_string_nametags[person] = swapping_person

sheet = labels.Sheet(specs, write_grouping, border=True)
sheet.add_labels((name, result_string_nametags, event_ids, scramblerlist) for name in result_string_nametags)
grouping_nametag_file = competition_name + '/' + competition_name_stripped + '-nametags-grouping.pdf'
sheet.save(grouping_nametag_file)

if two_sided_nametags:
    pdf_splitter(grouping_nametag_file)
    pdf_splitter(nametag_file)

    paths1 = glob.glob(competition_name + '/' + competition_name_stripped + '-nametags_*.pdf')
    paths2 = glob.glob(competition_name + '/' + competition_name_stripped + '-nametags-grouping_*.pdf')
    paths = paths1 + paths2
    paths = sorted(paths, key=lambda x: x.split('_')[2])

    merger(nametag_file, paths)
    os.remove(grouping_nametag_file)

'''
