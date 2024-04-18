import googlemaps
from dotenv import dotenv_values
import requests
from ..utils.helper import findNearestStation, getCurrentDatetime, isPeak, isBusinessDay, isHoliday
import urllib.parse
import json
import os

current_dir = os.getcwd()
dotenv_path = os.path.join(current_dir, '.env')
collected_path = os.path.join(current_dir, '..', 'collectedData.json')
config = dotenv_values(dotenv_path)
googleApiKey=config["GOOGLE_API_KEY"]
gojekToken=config["GOJEK_TOKEN"]
zigToken=config["ZIG_TOKEN"]
zigGoogToken=config["ZIG_GOOGLEMAP_TOKEN"]
tadaToken=config["TADA_TOKEN"]
zigRefreshToken=config["ZIG_REFRESH_TOKEN"]

Maps = googlemaps.Client(key=googleApiKey)

def calculateDistAndDura(startDestination,endDestination):
    DistanceObject = Maps.directions(startDestination,endDestination)
    distance,duration = DistanceObject[0]["legs"][0]["distance"]["value"],DistanceObject[0]["legs"][0]["duration"]["value"]
    return distance,duration

def calculateGojek(startLat,startLong,endLat,endLong):
    headers={
        "Authorization": gojekToken,
        "Gojek-Country-Code": "SG",
        "Content-Type": "application/json"
    }
    data={
        "allow_usst_override": True,
        "include_preferred_payment_method": False,
        "send_prioritised_order": True,
        "user_selected_service_type": 50,
        "waypoints": [
            {"latitude": startLat, "longitude": startLong},
            {"latitude": endLat, "longitude": endLong}
    ]
    }

    url = ""
    try:
        response = requests.post(url,headers=headers,json=data).json()
        price = response["data"]["estimates"][0]["payment_methods"][1]["estimated_price"]["without_voucher"]
        surgeFactor = response["data"]["estimates"][0]["payment_methods"][1]["surge"]["surge_factor"]
        gojekDistance = response["data"]["estimates"][0]["route"]["distance_in_meters"]
        return price,surgeFactor,gojekDistance
    except Exception as e:
        print("An error occured at calcgojek:", e)
        return "An error occurred: {}".format(e)
    
def get_gojek_price(startLat,startLong,endLat,endLong):
    headers={
        "Authorization": gojekToken,
        "Gojek-Country-Code": "SG",
        "Content-Type": "application/json"
    }
    data={
        "allow_usst_override": True,
        "include_preferred_payment_method": False,
        "send_prioritised_order": True,
        "user_selected_service_type": 50,
        "waypoints": [
            {"latitude": startLat, "longitude": startLong},
            {"latitude": endLat, "longitude": endLong}
    ]
    }

    url = ""
    try:
        response = requests.post(url,headers=headers,json=data).json()
        price = response["data"]["estimates"][0]["payment_methods"][1]["estimated_price"]["without_voucher"]
        return float(price)
    except Exception as e:
        print("An error occured at get_gojek_price:", e)
        return 100
        # return "An error occurred: {}".format(e)
    
def calculateTada(startLat,startLong,endLat,endLong):
    headers={
        "Authorization": tadaToken,
        "Content-Type": "application/json"
    }
    data={
        "locations":[
            {
                "latitude":startLat,
                "longitude":startLong
            },
            {
                "latitude":endLat,
                "longitude":endLong
            }
        ],
        "isStudentFleet":"false"
    }
    
    url = ""
    try:
        response = requests.post(url,headers=headers,json=data).json()
        price = response["products"][0]["price"]
        distance = response["routes"]["0"]["distanceMeter"]
        duration = response["routes"]["0"]["duration"]
        return price,distance,duration
    except Exception as e:
        print("An error occured at calc tada:", e)
        return 200
        # return "An error occurred: {}".format(e)
    
def get_tada_price(startLat,startLong,endLat,endLong):
    headers={
        "Authorization": tadaToken,
        "Content-Type": "application/json"
    }
    data={
        "locations":[
            {
                "latitude":startLat,
                "longitude":startLong
            },
            {
                "latitude":endLat,
                "longitude":endLong
            }
        ],
        "isStudentFleet":"false"
    }
    
    url = ""
    try:
        response = requests.post(url,headers=headers,json=data).json()
        price = response["products"][0]["price"]
        return price
    except Exception as e:
        print("An error occured at get tada:", e)
        return 300
        # return "An error occurred: {}".format(e)

def calculateZig(startLat,startLong,startAddrRef,endLat,endLong,endAddrRef):
    headers={
        "Content-Type": "application/x-www-form-urlencoded"
    }

    url = ""
    try:
        response = requests.post(url,headers=headers,data=data).json()
        price = response["fares"][0]["oriFareUpper"]
        isSurge = response["fares"][0]["surgeIndicator"]
        return price,isSurge
    except Exception as e:
        if(renewAccessToken()):
            return calculateZig(startLat,startLong,startAddrRef,endLat,endLong,endAddrRef)
        return "An error occurred: {}".format(e)

def get_zig_price(startLat,startLong,startAddrRef,endLat,endLong,endAddrRef):
    headers={
        "Content-Type": "application/x-www-form-urlencoded"
    }


    url = ""
    try:
        response = requests.post(url,headers=headers,data=data).json()
        price = response["fares"][0]["oriFareUpper"]
        return price
    except Exception as e:
        if(renewAccessToken()):
            return get_zig_price(startLat,startLong,startAddrRef,endLat,endLong,endAddrRef)
        return "An error occurred: {}".format(e)


def renewAccessToken():
    global zigToken
    global zigGoogToken
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data={
        "refreshToken":zigRefreshToken,
    }

    url=""
    try:
        response = requests.post(url,headers=headers,data=data).json()
        newToken = response["accessToken"]
        zigToken=newToken
        zigGoogToken = "Bearer "+newToken
        return True
    except Exception as e:
        print("An error occured at renew acess:", e)
        return False


def get_dest_addr_ref(address):
    headers={
        "Authorization": zigGoogToken,
        "Content-Type": "application/json"
    }
    data={
        "radius": 50,
        "countryCode": "65",
        "searchStr": address
    }
    url = ""
    try:
        response = requests.post(url,headers=headers,json=data).json()
        data = response["data"]
        return data
    except Exception as e:
        if(renewAccessToken()):
            return get_dest_addr_ref(address)
        return "An error occurred: {}".format(e)
    
def getStartAddrRef(startLat,startLong):
    headers={
        "Authorization": zigGoogToken,
        "Content-Type": "application/json"
    }
    data={
        "countryCode": "65",
        "lat":startLat,
        "lng": startLong,
    }
    url = ""
    try:
        response = requests.post(url,headers=headers,json=data).json()
        data = response["addrRef"]
        return data
    except Exception as e:
        print("An error occured at get start addr ref:", e)
        return "An error occurred: {}".format(e)

def getRainfall(startLat,startLong):
    main_api='https://api.data.gov.sg/v1/environment/rainfall?'
    dateTime = getCurrentDatetime()
    station = findNearestStation(startLat,startLong)
    url=main_api+urllib.parse.urlencode({'date_time':dateTime})
    rainfall = 0
    try:
        data=requests.get(url).json()
        itemArr = data["items"][0]["readings"]
        for item in itemArr:
            if item["station_id"] == station:
                rainfall = item["value"]
    except Exception as e:
        return "An error occured at get rainfaill:{}".format(e)
    return rainfall

def querydump(startLocation,endLocation):
    try:
        dateTime=getCurrentDatetime()
        gojekFare,gojekSurgeFactor,gojekDistance = calculateGojek(startLocation["latitude"],startLocation["longitude"],endLocation["latitude"],endLocation["longitude"])
        tadaFare,tadaDistance,tadaDuration = calculateTada(startLocation["latitude"],startLocation["longitude"],endLocation["latitude"],endLocation["longitude"])
        zig_price, zigSurge = calculateZig(startLocation["latitude"],startLocation["longitude"],startLocation["addrRef"],endLocation["latitude"],endLocation["longitude"],endLocation["addrRef"])
        distance,duration=calculateDistAndDura(
            (startLocation["latitude"],startLocation["longitude"]),
            (endLocation["latitude"],endLocation["longitude"])
        )
        rain = getRainfall(startLocation["latitude"],startLocation["longitude"])
        peak = isPeak(dateTime)
        holiday = isHoliday(dateTime)
        businessDay = isBusinessDay(dateTime)
    except Exception as e:
        print("An error occured at query dump:", e)
        return "An error occurred: {}".format(e)

    
    Id = 0
    # Read the existing JSON file
    with open(collected_path, 'r') as json_file:
        existing_data = json.load(json_file)
        Id = len(existing_data)+1

    data={
        "Id": Id,
        "timeStamp":dateTime,
        "startLat": startLocation["latitude"],
        "startLong":startLocation["longitude"],
        "startLocation":startLocation["name"],
        "endLat":endLocation["latitude"],
        "endLong": endLocation["longitude"],
        "endLocation": endLocation["name"],
        "googleDistance": distance,
        "googleDuration":duration,
        "gojekFare": gojekFare,
        "gojekSurgeFactor":gojekSurgeFactor,
        "gojekDistance":gojekDistance,
        "tadaFare":tadaFare,
        "tadaDistance":tadaDistance,
        "tadaDuration":tadaDuration,
        "zig_price":zig_price,
        "zigSurge":zigSurge,
        "rainfall":rain,
        "isPeak":peak,
        "isHoliday":holiday,
        "isBusinessDay":businessDay 
    }

    # Append the new data to the existing array
    existing_data.append(data)
    
    # Write the updated array back to the JSON file
    with open(collected_path, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

    print("success")
