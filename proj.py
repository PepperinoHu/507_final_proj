import json
from flask import Flask, render_template, request
import requests
from secrets import DOC_KEY,YELP_KEY
from json2html import *
import os.path
from os import path
import sqlite3
headers = {'Authorization': 'Bearer %s' % YELP_KEY}
yelp_url='https://api.yelp.com/v3/businesses/search'
yelp_url_review= 'https://api.yelp.com/v3/businesses/'

app = Flask(__name__)

conn = sqlite3.connect("restaurants.sqlite")
cur = conn.cursor()

drop_restaurants = '''
    DROP TABLE IF EXISTS "restaurants";
'''

create_restaurants = '''
    CREATE TABLE IF NOT EXISTS "restaurants" (
        Id       INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        Name  TEXT NOT NULL,
        Review_count TEXT NOT NULL,
        Location  TEXT NOT NULL,
        Price    TEXT NOT NULL,
        Cuisines    TEXT NOT NULL,
        Hours    TEXT NOT NULL,
        Image_url    TEXT NOT NULL
    );
'''
drop_reviews = '''
    DROP TABLE IF EXISTS "reviews";
'''
create_reviews = '''
    CREATE TABLE IF NOT EXISTS "reviews" (
        Id        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        Name  TEXT NOT NULL,
        Rating TEXT NOT NULL,
        Time_Created  TEXT NOT NULL,
        Review    TEXT NOT NULL,
        Restaurant_ID INTEGER NOT NULL,
        FOREIGN KEY(Restaurant_ID) REFERENCES restaurants(Id) 
       
    );
'''


cur.execute(drop_restaurants)
cur.execute(create_restaurants)
cur.execute(drop_reviews)
cur.execute(create_reviews)
conn.commit()
insert_restaurants = '''
INSERT INTO restaurants
VALUES (NULL,?,?,?,?,?,?,?)
'''
insert_review = '''
INSERT INTO reviews
VALUES(NULL,?,?,?,?,?)
'''
def open_cache(CACHE_FILENAME):
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict,CACHE_FILENAME):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


@app.route('/')
def index():     
    return render_template('search1.html')

@app.route('/handle_form', methods=['POST'])
def handle_the_form():
    user_name = request.form["name"]
    if user_name == '':
        return '''<html>
 <head>
 </head>
 <body>
   <h1>Please enter user name!<h1>
 </body>
</html> ''' 
    restaurant_name = request.form["restaurant"]
    try:
        sort_by = request.form["sort_by"]
    except:
        sort_by = 'best_match'
    location = request.form["location"]
    latitude = request.form["latitude"]
    longtitude = request.form['longtitude']
    if ((location =='')&(latitude =='')&(longtitude =='')):
        return '''<html>
 <head>
 </head>
 <body>
   <h1>Please enter location!<h1>
 </body>
</html> ''' 
    categories = request.form['categories']
    if restaurant_name != '':
        if (latitude != '')&(longtitude != ''):
            url = 'https://api.yelp.com/v3/businesses/search?term=restaurants&latitude='+latitude+'&longitude='+longtitude+'&name='+restaurant_name+'&categories='+categories
            cache_dict = open_cache('yelp.json')
            try:
                req = cache_dict['latitude='+latitude+'&longitude='+longtitude+'&name='+restaurant_name+'categories='+categories]
                print('using cache')
            except:
                print("searching with geolocation")
                req=requests.get(url, headers=headers).json()
                cache_dict['latitude='+latitude+'&longitude='+longtitude+'&name='+restaurant_name+'categories='+categories] = req
                save_cache(cache_dict,'yelp.json')
        elif location != '':
            params = {'term':'restaurants','location':location,'sort_by':sort_by,'name':restaurant_name,'categories':categories}
            cache_dict = open_cache('yelp.json')
            try:
                req = cache_dict['location='+location+'sort_by='+sort_by+'name='+restaurant_name+'categories='+categories]
                print('using cache')
            except:
                req=requests.get(yelp_url, params=params, headers=headers).json()
                cache_dict['location='+location+'sort_by='+sort_by+'name='+restaurant_name+'categories='+categories] = req
                save_cache(cache_dict,'yelp.json')
                print("searching by city/state")

        result_dict = {}
        for business in req['businesses']:
            result_dict = {}
            if business['name'] == restaurant_name:
                result_dict['name'] = business['name']
                result_dict['review_count'] = business['review_count']
                result_dict['image_url'] = business['image_url']
                result_dict['rating']=business['rating']
                result_dict['cuisines'] = ','.join([i['title'] for i in business['categories']])
                try:
                    result_dict['price'] = business['price']
                except:
                    result_dict['price'] = 'No price displayed'

                result_dict['location'] = (','.join(business['location']['display_address']))
                result_dict['phone'] = business['display_phone']

                menu_dict = open_cache('menus.json')
                try:
                    doc_response = menu_dict[business['name']]
                    print('using cache')
                except:
                    doc_response = requests.get("https://api.documenu.com/v2/restaurants/search/fields?restaurant_name="+business['name'] +"&exact=true&key="+DOC_KEY).json()
                    menu_dict[business['name']] = doc_response
                    save_cache(menu_dict, 'menus.json')
                    print("searching")

                if int(doc_response['totalResults']) == 0:
                    result_dict['menu'] = 'No menu available'
                else:
                    id =str(doc_response['data'][0]['restaurant_id'])
                    menu_dict = open_cache('menus.json')
                    try: 
                        menu_response = menu_dict[id]
                        print('using cache')
                    except:
                        menu_response = requests.get("https://api.documenu.com/v2/restaurant/"+id+"?key="+DOC_KEY).json()
                        menu_dict[id] = menu_response
                        save_cache(menu_dict,'menus.json')
                        print("searching")
                    
                    result_dict['menu'] = json2html.convert(json = menu_response['result']['menus'])
                try: 
                    result_dict['cuisines'] =  result_dict['cuisines'] + ','+(','.join(doc_response['data'][0]['cuisines']  ))
                except: 
                    pass
                try:   
                    result_dict['hours'] =    'Hours not available' if (doc_response['data'][0]['hours'] == '') else doc_response['data'][0]['hours']
                except:
                    pass
                
                conn = sqlite3.connect("restaurants.sqlite")
                cur = conn.cursor()
                restaurant_input = [result_dict['name'],result_dict['review_count'],result_dict['location'],result_dict['price'],result_dict['cuisines'],result_dict['hours'],result_dict['image_url']]
                cur.execute(insert_restaurants,restaurant_input)
                conn.commit()

                reviews_list = []
                review_dict = open_cache('reviews.json')
                try:
                    req_reviews = review_dict[business['id']]
                    print('using cache')
                except:
                    req_reviews=requests.get(yelp_url_review+ business['id']+'/reviews',headers=headers).json()
                    review_dict[business['id']] = req_reviews
                    save_cache(review_dict,'reviews.json')
                    print("searching")

                conn = sqlite3.connect("restaurants.sqlite")
                cur = conn.cursor()
                cursor_name = cur.execute('''SELECT Id FROM restaurants WHERE Name = ?''', [result_dict['name']])
                id = cursor_name.fetchall()[0][0]
                for review in req_reviews['reviews']:
                    review_dict = {}
                    review_dict['name'] = review['user']['name']
                    review_dict['rating'] = review['rating']
                    review_dict['time_created'] = review['time_created']
                    review_dict['text'] = review['text']
                    reviews_list.append(review_dict)
                    cur.execute(insert_review,[review_dict['name'],review_dict['rating'],review_dict['time_created'],review_dict['text'],id])
                conn.commit()
                result_dict['reviews'] = reviews_list

                template = open(r"C:\Users\IvanH\507_final_proj\templates\response_menu.html", "r")
                my_file_name = r'C:\Users\IvanH\507_final_proj\templates\response_menu_'+ result_dict['name']+".html"
                if path.exists(my_file_name) == False:
                    my_file = open(my_file_name, "w")
                    for line in template:
                        my_file.write(line)
                    my_file.write('Here is the menu for '+result_dict['name']+':')
                    my_file.write(result_dict['menu'])
                    my_file.write('</body>')
                    my_file.write('</html>')
                    my_file.close()
                    template.close()
                return render_template('response_menu_'+ result_dict['name']+".html", 
                    name=user_name, 
                    req=result_dict)
        
        return '''<html>
 <head>
 </head>
 <body>
   <h1>No match for chosen restaurant name, sorry!<h1>
 </body>
</html> ''' 


    
    if (latitude != '')&(longtitude != ''):
        url = 'https://api.yelp.com/v3/businesses/search?term=restaurants&latitude='+latitude+'&longitude='+longtitude+'&limit=5'+'&sort_by'+sort_by+'&categories='+categories
        cache_dict = open_cache('yelp.json')
        try:
            req = cache_dict['latitude='+latitude+'&longitude='+longtitude+'&sort_by'+sort_by+'&categories='+categories]
            print('using cache')
        except:
            print("searching with geolocation")
            req=requests.get(url, headers=headers).json()
            cache_dict['latitude='+latitude+'&longitude='+longtitude+'&sort_by'+sort_by+'&categories='+categories] = req
            save_cache(cache_dict,'yelp.json')
    elif location != '':
        cache_dict = open_cache('yelp.json')
        params = {'term':'restaurants','location':location,'limit':5,'sort_by':sort_by,'categories':categories}
        try:
            req = cache_dict['location='+location+'sort_by='+sort_by+'categories='+categories]
            print('using cache')
        except:
            req=requests.get(yelp_url, params=params, headers=headers).json()
            cache_dict['location='+location+'sort_by='+sort_by+'categories='+categories] = req
            save_cache(cache_dict,'yelp.json')
            print("searching with geolocation")   

    result_list = []
    for business in req['businesses']:
        result_dict = {}
        result_dict['name'] = business['name']
        result_dict['review_count'] = business['review_count']
        result_dict['image_url'] = business['image_url']
        result_dict['rating']=business['rating']
        result_dict['cuisines'] = ','.join([i['title'] for i in business['categories']])
        try:
            result_dict['price'] = business['price']
        except:
            result_dict['price'] = 'No price displayed'
        result_dict['location'] = (','.join(business['location']['display_address']))
        result_dict['phone'] = business['display_phone']

        reviews_list = []
        reviews_dict = open_cache('reviews.json')
        try:
            req_reviews = reviews_dict[business['id']]
            print('using cache')
        except:
            req_reviews=requests.get(yelp_url_review+ business['id']+'/reviews',headers=headers).json()
            reviews_dict[business['id']] = req_reviews
            save_cache(reviews_dict,'reviews.json')
            print("searching")
        for i in range(5):
            review_dict = {}
            try:
                review = req_reviews['reviews'][i]
                review_dict['name'] = review['user']['name']
                review_dict['rating'] = review['rating']
                review_dict['time_created'] = review['time_created']
                review_dict['text'] = review['text']
            except:
                pass
            reviews_list.append(review_dict)
        result_dict['reviews'] = reviews_list

        menu_dict = open_cache('menus.json')
        try:
            doc_response = menu_dict[business['name']]
        except:
            doc_response = requests.get("https://api.documenu.com/v2/restaurants/search/fields?restaurant_name="+business['name'] +"&exact=true&key="+DOC_KEY).json()
            menu_dict[business['name']] = doc_response
            save_cache(menu_dict, 'menus.json')

        try: 
            result_dict['cuisines'] =  result_dict['cuisines'] + ','+(','.join(doc_response['data'][0]['cuisines']  ))
        except: 
            pass
        try:   
            result_dict['hours'] =    'Hours not available' if (doc_response['data'][0]['hours'] == '') else doc_response['data'][0]['hours']
        except:
            pass
        result_list.append(result_dict)

    return render_template('response.html', 
        name=user_name, 
        req=result_list)

if __name__ == '__main__':  
    print('starting Flask app', app.name)
    app.run(debug=True)        