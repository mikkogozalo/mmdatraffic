# -*- coding: utf-8 -*-
from dateutil.parser import parse
import arrow

from scrapy import Item, Field
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose

class IntensityItem(Item):
    name = Field()
    line = Field()
    direction = Field()
    intensity = Field()
    guid = Field()
    timestamp = Field()
    mmda_line_id = Field()
    mmda_loc_id = Field()

class AdvisoryItem(Item):
    body = Field()

def direction_processor(direction):
    if isinstance(direction, basestring) and direction:
        allowed_directions = ['n', 'e', 'w', 's']
        if direction[0].lower() in allowed_directions:
            return direction[0].upper() + 'B'

def intensity_processor(intensity):
    if isinstance(intensity, basestring) and intensity:
        intensity_map  = {
            'heavy': 5,
            'mod': 3,
            'light': 1,
            'l' : 1,
            'ml': 2,
            'm': 3,
            'mh': 4,
            'h': 5
        }
        if intensity.lower() in intensity_map:
            return intensity_map[intensity.lower()]
    elif isinstance(intensity, int):
        return intensity

def date_processor(date):
    try:
        parsed_date = arrow.get(parse(date))
        return parsed_date.timestamp
    except:
        return date


class IntensityItemLoader(ItemLoader):
    default_item_class = IntensityItem
    default_output_processor = TakeFirst()

    direction_in = MapCompose(direction_processor)
    intensity_in = MapCompose(intensity_processor)
    timestamp_in = MapCompose(date_processor)
