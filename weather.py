import json
import re
import urllib.request
import json,requests
import datetime
from collections import OrderedDict

from flask import Flask, render_template, request
from flask import jsonify
  
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


"""
:param request: 
:returns 
"""


def get_cities(raw_cities):
    """
    Function used to extract the city names individually
    :param request: the cities names in string format
    :returns a list with all the city names
    """
    #Delimiter can be  ',' and ' '
    cities = re.split(',',raw_cities)
    return cities




def check_date_format(raw_date):
    """
    Function used to chck if he date
    has the format in dd-mm-yyyy
    :param request: a certain date in string format
    :returns True is the format is correct, otherwise False
    """
    format = "%d.%M.%Y"
    try:
      datetime.datetime.strptime(raw_date, format)
      print("This is the correct date string format.")
      return True
    except ValueError:
      print("This is the incorrect date string format. It should be DD.MM.YYYY")    
      return False



def check_date(raw_date):
    """
    Function used to check if the date is
    included in the interval of the next 5 days
    :param request: a certain date in string format
    :returns True if it is in the next 5 days, otherwise False
    """
    parsed_date = re.split('\.', raw_date)
    day, month, year = int(parsed_date[0]), int(parsed_date[1]), int(parsed_date[2])

    format = "%d.%M.%Y"
    date = datetime.datetime(year=year, month=month, day=day)  
    today = date.today()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    available_date = today + datetime.timedelta(days=5)

    if(date < today or date > available_date):
        return False
    else:
        return True



def get_city_weather(city_name, raw_date):
    """
    Function used to get weather data for a 
    certain city on a specific date
    :param request:  city name and raw date in string format
    :returns a dictionary that encapsulates the weather data 
    in the specified date, or a error message if the city was not found
    """
    api_key = "6792b1d006d22c787a7150f9fd0d1ec2"
    url = "https://api.openweathermap.org/data/2.5/forecast?q=%s&&appid=%s&units=metric" % (city_name,  api_key)

    parsed_date = re.split('\.', raw_date)

    day,month,year = None, None, None
    if len(parsed_date[0]) > 1:
        day, month, year = (parsed_date[0]), (parsed_date[1]), (parsed_date[2])
    else:
        day, month, year = ('0'+ parsed_date[0]), (parsed_date[1]), (parsed_date[2])
    actual_date = year+"-"+month+"-"+day


    response = requests.get(url)
    # Check if the city was not found
    if response.status_code > 400 and response.status_code < 500:
        return "City not found"

    y = json.loads(response.text)

    # Build the response with weather data
    result_city = {}
    for x in y['list']:
        if actual_date in x['dt_txt']:
            temperature = str(x['main']['temp']) +" C, "
            weather_description = x['weather'][0]['description']
            wind_speed = ", Wind " + str(x['wind']['speed']) + " m/s"
            result_city[x['dt_txt']] =  temperature + weather_description + wind_speed
   
    return result_city




@app.route('/weather_route/', methods =['POST', 'GET'])
def weather_endpoint_1():
    """
    Function used to route the API queries for the weather_route endpoint
    :param request: an HTTPRequest object ( its actually  type is <class 'werkzeug.local.LocalProxy'>)
    :returns an HttpResponse for the query in JSON format
    """
    raw_cities = request.args.get('route')
    raw_date = request.args.get('date')

    # Check that the route has at least a city
    if not len(raw_cities) > 0:
        result={}
        result['cod'] = "404"
        result['message'] = 'The route must have at least one city'
        return jsonify(result)

    # Check the date format
    if not check_date_format(raw_date):
        result={}
        result['cod'] = "404"
        result['message'] = 'Invalid date format'
        #return json.dumps(result)
        return jsonify(result)


    # Check the if the date is in the next 5 days
    if not check_date(raw_date):
        result={}
        result['cod'] = "404"
        result['message'] = 'Date is out of boundaries'
        return jsonify(result)



    ## Query the weathermapapi for each city
    cities = get_cities(raw_cities)
    result = OrderedDict()
    for city in cities:
        weather = get_city_weather(city, raw_date)
        result[city] = weather


    return jsonify(result)





def get_city_weather_bonus(city_name, raw_date, city_ind):
    """
    Function used to get weather data for a 
    certain city on a specific date
    :param request:  city name ,raw date in string format and the city index in the route, 
    :returns a dictionary that encapsulates the weather data 
    in the specified date, or a error message if the city was not found
    """
    api_key = "6792b1d006d22c787a7150f9fd0d1ec2"
    url = "https://api.openweathermap.org/data/2.5/forecast?q=%s&&appid=%s&units=metric" % (city_name,  api_key)

    parsed_date = re.split('\.', raw_date)

    day,month,year = None, None, None
    if len(parsed_date[0]) > 1:
        day, month, year = (parsed_date[0]), (parsed_date[1]), (parsed_date[2])
    else:
        day, month, year = ('0'+ parsed_date[0]), (parsed_date[1]), (parsed_date[2])
    actual_date = year+"-"+month+"-"+day


    response = requests.get(url)
    # Check if the city was not found
    if response.status_code > 400 and response.status_code < 500:
        return "City not found"

    y = json.loads(response.text)


    # Taking into account that time passes while travelling between cities
    # I assume it exist a magic car  which takes exactly 1 hour between any 2 cities
    time_arrival = None
    time_arrival_interval = None
    if  city_ind < 3:
        time_arrival_interval = '09:00:00'
        switcher = {
            0: "09:00:00",
            1: "10:00:00",
            2: "11:00:00",
        }
        time_arrival = switcher.get(city_ind, "nothing")
    elif city_ind < 6:
        time_arrival_interval = '12:00:00'
        switcher = {
            3: "12:00:00",
            4: "13:00:00",
            5: "14:00:00",
        }
        time_arrival = switcher.get(city_ind, "nothing")
    elif city_ind < 9:
        time_arrival_interval = '15:00:00'
        switcher = {
            6: "15:00:00",
            7: "16:00:00",
            8: "17:00:00",
        }
        time_arrival = switcher.get(city_ind, "nothing")        
    elif city_ind < 12:
        time_arrival_interval = '18:00:00'
        switcher = {
            9: "18:00:00",
            10: "19:00:00",
            11: "20:00:00",
        }
        time_arrival = switcher.get(city_ind, "nothing")              

    # Build the response with weather data
    result_city = {}
    for x in y['list']:
        if actual_date in x['dt_txt'] and time_arrival_interval in x['dt_txt']:

            temperature = str(x['main']['temp']) +" C, "
            weather_description = x['weather'][0]['description']
            wind_speed = ", Wind " + str(x['wind']['speed']) + " m/s"

            actual_time = x['dt_txt'].split(" ")[0] + " "  + time_arrival
            result_city[actual_time] =  temperature + weather_description + wind_speed
   
    return result_city



@app.route('/weather_route_bonus/', methods =['POST', 'GET'])
def weather_endpoint_bonus_1():
    """
    Function used to route the API queries for the weather_route_bonus_1 endpoint
    taking into account that time passes while travelling between cities
    :param request: an HTTPRequest object ( its actually  type is <class 'werkzeug.local.LocalProxy'>)
    :returns an HttpResponse for the query in JSON format taking into account that time passes
    """
    raw_cities = request.args.get('route')
    raw_date = request.args.get('date')

    # Check that the route has at least a city
    if not len(raw_cities) > 0:
        result={}
        result['cod'] = "404"
        result['message'] = 'The route must have at least one city'
        return jsonify(result)

    # Check that the route has at least a city
    if not len(raw_cities) > 12:
        result={}
        result['cod'] = "404"
        result['message'] = 'The route must have at most twelve cities'
        return jsonify(result)        

    # Check the date format
    if not check_date_format(raw_date):
        result={}
        result['cod'] = "404"
        result['message'] = 'Invalid date format'
        #return json.dumps(result)
        return jsonify(result)


    # Check the if the date is in the next 5 days
    if not check_date(raw_date):
        result={}
        result['cod'] = "404"
        result['message'] = 'Date is out of boundaries'
        return jsonify(result)



    # Query the openweathermap API for each city
    # taking into account time passes while travelling between cities
    cities = get_cities(raw_cities)
    result = OrderedDict()
    city_index = 0
    for city in cities:
        weather = get_city_weather_bonus(city, raw_date, city_index)
        result[city] = weather
        city_index = city_index + 1


    return jsonify(result)









@app.route('/past_trips/', methods =['POST', 'GET'])
def weather_endpoint_bonus_2():
    """
    Function used to route the API queries for the past_trips endpoint
    :param request: an HTTPRequest object ( its actually  type is <class 'werkzeug.local.LocalProxy'>)
    :returns an HttpResponse for the query in JSON format with the last 5 past trips
    somebody queried for
    """
    raw_cities = request.args.get('route')
    raw_date = request.args.get('date')

    # Check that the route has at least a city
    if not len(raw_cities) > 0:
        result={}
        result['cod'] = "404"
        result['message'] = 'The route must have at least one city'
        return jsonify(result)

    # Check the date format
    if not check_date_format(raw_date):
        result={}
        result['cod'] = "404"
        result['message'] = 'Invalid date format'
        #return json.dumps(result)
        return jsonify(result)


    # Check the if the date is in the next 5 days
    if not check_date(raw_date):
        result={}
        result['cod'] = "404"
        result['message'] = 'Date is out of boundaries'
        return jsonify(result)



    ## Query the weathermapapi for each city
    cities = get_cities(raw_cities)
    result = OrderedDict()
    city_index = 0
    for city in cities:
        weather = get_city_weather_bonus(city, raw_date, city_index)
        result[city] = weather
        city_index = city_index + 1


    return jsonify(result)





  
if __name__ == '__main__':
    app.run(debug = True)