from time import sleep, strftime
from random import randint
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart


class WebscrapeKayak:

    def __init__(self, city_from = None, city_to = None, date_start = None, date_end = None):

        self.city_from  = city_from  if  city_from  else input('From which city?')
        self.city_to    = city_to    if  city_to    else input('Where to?')
        self.date_start = date_start if  date_start else input('Search around which departure date? Please use YYYY-MM-DD format only')
        self.date_end   = date_end   if  date_end   else input('Return when? Please use YYYY-MM-DD format only')


WebscrapeKayak()
