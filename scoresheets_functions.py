import labels
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, stringWidth
from reportlab.graphics import shapes
from reportlab.lib import colors

def scoresheet_results_header(label, limit, limit_width, font_size_limit, height):
    ### Depending on the length of the 'limit' string (which includes (cumulative) limits), the box height gets choosen
    if limit_width > 150:
        box_height = 15
    else:
        box_height = 0
    label.add(shapes.Rect(10,height-105-box_height,30, 15+box_height, fillColor=colors.white))
    label.add(shapes.String(12,height-100-box_height/2.0,'Attempt',fontSize=7, fontName='Arial'))
    label.add(shapes.Rect(210,height-105-box_height,30, 15+box_height, fillColor=colors.white))
    label.add(shapes.String(215,height-100-box_height/2.0,'Judge',fontSize=8, fontName='Arial'))
    label.add(shapes.Rect(245,height-105-box_height,30, 15+box_height, fillColor=colors.white))
    label.add(shapes.String(250,height-100-box_height/2.0,'Comp',fontSize=8, fontName='Arial'))
    
    if stringWidth(limit, 'Arial', font_size_limit) > 150:
        label.add(shapes.Rect(45,height-120,160, 30, fillColor=colors.white))
        label.add(shapes.String(49,height-100,limit[:40], fontSize=font_size_limit, fontName='Arial'))
        label.add(shapes.String(49,height-115,limit[41:], fontSize=font_size_limit, fontName='Arial'))
        height = height - 15
    else:
        label.add(shapes.Rect(45,height-105,160, 15, fillColor=colors.white))
        label.add(shapes.String(49,height-100,limit, fontSize=font_size_limit, fontName='Arial'))
        
def scoresheet_result_boxes(label, height, format, event, cutoff_number, name):
    height = height - 105
    number = 1
    for k in range(0,format):
        height -= 35
        label.add(shapes.Rect(10,height,30, 30, fillColor=colors.white))
        label.add(shapes.String(22,height+10,str(number),fontSize=12, fontName='Arial'))
        label.add(shapes.Rect(45,height,160, 30, fillColor=colors.white))
        label.add(shapes.Rect(210,height,30, 30, fillColor=colors.white))
        label.add(shapes.Rect(245,height,30, 30, fillColor=colors.white))
        
        # Special treatment for 3x3x3 Multi-Blindfolded: additional info in result boxes
        if event == '333mbf':
            label.add(shapes.Line(50, height+8, 72, height+8,trokeColor=colors.black))
            label.add(shapes.String(74,height+10,'out of',fontSize=10, fontName='Arial'))
            label.add(shapes.Line(100, height+8, 125, height+8,trokeColor=colors.black))
            label.add(shapes.String(125,height+10,'  Time:',fontSize=10, fontName='Arial'))
            label.add(shapes.Line(156, height+8, 200, height+8,trokeColor=colors.black))
    
        # Add cutoff information (if there are any)
        if cutoff_number == number and name['name']:
            if cutoff_number == 1: 
                cutoff = 'Continue if Attempt 1 is below ' + cutoff_time
                indent = 70
            else:
                cutoff = 'Continue if Attempt 1 or Attempt 2 is below ' + cutoff_time
                indent = 93
            label.add(shapes.Line(10,height-13,width/2.0-indent,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
            label.add(shapes.Line(width/2+indent,height-13,width-10,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
            label.add(shapes.String(width/2.0,height-15,cutoff,fontSize=8,textAnchor='middle', fontName='Arial'))
            height -= 20
        number+= 1
    return height
        
def scoresheet_extra(label, height, width):
    label.add(shapes.Line(10,height-13,width/2.0-50,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
    label.add(shapes.Line(width/2+50,height-13,width-10,height-13,trokeColor=colors.black,strokeWidth=1,strokeDashArray=[2,2])) 
    label.add(shapes.String(width/2.0,height-15,'Extra or Provisional Solve',fontSize=8,textAnchor='middle', fontName='Arial'))
    label.add(shapes.Rect(10,height-55,30, 30, fillColor=colors.white))
    label.add(shapes.Rect(45,height-55,160, 30, fillColor=colors.white))
    label.add(shapes.Rect(210,height-55,30, 30, fillColor=colors.white))
    label.add(shapes.Rect(245,height-55,30, 30, fillColor=colors.white))
    
def scoresheet_blank_header(label, height, width, competition_name):
    text_width = width - 10
    font_size = 25
    comp_name_width = stringWidth(competition_name, 'Arial', font_size)
    while comp_name_width > text_width:
        font_size *= 0.95
        comp_name_width = stringWidth(competition_name, 'Arial', font_size)
    label.add(shapes.String(width/2, height-25, competition_name, textAnchor='middle', fontSize=font_size, fontName='Arial'))

    label.add(shapes.Rect(10,height-63,125, 17, fillColor=colors.white))
    label.add(shapes.String(12, height-58, 'Event:', fontSize=12, fontName='Arial'))
    label.add(shapes.Rect(140,height-63,65, 17, fillColor=colors.white))
    label.add(shapes.String(142, height-58, 'Round:', fontSize=12, fontName='Arial'))
    label.add(shapes.Rect(210,height-63,65, 17, fillColor=colors.white))
    label.add(shapes.String(212, height-58, 'Group:', fontSize=12, fontName='Arial'))
    label.add(shapes.Rect(10,height-85,195, 17, fillColor=colors.white))
    label.add(shapes.String(12, height-80, 'Name:', fontSize=12, fontName='Arial'))
    label.add(shapes.Rect(210,height-85,65, 17, fillColor=colors.white))
    label.add(shapes.String(212, height-80, 'Id:', fontSize=12, fontName='Arial'))
