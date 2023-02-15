from flask import Flask, render_template,request,jsonify
from flask_cors import CORS,cross_origin
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import requests


app = Flask(__name__)

@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")


@app.route("/review", methods= ['POST','GET'])
def index():
    if request.method == 'POST':
        try:
            searchstring = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchstring
            uClient = uReq(flipkart_url)
            flipkart_page = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkart_page, "html.parser")
            bigboxes = flipkart_html.findAll("div",{"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            comment_boxes = prod_html.find_all('div', {"class":"_16PBlm"})

            filename = searchstring + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            
            for commentbox in comment_boxes:
                try:
                    name = commentbox.div.div.find_all('p',{'class':"_2sc7ZR _2V5EHH"})[0].text
                except:
                    name = 'No Name'

                try:
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = "No rating"

                try:
                    commentHead = commentbox.div.div.div.p.text
                
                except:
                    commentHead  = "No Comment Heading"

                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchstring, "Name": name, "Rating": rating, "CommentHead": commentHead, "Comment": custComment}
                reviews.append(mydict)
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            return 'something is wrong'





    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0")