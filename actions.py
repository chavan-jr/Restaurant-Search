from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import zomatopy
import json


class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurants'

    # def validate_location(self,tracker):
    # tier_1_2_cities = []
    # location = tracker.get_slot('location')
    # return location in tier_1_2_cities
    #def restaurants_based_on_budget(self, budget, d, n):b
        #if email
        #return 0

    def run(self, dispatcher, tracker, domain):
        config = {"user_key": "f4924dc9ad672ee8c4f8c84743301af5"}
        zomato = zomatopy.initialize_app(config)
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        budget = tracker.get_slot('budget')
        t1_t2_cities = ['Agra', 'Ajmer', 'Aligarh', 'Amravati', 'Amritsar', 'Asansol', 'Aurangabad', 'Bareilly',
                        'Belgaum', 'Bhavnagar', 'Bhiwandi', 'Bhopal', 'Bhubaneswar', 'Bikaner', 'Bilaspur',
                        'BokaroSteelCity', 'Chandigarh', 'Coimbatore', 'Cuttack', 'Dehradun', 'Dhanbad', 'Bhilai',
                        'Durgapur', 'Dindigul', 'Erode', 'Faridabad', 'Firozabad', 'Ghaziabad', 'Gorakhpur', 'Gulbarga',
                        'Guntur', 'Gwalior', 'Gurgaon', 'Guwahati', 'Hamirpur', 'Hubli–Dharwad', 'Indore', 'Jabalpur',
                        'Jaipur', 'Jalandhar', 'Jammu', 'Jamnagar', 'Jamshedpur', 'Jhansi', 'Jodhpur', 'Kakinada',
                        'Kannur', 'Kanpur', 'Kochi', 'Kolhapur', 'Kollam', 'Kozhikode', 'Kurnool', 'Ludhiana',
                        'Lucknow', 'Madurai', 'Malappuram', 'Mathura', 'Mangalore', 'Meerut', 'Moradabad', 'Mysore',
                        'Nagpur', 'Nanded', 'Nashik', 'Nellore', 'Noida', 'Patna', 'Pondicherry', 'Purulia',
                        'Prayagraj', 'Raipur', 'Rajkot', 'Rajahmundry', 'Ranchi', 'Rourkela', 'Salem', 'Sangli',
                        'Shimla', 'Siliguri', 'Solapur', 'Srinagar', 'Surat', 'Thanjavur', 'Thiruvananthapuram',
                        'Thrissur', 'Tiruchirappalli', 'Tirunelveli', 'Ujjain', 'Bijapur', 'Vadodara', 'Varanasi',
                        'Vasai-VirarCity', 'Vijayawada', 'Visakhapatnam', 'Vellore', 'Warangal', 'Ahmedabad',
                        'Bengaluru', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai', 'Pune']
        t1_t2_cities = [city.lower() for city in t1_t2_cities]

        if loc.lower() not in t1_t2_cities:
            dispatcher.utter_message("We do not operate in that area yet")
            return [SlotSet('location', loc)]

        location_detail = zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        lat = d1["location_suggestions"][0]["latitude"]
        lon = d1["location_suggestions"][0]["longitude"]
        cuisines_dict = {'chinese': 25,  'italian': 55,  'north indian': 50,'american': 1, 'mexican': 73,
                         'south indian': 85}
        results = zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 100)
        d = json.loads(results)
        global response_email
        response_email = ""
        response = ""

        if d['results_found'] == 0:
            response = "no results"
        else:
            response = self.restaurants_based_on_budget(budget,d, n = 5)
            response_email = self.restaurants_based_on_budget(budget,d,n=10)
            for restaurant in d['restaurants']:
                response_email = response_email + restaurant['restaurant']['name'] + " in " \
                                 + restaurant['restaurant']['location']['address'] \
                                 + " with average cost for 2 people = " + str(
                    restaurant['restaurant']['average_cost_for_two']) \
                                 + " and average rating of " + str(
                    restaurant['restaurant']['user_rating']['aggregate_rating']) + "\n"
                response = response + restaurant['restaurant']['name'] + " in " + restaurant['restaurant']['location'][
                    'address'] + " has been rated " \
                           + str(restaurant['restaurant']['user_rating']['aggregate_rating']) + "\n"

        message = "The details of all the restaurants you inquried \n \n"
        dispatcher.utter_message("-----" + response)

        # print(d['restaurants'])
        return [SlotSet('location', loc)]


class ActionSendEmail(Action):
    def name(self):
        return 'action_send_email'

    def run(self, dispatcher, tracker, domain):
        import smtplib
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login('restaurentsearchzomato@gmail.com', 'searchsearchsearch')
        email_body = 'sending this from python!'
        email_to = tracker.get_slot('email_id')
        try:
            server.sendmail('restaurentsearchzomato@gmail.com', str(email_to), email_body + response_email)
            server.quit()
            dispatcher.utter_message('The top 10 restaurants have been sent to your email id')
        except Exception as e:
            dispatcher.utter_message("-----" + 'Some error occured while sending email')
