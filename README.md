# Facebook Data Scraping - Download Photo from your Facebook profile.

## Why I created this

I forked this repository from stevenvo's profile. I wanted to download all the photos from my facebook profile.
I modified the script to make it work with python 3. I also changed the way the script parsed the data coming from facebook, because
facebook changed the way its html responses looked like

## Prerequisites
These are the open-source libraries or framework utilized in the project, which **requires installation before hand**:
* [Scrapy framework](http://scrapy.org/): a very powerful web data scraping tool and framework for Python developers. Installation using PIP: `pip install scrapy`
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/): a great HTML text entities parsing & formatting library. Installation: `pip install beautifulsoup4`
* Image module: `pip install image`
* Twisted module: `pip install twisted`
* python 3

## Usage

### Clone the repository to your machine
```
$ git clone https://github.com/LeDevDuDimanche/facebook_data_scraping.git
$ cd facebook_data_scraping
```
### Execute

```
scrapy crawl photo_crawler -a email=<email> -a password=<password> -a target_username=<profile_username>
```
__Parameters:__
* `email`: login email to your Facebook account.
* `password`: login password to your Facebook account.
* `target_username`: Facebook profile ID which you want to crawl all images from. Using your browser and go to your friend's profile or yours, the profile ID is the string after the split character '/'.
  * For example https://www.facebook.com/johnson, the ID will be `johnson`.

All images will be downloaded into folder `downloaded-photos`. The image filename will have 2 parts: 1st part contains the `target_username`, 2nd part is the random file name.

*__Notes:__*
- I've configured `THROTTLE` and `USER-AGENT` parameters in the settings.py. It makes the query more reasonable with less "robot" browsing speed  and more legit user agent. Feel free to adjust it to your needs.
- Don't ask me about using Facebook Graph API. Facebook has removed the API access to friends data since v2.4, all you can read is your own information. So it's not much very useful here.


__Disclaimer: this is an open-source project for educational purposes, please use it at your own risk, I'm not responsible for your account being banned by Facebook, nor your password is stolen.__
