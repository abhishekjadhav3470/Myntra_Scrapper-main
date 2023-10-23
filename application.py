from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
import csv
import os
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By # This needs to be used 

application = Flask(__name__) # initializing a flask appa
app=application

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
          
          DRIVER_PATH = r"chromedriver.exe"
          driver = webdriver.Chrome(DRIVER_PATH)
          searchString = request.form['content'].replace(" ","")
          # Navigate to the URL
          driver.get("https://www.myntra.com/kurta?rawQuery="+searchString)
          myntra_text = driver.page_source
          myntra_html = bs(myntra_text, "html.parser")
          pclass=myntra_html.findAll("ul", {"class": "results-base"})
          for i in pclass:
            href = i.find_all('a', href=True)
            t=(href[0]['href'])
          productLink = "https://www.myntra.com/"+ t 
          driver.get(productLink)
          prodRes= driver.page_source
          prodRes_html = bs(prodRes, "html.parser") 
          title_h=prodRes_html.findAll("title")
          title=title_h[0].text
          overallRating=prodRes_html.findAll("div",{"class":"index-overallRating"})
          for i in overallRating:
              rating_value = i.find('div').text
          price=prodRes_html.findAll("span",{"class":"pdp-price"})
          for i in price:
                p=i.text
          Reviews=prodRes_html.find("a",{"class":"detailed-reviews-allReviews"})
          t2=Reviews['href']
          Review_link="https://www.myntra.com"+t2
          driver.get(Review_link)
          review_page= driver.page_source
          driver.quit()
          review_html = bs(review_page, "html.parser")
          review=review_html.findAll("div",{"class":"detailed-reviews-userReviewsContainer"})
          for i in review:
            user_rating=i.findAll("div",{"class":"user-review-main user-review-showRating"})
            user_comment=i.findAll("div",{"class":"user-review-reviewTextWrapper"})
            user_name=i.findAll("div",{"class":"user-review-left"})
         
          filename = searchString + ".csv"
          with open(filename, "w", newline='', encoding='utf-8') as fw:
                headers = ["Product Name","Over_All_Rating","Price","Date","Rating","Name","Comment"]
                writer = csv.DictWriter(fw, fieldnames=headers)
                writer.writeheader()

                reviews = []  
                for i in range(len(user_rating)):
                    try:
                        rating = user_rating[i].find('span', class_='user-review-starRating').get_text().strip()
                    except:
                        rating="No rating Given"    
                    try:    
                        comment=user_comment[i].text
                    except:
                        comment="No comment Given" 
                    try:       
                        name = user_name[i].find('span').text
                    except:
                        name="No Name given"
                    try:    
                        date = user_name[i].find_all('span')[1].text 
                    except:
                        date="No Date given"       
                    mydict = {"Product Name":title,"Over_All_Rating":rating_value,"Price":p,"Date": date,"Rating": rating,"Name":name,"Comment":comment}
                    reviews.append(mydict)
                writer.writerows(reviews) 
          client = pymongo.MongoClient("mongodb+srv://abc:abc@cluster0.lj6xm5o.mongodb.net/?retryWrites=true&w=majority")
          db = client['myntra_scrap1']
          review_col = db['review_scrap_data']
          review_col.insert_many(reviews)
          return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
	#app.run(debug=True)              
                                

          
                
