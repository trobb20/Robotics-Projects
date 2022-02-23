import logging

import requests
import json
import datetime


def format_plus_code(plus_code):
    """
    Takes a plus code (From google maps) and formats it for use
    in the google maps api
    :param plus_code: string containing the global plus code
    :return: out_code: url-formatted for use in the api call
    """
    out_code = ''
    for char in plus_code:
        if char == '+':
            out_code = out_code + '%2B'
        elif char == ' ':
            out_code = out_code + '%20'
        elif char == ',':
            pass
        else:
            out_code = out_code + char
    return out_code


def format_duration_text(s):
    """
    Takes google maps' api response string for time, and returns
    it as a timedelta object. Only works for durations < 1 day.

    Ex: '2 hours 15 minutes' becomes
        timedelta(hours=2, minutes=15)

    :param s: duration text string input
    :return: timedelta object
    """
    l = s.split(' ')
    nums = []
    text = []
    hrs = 0
    mins = 0
    for i in enumerate(l):
        if i[0] % 2 == 0:  # if even, its a number
            nums.append(int(i[1]))
        elif i[0] % 2 == 1:  # if odd, its a string
            text.append(i[1])
        else:
            logging.error('Error! This should never happen.')

    for i in enumerate(text):
        ind = i[0]
        s = i[1]
        if 'hour' in s:
            hrs = nums[ind]
        elif 'min' in s:
            mins = nums[ind]
        else:
            logging.error('Not an hour or a min.')

    return datetime.timedelta(hours=hrs, minutes=mins)


def google_maps_api_call(origin, destination, api_f):
    """
    Calls the google maps destination matrix api given an origin and destination
    Requires an api_key stored in a text file.
    :param origin: Plus-code formatted origin
    :param destination: Plus-code formatted destination
    :param api_f: API key filename
    :return: returns the json response from Google
    """
    base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?departure_time=now'
    destinations = '&destinations=%s' % (format_plus_code(destination))
    origins = '&origins=%s' % (format_plus_code(origin))
    api_key = '&key=%s' % (open(api_f, 'r').read())

    full_url = base_url + destinations + origins + api_key

    j = json.loads(requests.get(full_url).text)
    logging.debug(json.dumps(j, indent=4, sort_keys=True))
    return j


def return_times_from_api(response):
    """
    Given a google maps api response json, returns the time
    spent driving (w/o traffic, w/ traffic)
    as timedelta objects.
    :param response: JSON response from google api
    :return:
            duration: driving time normally
            duration_in_traffic: driving time given traffic conditions
    """
    if response['status'] == 'OK':
        element = response['rows'][0]['elements'][0]
        duration_s = element['duration']['text']
        duration = format_duration_text(duration_s)
        duration_in_traffic_s = element['duration_in_traffic']['text']
        duration_in_traffic = format_duration_text(duration_in_traffic_s)
    else:
        logging.error('Got an error from the api.')
        return None
    logging.debug('Duration: %s'%str(duration))
    logging.debug('Duration in traffic: %s' % str(duration_in_traffic))
    return duration, duration_in_traffic
