from time import sleep, strftime
from random import randint
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart



class WebscrapeKayak:

    def __init__(self, city_from = None, city_to = None, date_start = None, date_end = None):
        self.city_from  = city_from  if city_from  else input('From which city?')
        self.city_to    = city_to    if city_to    else input('Where to?')
        self.date_start = date_start if date_start else input('Search around which departure date? Please use YYYY-MM-DD format only')
        self.date_end   = date_end   if date_end   else input('Return when? Please use YYYY-MM-DD format only')
        self.chromedriver_path = '../chromedriver_linux64/chromedriver'
        self.driver = webdriver.Chrome(executable_path = self.chromedriver_path)
        sleep(2)

    # TODO: add functionality for different dates flexibility

    def open_link(self):
        """ opens Kayak webpage"""
        kayak_link = ('https://www.kayak.com/flights/' + self.city_from + '-' + self.city_to +
                      '/' + self.date_start + '-flexible/' + self.date_end + '-flexible?sort=bestflight_a')
        self.driver.get(kayak_link)

    def close_popup(self):
        """Closes the popup window on Kayak """
        try:
            xp_popup_close = '//button[contains(@id,"dialog-close") and contains(@class,"Button-No-Standard-Style close ")]'
            self.driver.find_elements_by_xpath(xp_popup_close)[8].click()
        except:
            pass

    def load_more(self):
        try:
            more_results = '//a[@class = "moreButton"]'
            self.driver.find_element_by_xpath(more_results).click()
        except:
            pass

    def split_list(self, array):
        return array[::2], array[1::2]

    def run(self):
        self.open_link()
        print('linked opened')
        sleep(randint(8, 10))
        self.close_popup()
        print('popup closed')
        sleep(randint(20, 30))
        self.load_more()
        print('more loaded')
        sleep(randint(20, 30))

        df_flights_best = self.page_scrape()
        # df_flights_best['sort'] = 'best'
        # sleep(randint(60, 80))
        # x = input()

    def page_scrape(self):
        """This function takes care of the scraping part"""
        xp_sections = '//*[@class="section duration allow-multi-modal-icons"]'
        flight_legs = [value.text for value in self.driver.find_elements_by_xpath(xp_sections)]
        flights_dep, flights_ret = self.split_list(flight_legs)

        # If lists are empty, probably some captcha issue, --> raise SystemExit
        if not flights_dep:
            raise SystemExit

        flight_parts = []
        variables = [v + suffix for v in ['section_names', 'duration'] for suffix in ['_dep', '_ret']]
        flight_data = dict().fromkeys(variables, [])

        xp_dates = '//div[@class="section date"]'
        xp_prices = '//a[@class="booking-link "]/span[@class="price option-text"]/span[@class = "price-text"]'
        xp_stops = '//div[@class="section stops"]/div[1]'
        xp_stops_cities = '//div[@class="section stops"]/div[2]'
        xp_schedule = '//div[@class="section times"]'

        # # I'll use the letter A for the outbound flight and B for the inbound
        # a_duration = []
        # a_section_names = []
        # for n in section_a_list:
        #     # Separate the time from the cities
        #     a_section_names.append(''.join(n.split()[2:5]))
        #     a_duration.append(''.join(n.split()[0:2]))
        # b_duration = []
        # b_section_names = []
        # for n in section_b_list:
        #     # Separate the time from the cities
        #     b_section_names.append(''.join(n.split()[2:5]))
        #     b_duration.append(''.join(n.split()[0:2]))

        xp_dates = '//div[@class="section date"]'
        dates = [value.text for value in self.driver.find_elements_by_xpath(xp_dates)]
        dates_dep, dates_ret = self.split_list(dates)

        # # Separating the weekday from the day
        # a_day = [value.split()[0] for value in a_date_list]
        # a_weekday = [value.split()[1] for value in a_date_list]
        # b_day = [value.split()[0] for value in b_date_list]
        # b_weekday = [value.split()[1] for value in b_date_list]

        # getting the prices
        prices = driver.find_elements_by_xpath(xp_prices)
        prices_list = [price.text.replace('$', '') for price in prices if price.text != '']
        prices_list = list(map(int, prices_list))

        # the stops are a big list with one leg on the even index and second leg on odd index
        stops = self.driver.find_elements_by_xpath(xp_stops)
        stops = [stop.text[0].replace('n', '0') for stop in stops]
        stops_dep, stops_ret = self.split_list(stops)


        stops_cities = [stop.text for stop in self.driver.find_elements_by_xpath(xp_stops_cities)]
        stops_names_dep , stops_names_ret  = self.split_list(stops_cities)


        # this part gets me the airline company and the departure and arrival times, for both legs
        schedules = self.driver.find_elements_by_xpath(xp_schedule)
        hours = []
        carrier = []
        for schedule in schedules:
            hours.append(schedule.text.split('\n')[0])
            carrier.append(schedule.text.split('\n')[1])
        # split the hours and carriers, between a and b legs
        hours_dep , hours_ret = self.split_list(hours)
        carrier_dep , carrier_ret = self.split_list(hours)


        cols = (['Out Day', 'Out Time', 'Out Weekday', 'Out Airline', 'Out Cities', 'Out Duration', 'Out Stops',
                 'Out Stop Cities',
                 'Return Day', 'Return Time', 'Return Weekday', 'Return Airline', 'Return Cities', 'Return Duration',
                 'Return Stops', 'Return Stop Cities',
                 'Price'])

        # flights_df = pd.DataFrame({'Out Day': a_day,
        #                            'Out Weekday': a_weekday,
        #                            'Out Duration': a_duration,
        #                            'Out Cities': a_section_names,
        #                            'Return Day': b_day,
        #                            'Return Weekday': b_weekday,
        #                            'Return Duration': b_duration,
        #                            'Return Cities': b_section_names,
        #                            'Out Stops': a_stop_list,
        #                            'Out Stop Cities': a_stop_name_list,
        #                            'Return Stops': b_stop_list,
        #                            'Return Stop Cities': b_stop_name_list,
        #                            'Out Time': a_hours,
        #                            'Out Airline': a_carrier,
        #                            'Return Time': b_hours,
        #                            'Return Airline': b_carrier,
        #                            'Price': prices_list})[cols]

        flights_df['timestamp'] = strftime("%Y%m%d-%H%M")  # so we can know when it was scraped
        return flights_df


scrape = WebscrapeKayak(city_from = 'ORD', city_to = 'ATH', date_start = '2020-06-30', date_end = '2020-07-20')
scrape.run()

# for flight in zip(['_dep', '_ret'], [flights_dep, flights_ret]):
#     suffix, flightpart = flight
#     for data in flightpart:
#         flight_length, *route = data.split('\n')
#         flight_lengths =
#         flight_data['duration' + suffix].append(flight_length)
#         flight_data['section_names' + suffix].append(''.join(route))