# Readme for SI507 Final Project: Simple Restaurant Search
## Supplying API Keys
API keys are required for both Yelp Fusion and Documenu APIs. The keys have to be applied for on the respective websites.  
To use Yelp Fusion API, you need to include a header in your GET request, in the form of headers = {'Authorization': 'Bearer %s' % YELP_KEY}.  
To use a Documenu API, simply attach <&key=DOC_KEY> to the end of your query string.
## Interacting with Program
There are two main ways to interact with my Flask program.  
The first is to search with a restaurant name for basic info, reviews, menu of the specific restaurant.  
The second one is to search for top 5 restaurants that match your search fields. The search will return basic info of the top 5 restaurants as well as 3 review scipts for each restaurants.  
To make the search work, one has to fill in all required fields, which includes location and user name for both methods, and an additional restaurant name is required for menu search. Failure to enter the name will result in the application directing user to an error page, which tells the user which information he/she is missing.  
If no corresponding restaurant is found for menu search, the application will direct user to a page informing him/her that there is no match. There will always be top 5 results for top 5 search option.
### Menu Search
This type of search requires use to enter the exact restaurant name and its location, either in city/state or longtitude&latitude format. Optional search fields include sort_by method, which is the criterion for the Yelp API to select restaurants, as well as the restaurant categories in Yelp Category list. 
### Top 5 Search
The required field of this search is location. Optional fields include sort_by method and categories.