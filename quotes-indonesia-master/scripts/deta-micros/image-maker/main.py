# quotes format: {caption}. --{author}
# example: `Lorem ipsum dolor sit. --Amet`

import json
import os
import random
from deta import Deta
from dotenv import load_dotenv
from flask import Flask, request, send_file
from io import BytesIO
from urllib import request as libreq
from PIL import Image, ImageDraw, ImageFont

load_dotenv('env')

app = Flask(__name__)
deta = Deta(os.environ.get('PROJECT_KEY'))

font_url  = 'https://github.com/google/fonts/blob/main/ofl/neucha/Neucha.ttf?raw=true'
quote_api_url = os.environ.get('QUOTE_API_URL')
random_quote_url = quote_api_url + '/random'

def generate_image(quote_body, quote_by):
    # image configuration
    img_width = 612
    img_height = 612

    # font configuration
    font_urls = [
        font_url
        # font_base_url + 'lobstertwo.ttf',
        # font_base_url + 'underdog.ttf',
        # font_base_url + 'specialelite.ttf',
        # font_base_url + 'abrilfatface.ttf',
        # font_base_url + 'merienda.ttf',
        # font_base_url + 'poiretone.ttf',
        # font_base_url + 'shadowsintolight.ttf',
        # font_base_url + 'caveatbrush.ttf',
        # font_base_url + 'gochihand.ttf',
        # font_base_url + 'itim.ttf',
        # font_base_url + 'rancho.ttf'
    ]
    font_selected = random.choice(font_urls)
    font_get = libreq.urlopen(font_selected)
    font = ImageFont.truetype(BytesIO(font_get.read()), 35)

    # color configuration
    # https://clrs.cc/
    colors = [
        { 'bg': (255, 255, 255),    'fg': (100,100,100) }
        # { 'bg': (0, 31, 63),        'fg': (128, 191, 255) },
        # { 'bg': (0, 116, 217),      'fg': (179, 219, 255) },
        # { 'bg': (127, 219, 255),    'fg': (0, 73, 102) },
        # { 'bg': (57, 204, 204),     'fg': (0, 0, 0) },
        # { 'bg': (61, 153, 112),     'fg': (22, 55, 40) },
        # { 'bg': (46, 204, 64),      'fg': (14, 62, 20) },
        # { 'bg': (1, 255, 112),      'fg': (0, 102, 44) },
        # { 'bg': (255, 220, 0),      'fg': (102, 88, 0) },
        # { 'bg': (255, 133, 27),     'fg': (102, 48, 0) },
        # { 'bg': (255, 65, 54),      'fg': (128, 6, 0) },
        # { 'bg': (133, 20, 75),      'fg': (235, 122, 177) },
        # { 'bg': (240, 18, 190),     'fg': (101, 6, 79) },
        # { 'bg': (177, 13, 201),     'fg': (239, 169, 249) },
        # { 'bg': (17, 17, 17),       'fg': (221, 221, 221) },
        # { 'bg': (170, 170, 170),    'fg': (0, 0, 0) },
        # { 'bg': (221, 221, 221),    'fg': (0, 0, 0) }
    ]
    color = random.choice(colors)

    # draw image
    image = Image.new('RGB', (img_width, img_height), color = color['bg'])
    document = ImageDraw.Draw(image)

    # find the average size of the letter in quote_body
    sum = 0
    for letter in quote_body:
        sum += document.textsize(letter, font=font)[0]
    average_length_of_letter = sum/len(quote_body)

    # find the number of letters to be put on each linex
    number_of_letters_for_each_line = (img_width / 1.818) / average_length_of_letter

    # build new text to put on the image
    incrementer = 0
    fresh_quote = ''
    for letter in quote_body:
        if (letter == '-'):
            # fresh_quote += '\n\n' + letter #add some line breaks
            fresh_quote += '' + letter
        elif (incrementer < number_of_letters_for_each_line):
            fresh_quote += letter
        else:
            if(letter == ' '):
                fresh_quote += '\n'
                incrementer = 0
            else:
                fresh_quote += letter
        incrementer += 1
    fresh_quote += '\n\n--' + quote_by

    # render the text in the center of the box
    dim = document.textsize(fresh_quote, font=font)
    x2 = dim[0]
    y2 = dim[1]
    qx = (img_width / 2 - x2 / 2)
    qy = (img_height / 2 - y2 / 2)
    document.text((qx,qy), fresh_quote, align="center", font=font, fill=color['fg'])

    # save image and return it as response
    image_io = BytesIO()
    image.save(image_io, 'JPEG', quality=100)
    image_io.seek(0)

    return send_file(image_io, mimetype='image/jpeg')

@app.get('/')
def http_index():
    default_quote = 'Aku masih menunggumu. --Lakuapik'
    quote_full = request.values.get('text') or default_quote
    quote_body, quote_by = quote_full.split(' --')
    return generate_image(quote_body, quote_by)

@app.get('/random')
def http_random():
    result = libreq.urlopen(random_quote_url).read()
    data = json.loads(result)
    return generate_image(data.get('quote'), data.get('by'))