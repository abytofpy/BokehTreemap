# -*- coding: utf-8 -*-
"""
Created on Thu May 20 10:01:28 2017
Treemap basic example - lacks any type of interactivity !
@author: seb F-S
"""

###############################################################################
#### Some squarify functions definitions - should happily sit in a module
###############################################################################

def normalize_sizes(sizes, dx, dy):
    total_size = sum(sizes)
    total_area = dx * dy
    sizes = list(map(float, sizes))
    sizes = list(map(lambda size: size * total_area / total_size, sizes))
    return sizes
   
def layoutrow(sizes, x, y, dx, dy):
    covered_area = sum(sizes)
    width = covered_area / dy
    rects = []
    for size in sizes:
        rects.append({'x': x, 'y': y, 'dx': width, 'dy': size / width})
        y += size / width
    return rects

def layoutcol(sizes, x, y, dx, dy):
    covered_area = sum(sizes)
    height = covered_area / dx
    rects = []
    for size in sizes:
        rects.append({'x': x, 'y': y, 'dx': size / height, 'dy': height})
        x += size / height
    return rects

def layout(sizes, x, y, dx, dy):
    return layoutrow(sizes, x, y, dx, dy) if dx >= dy else layoutcol(sizes, x, y, dx, dy)

def leftoverrow(sizes, x, y, dx, dy):
    covered_area = sum(sizes)
    width = covered_area / dy
    leftover_x = x + width
    leftover_y = y
    leftover_dx = dx - width
    leftover_dy = dy
    return (leftover_x, leftover_y, leftover_dx, leftover_dy)

def leftovercol(sizes, x, y, dx, dy):
    covered_area = sum(sizes)
    height = covered_area / dx
    leftover_x = x
    leftover_y = y + height
    leftover_dx = dx
    leftover_dy = dy - height
    return (leftover_x, leftover_y, leftover_dx, leftover_dy)

def leftover(sizes, x, y, dx, dy):
    return leftoverrow(sizes, x, y, dx, dy) if dx >= dy else leftovercol(sizes, x, y, dx, dy)
   
def worst_ratio(sizes, x, y, dx, dy):
    return max([max(rect['dx'] / rect['dy'], rect['dy'] / rect['dx']) for rect in layout(sizes, x, y, dx, dy)])

def squarify(sizes, x, y, dx, dy):
    sizes = list(map(float, sizes))
    if len(sizes) == 0:
        return []
    if len(sizes) == 1:
        return layout(sizes, x, y, dx, dy)
    # figure out where 'split' should be
    i = 1
    while i < len(sizes) and worst_ratio(sizes[:i], x, y, dx, dy) >= worst_ratio(sizes[:(i+1)], x, y, dx, dy):
        i += 1
    current = sizes[:i]
    remaining = sizes[i:]
    (leftover_x, leftover_y, leftover_dx, leftover_dy) = leftover(current, x, y, dx, dy)
    return layout(current, x, y, dx, dy) + squarify(remaining, leftover_x, leftover_y, leftover_dx, leftover_dy)

#### End of squarify functions definitions
###############################################################################
#### Bokeh demo starts here :

from bokeh.plotting import figure, output_file, show
from bokeh.models import LabelSet, ColumnDataSource


if __name__ == '__main__':
   
    x = 0.
    y = 0.
    width = 1
    height = 1
    norm_x= 1
    norm_y= 1
         
   
#### Please input your data here
    source = ColumnDataSource(
        data=dict(
            Labels = ['Granny Smith', 'Pink Lady', 'MCIntosh', 'Golden', 'Bosc',
                  'Comice', 'Red Anjou', 'bananas', 'Passion Fruit', 'Avocado',
                  'Lychee'],
            Quantity = [7, 12, 10, 2, 18, 14, 13, 3, 5, 9, 17],
            CVitamin = [12, 4.8, 11.6, 17.4, 5.6, 8.0, 8.0, 10.2, 60, 12.5, 6.6],
            Colors = ['#001a70', '#003089', '#0045a2', '#005bbb', '#509e2f', '#8aba18',
                      '#c4d600', '#001a70', '#003089', '#0045a2', '#005bbb'],
            Units = [' mg/100g']*11
            )
    )  
        
#### Select data to use as input for size of the rectangles (will be normalized)
    values = source.data['Quantity']

#### Calculation of rects size, coords
    values.sort(reverse=True)
   
    values = normalize_sizes(source.data['Quantity'], width, height)

    rects = squarify(values, x, y, width, height)

    X = [rect['x'] for rect in rects]
    Y = [rect['y'] for rect in rects]
    dX = [rect['dx'] for rect in rects]
    dY = [ rect['dy'] for rect in rects]


    XdX = []
    YdY = []

    for i in range(len(X)):
        XdX.append(X[i]+dX[i])
        YdY.append(Y[i]+dY[i])

#### Preparation of labels - compute rects centers in particular
    Xlab = []
    Ylab = []
    for r in rects:
        x, y, dx, dy = r['x'], r['y'], r['dx'], r['dy']
        Xlab.append(x+dx/2)
        Ylab.append(y+dy/2)

#### Now we have everything ready, let's gather data for the treemap
    plotsource = ColumnDataSource(
        data=dict(
            Xlab = Xlab,
            Ylab = Ylab,
            CVitamin = source.data['CVitamin'],
            Colors = source.data['Colors'],
            Labels = source.data['Labels'],
            Units = source.data['Units']
        )
    )

#### Bokeh figure :

    output_file("Bokeh Treemap.html", mode = 'inline')

    p = figure(plot_width=1200, plot_height=1024, title = 'Fruit Inventory, plus Vitamin C content')
    p.quad(top=YdY, bottom=Y, left=X, right=XdX, color=plotsource.data['Colors'])
   
    p.axis.visible = False
     
    labels1 = LabelSet(x='Xlab', y='Ylab', text='Labels', level='glyph',
        text_font_style='bold', text_color='white', text_align = 'center',
        source=plotsource)
   
    labels2 = LabelSet(x='Xlab', y='Ylab', text='CVitamin', level='glyph',
    text_font_style='bold', text_color='white', text_align = 'right',
    y_offset = -20, source=plotsource)

    labels3 = LabelSet(x='Xlab', y='Ylab', text='Units', level='glyph',
    text_font_style='bold', text_color='white', text_align = 'left',
    y_offset = -20, source=plotsource)
   
    p.add_layout(labels1)
    p.add_layout(labels2)
    p.add_layout(labels3)
    # showing p
    show(p)
