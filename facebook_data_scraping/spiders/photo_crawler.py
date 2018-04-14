# -*- coding: utf-8 -*-

import scrapy
import re
import json
import urllib.parse


from bs4 import BeautifulSoup
from scrapy.shell import inspect_response
from scrapy.http import FormRequest
from facebook_data_scraping.items import FacebookPhoto


class PhotoCrawlerSpider(scrapy.Spider):
    # ARGS
    target_username = ""
    email = ""
    password = ""

    # VARS
    album_id = ""
    user_id = ""
    name = "photo_crawler"
    allowed_domains = ["m.facebook.com"]
    start_urls = (
        'http://m.facebook.com/',
    )
    top_url = 'https://m.facebook.com'

    def __init__(self, *args, **kwargs):
      super(PhotoCrawlerSpider, self).__init__(*args, **kwargs)

      self.debugFile = open('debugFile', 'w')
      self.email = kwargs.get('email')
      self.password = kwargs.get('password')
      self.target_username = kwargs.get('target_username')

    def parse(self, response):
        return [FormRequest("https://m.facebook.com/login.php",
            formdata={
                'email': self.email,
                'pass': self.password
            }, callback=self.parse_post_login)
        ]

    def parse_post_login(self, response):
        return scrapy.Request("{0}/{1}?v=photos".format(self.top_url, self.target_username), callback=self.parse_user_photo_page)

    def parse_user_photo_page(self, response):
        def extract_album_id(s): 
            p = re.compile(r'set=t\.(\d*)')
            search = re.search(p, s)
            return search.group(1)

        def extract_user_id(s):
            p = re.compile(r'"USER_ID":"(\d*)"')
            search = re.search(p, s)
            return search.group(1)

        utf8ResponseBody = self.getUtf8ResponseBody(response)
        self.album_id = extract_album_id(utf8ResponseBody)
        self.user_id = extract_user_id(utf8ResponseBody)
        ajax_photos_url = "{0}/{1}?v=photos&psm=default&album=t.{2}&__ajax__=&__user={3}".format(
            self.top_url, self.target_username, self.album_id, self.user_id
        )
        return scrapy.Request(ajax_photos_url, callback=self.parse_photos)

    def getUtf8ResponseBody(self, response):
        return response.body.decode("utf-8")

    def parse_photos(self, response):
        def extract_photo_pages(html_str):
            p = re.compile(r'href="(/photo\.php.*?)">')
            m = re.findall(p, html_str)
            photo_page_urls = []
            for encoded_url in m:
                photo_page_urls.append("{0}{1}".format(self.top_url, BeautifulSoup(encoded_url, 'html.parser').get_text()))
            return photo_page_urls

        # need to throw exception if can't find next_cursor (END condition)
        def extract_next_cursor(html_str):
            p = re.compile(r'cursor=(\d*)&')
            search = re.search(p, html_str)
            return search.group(1)

        def last_photo_query(url, next_cursor):
            parsed = urllib.parse.urlparse(url)
            cursor = urllib.parse.parse_qs(parsed.query)['cursor']
            return cursor == next_cursor

        responseBody = self.getUtf8ResponseBody(response)
    
        if responseBody.startswith("for (;;);"):
            json_obj = json.loads(responseBody[9:]) #remove prefix "for (;;);""
        else:
            json_obj = json.loads(responseBody)

        photo_urls = extract_photo_pages(json_obj['payload']['actions'][0]['html'])
        next_cursor = extract_next_cursor(json_obj['payload']['actions'][2]['code'])

        for photo_url in photo_urls:
            full_url = yield scrapy.Request(photo_url, callback=self.parse_photo)

        if response.url.find("cursor") >-1 and last_photo_query(response.url, next_cursor):
            yield
        else:
            ajax_photos_url = "https://m.facebook.com/{0}?v=photos&editdata=%7B%7D&cursor={1}&psm=default&album=t.{2}&__ajax__=&__user={3}".format(
                self.target_username, next_cursor, self.album_id, self.user_id
            )
            yield scrapy.Request(ajax_photos_url, callback=self.parse_photos)


    def parse_photo(self, response):
        def extract_full_size_photo_url(s):
            s = s.replace('\\', "")
            p = re.compile(r'href="([^"]+)" +class="sec"> *View Full Size')
            search = re.search(p, s)
            absoluteUrl = 'https://m.facebook.com/'+search.group(1)
            return BeautifulSoup(absoluteUrl, 'html.parser').get_text()

        responseBody = self.getUtf8ResponseBody(response)
        url = extract_full_size_photo_url(responseBody)
        print("PHOTO URL: "+url)
        fb_photo = FacebookPhoto()
        fb_photo["image_url"] = url
        fb_photo["username"] = self.target_username
        return fb_photo
        # inspect_response(response, self)
