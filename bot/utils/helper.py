from datetime import datetime,time,timezone, timedelta
import requests
import json
import math
import pytz
import os
import boto3
import random
import time
import json
import uuid
from bot.repository import user as user, query as query, userTravelHistory as user_travel_history, ads as ads
from math import radians, sin, cos, sqrt, atan2

def weekDayOrWeekEnd(timestamp):
    # Parse the timestamp into a datetime object
    datetime_obj = datetime.fromisoformat(timestamp)
    # Extract the weekday from the datetime object
    weekno = datetime_obj.weekday()
    # Check if it's a weekday (0 to 4 are Monday to Friday)
    if weekno < 5:
        return "Weekday"
    else:
        return "Weekend"

def isHoliday(timestamp):
    datetime_obj = datetime.fromisoformat(timestamp)
    current_date = datetime_obj.strftime("%Y-%m-%d")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    holidayPath = os.path.join(current_dir, 'public_holidays_mapping.json')
    with open(holidayPath,"r") as file:
        data = json.load(file)
        if data.get(current_date)==True:
            return True
        return False

def isPeak(timestamp):
    datetime_obj = datetime.fromisoformat(timestamp)
    current_time = datetime_obj.time()
    day = weekDayOrWeekEnd(timestamp)
    range2_start = time(17, 0)
    range2_end = time(23, 59)
    if day == "Weekend":
        range1_start = time(10, 0)
        range1_end = time(13, 59)
        if (range1_start <= current_time <= range1_end):
            return True
    elif day == "Weekday":
        range3_start = time(6,0)
        range3_end = time(9,29)
        if(range3_start<=current_time<=range3_end):
            return True
    if  range2_start <= current_time <= range2_end:
        return True
    return False

def isBusinessDay(timestamp):
    if weekDayOrWeekEnd(timestamp) == "Weekday" and not isHoliday(timestamp):
        return True
    
#generate a random timestamp in DD/MM/YY format in the past 2 weeks
def generate_random_timestamp(start_date="15/03/2024", end_date="29/03/2024", date_format="%d/%m/%Y"):
    start = datetime.strptime(start_date, date_format)
    end = datetime.strptime(end_date, date_format)
    delta = end - start
    random_days = random.randrange(delta.days + 1) # +1 to include the end date
    random_date = start + timedelta(days=random_days)
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    random_timestamp = random_date.replace(hour=random_hour, minute=random_minute, second=random_second)
    return random_timestamp.strftime("%d/%m/%Y %H:%M:%S")

def generate_random_timestamp_specific_day(day="15/03/2024", start_hour=8):
    date_format = "%d/%m/%Y %H:%M:%S"
    start_datetime = datetime.strptime(f"{day} {start_hour}:00:00", date_format)
    # Assuming the end time is the end of the day (23:59:59)
    end_datetime = start_datetime.replace(hour=23, minute=59, second=59)
    delta_seconds = int((end_datetime - start_datetime).total_seconds())
    random_seconds = random.randrange(delta_seconds + 1) # +1 to include the end time
    random_timestamp = start_datetime + timedelta(seconds=random_seconds)
    return random_timestamp.strftime(date_format)
    
def findNearestStation(startLat,startLong):
    min = float('inf')
    stationId = ''
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rainPath = os.path.join(current_dir, 'rainStations.json')
    with open(rainPath,"r") as file:    
        data = json.load(file)
        for station in data:
            distance = math.sqrt((startLat - station["location"]["latitude"])**2 + (startLong - station["location"]["longitude"])**2)
            if distance < min:
                min = distance
                stationId = station["id"]
    return stationId

def getCurrentDatetime():
    # Get the current date and time in UTC
    current_datetime_utc = datetime.now(pytz.utc)

    # Convert UTC time to your desired timezone (in this case, UTC+8:00)
    sg_timezone = pytz.timezone('Asia/Singapore')
    current_datetime_local = current_datetime_utc.astimezone(sg_timezone)

    # Format the datetime object as a string in the desired format
    formatted_datetime = current_datetime_local.strftime("%Y-%m-%dT%H:%M:%S%z")

    return formatted_datetime

def get_current_date():
    # Get the current date and time in UTC
    current_datetime_utc = datetime.now(pytz.utc)

    # Convert UTC time to your desired timezone (in this case, UTC+8:00)
    sg_timezone = pytz.timezone('Asia/Singapore')
    current_datetime_local = current_datetime_utc.astimezone(sg_timezone)

    # Format the datetime object as a string in the desired format
    formatted_date = current_datetime_local.strftime("%Y-%m-%d")

    return formatted_date

def get_epoch_time():
    return str(int(time.time()))

def convert_epoch_to_human(epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))

#convert human readable time to epoch
def convert_human_to_epoch(humanReadable):
    return int(time.mktime(time.strptime(humanReadable, '%Y-%m-%d %H:%M:%S')))

def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in meters
    R = 6371000.0  # meters

    # Convert latitude and longitude from degrees to radians
    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    # Calculate the change in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Calculate the distance using Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance

def within_1_km(location1,location2):
    lat1, lon1 = location1.split(',')
    lat2, lon2 = location2.split(',')
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    return distance <= 1000

def within_2_km(location1,location2):
    lat1, lon1 = location1.split(',')
    lat2, lon2 = location2.split(',')
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    return distance <= 2000

def scanTable(tableName,table):
    response = table.scan()
    items = response['Items']
    return items

def genRandomQuery():
    #Generate random number between a certain range
    randomNum = random.randint(20, 40)
    #generate random percentage value
    randomPercentage = random.uniform(0.5, 1.0)
    clicks = round(randomNum * randomPercentage)
    return randomNum, clicks

def generateSpend():
    randomNum = random.randint(200,600)
    return randomNum

def generateAdClicks():
    randomNum = random. randint(1, 15)
    randomPercentage = random.uniform(0.2, 0.3)
    clicks = round(randomNum * randomPercentage)
    return randomNum,clicks

def getSpendingPower(userId,table=None):
    item = user.get_user(userId,table)
    #if item has no ['spend'] or ['app_clicks'] attribute, return low
    if not hasattr(item, 'spend') or not hasattr(item, 'app_clicks'):
        return 'low'
    apc = float(item['spend'])/float(item['app_clicks'])
    if apc >= 30:
        return "High"
    elif apc >= 20 and apc < 30:
        return "Medium"
    else:
        return "Low"

def isActive(userId,table=None):
    response = query.get_latest_query(userId,table)
    if response:
        response = int(response['timestamp'])
        current_time = int(time.time())
        if current_time - response <= 1209600:
            return True
        else:
            return False
    return False
    

def getEngagementLevel(userId,user_table=None,query_table=None):
    response = user.get_user(userId,user_table)
    if not response:
        return "Low"
    if not hasattr(response, 'spend') or not hasattr(response, 'app_clicks') or not hasattr(response, 'ad_clicks') or not hasattr(response, 'ads_sent') or not hasattr(response, 'queries'):
        return 'Low'
    adCTR = float(response['ad_clicks'])/float(response['ads_sent']) *100
    ctr = float(response['app_clicks'])/float(response['queries']) * 100
    active = isActive(userId, query_table)
    if not active:
        return "Low"
    if adCTR > 5 and ctr > 40:
        return "High"
    elif adCTR > 2 and ctr > 20:
        return "Medium"
    else:
        return "Low"

def preferredTravelTime(userid,table=None):
    response = query.get_all_user_queries(userid,table)
    timeRanges = {
    "Morning": (6, 12),
    "Afternoon": (12, 18),
    "Night": (18, 24),
    "Early_morning": (0, 6)
    }

    timeMap = {
        "Morning":0,
        "Afternoon":0,
        "Night": 0,
        "Early_morning":0
    }

    for i in response:
        timehr = time.strftime('%H:%M:%S', time.localtime(int(i['timestamp'])))
        hour = int(timehr.split(':')[0])

        for period, (start, end) in timeRanges.items():
            if start <= hour < end:
                # Increment corresponding key in timeMap
                timeMap[period] += 1
                break
    
    #Find the most frequent time range and return the time period
    preferredTime = max(timeMap, key=timeMap.get)
    return preferredTime

def contains_point(userId,targetPoints,table=None):
    items = user_travel_history.get_user_frequent_locations(userId,table)
    points = []
    for item in items:
        points.append(item['location'])
    for point in points:
        for targetPoint in targetPoints['SS']:
            if within_2_km(point, targetPoint):
                return True
    return False

def qualified(userId,ad_item,table_obj=None):
    spending_power = getSpendingPower(userId,table_obj['user_table'])
    engagement_level = getEngagementLevel(userId,table_obj['user_table'],table_obj['query_table'])
    time = preferredTravelTime(userId,table_obj['query_table'])
    close_proximity = contains_point(userId,ad_item['locations'],table_obj['user_travel_history_table'])
    #Do weighted sum of the 4 parameters
    if spending_power == ad_item['spending_power']:
        spending_power_score = 1
    else:
        spending_power_score = 0
    if engagement_level == ad_item['engagement_level']:
        engagement_level_score = 1
    else:
        engagement_level_score = 0
    if time == ad_item['preferred_time']:
        preferred_time_score = 1
    else:
        preferred_time_score = 0
    if close_proximity:
        close_proximity_score = 1
    else:
        close_proximity_score = 0
    
    score = (spending_power_score * 0.3) + (engagement_level_score * 0.3) + (close_proximity_score * 0.3)+(preferred_time_score * 0.1) 
    if(score>=0.5):
        return True
    return False

def getAd(userId,table=None):
    response = ads.get_all_ads_sortby_bid(table['ad_table'])
    for item in response:
        if qualified(userId, item, table):
            return item
    return None

def has_received_ad(userId,table=None):
    curr_date = get_current_date()
    response = user.get_ad_received(userId,table)
    if response == curr_date:
        return True
    return False