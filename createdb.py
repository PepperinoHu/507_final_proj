import sqlite3

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

insert_restaurants = '''
INSERT INTO restaurants
VALUES (NULL,?,?,?,?,?,?,?)
'''
BORN = ['Born & Raised NYC','6','Brooklyn, NY 11221','$','Spanish,Tapas','Mon-Thu, Sun: 5pm-11pm Fri-Sat: 5pm-12am','']
cur.execute(insert_restaurants,BORN)
conn.commit()
conn = sqlite3.connect("restaurants.sqlite")
cur = conn.cursor()
insert_review = '''
INSERT INTO reviews
VALUES(NULL,?,?,?,?,?)
'''
name = 'Born & Raised NYC'
a = cur.execute('''
SELECT Id FROM restaurants WHERE Name = ?''', [name])
review = ['Chris C.','5','2017-10-21 13:01:40','Great combination after having a beer from Brooklyn Lagar Brewery. Got the steak quesadilla with quac. They made it on the spot and it was cheesy, creamy,...',a.fetchall()[0][0]]
cur.execute(insert_review,review)
conn.commit()