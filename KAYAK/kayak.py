from operator import itemgetter
from time import sleep, strftime
from random import randint
import pandas as pd
from selenium import webdriver


class WebscrapeKayak:

    def __init__(self, city_from=None, city_to=None, date_start=None, date_end=None):
        self.city_from = city_from if city_from else input('From which city?')
        self.city_to = city_to if city_to else input('Where to?')
        self.date_start = date_start if date_start else input(
            'Search around which departure date? Please use YYYY-MM-DD format only')
        self.date_end = date_end if date_end else input('Return when? Please use YYYY-MM-DD format only')
        self.chromedriver_path = '../chromedriver_linux64/chromedriver'
        self.driver = webdriver.Chrome(executable_path=self.chromedriver_path)
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
        df_flights_best['sort'] = 'best'
        sleep(randint(20, 30))

        # Matrix on top of page with lowest prices
        matrix = self.driver.find_elements_by_xpath('//*[contains(@id,"FlexMatrixCell")]')
        matrix_prices = list(map(int, [price.text.replace('$', '') for price in matrix]))
        matrix_min = min(matrix_prices)
        matrix_avg = sum(matrix_prices) / len(matrix_prices)

        xp_cheap_results = '//a[@data-code = "price"]'
        self.driver.find_element_by_xpath(xp_cheap_results).click()
        sleep(randint(20, 30))
        self.load_more()
        sleep(randint(20, 30))


        print('starting second scrape.....')
        df_flights_cheap = self.page_scrape()
        df_flights_cheap['sort'] = 'cheap'
        sleep(randint(20, 30))

        print('switching to quickest results.....')
        xp_quick_results = '//a[@data-code = "duration"]'
        self.driver.find_element_by_xpath(xp_quick_results).click()
        sleep(randint(20, 30))
        print('loading more.....')
        self.load_more()
        sleep(randint(20, 30))

        print('starting third scrape.....')
        df_flights_fast = self.page_scrape()
        df_flights_fast['sort'] = 'fast'
        sleep(randint(20, 30))

        # saving a new dataframe as an excel file. the name is custom made to your cities and dates
        final_df = df_flights_cheap.append(df_flights_best).append(df_flights_fast)
        final_df.to_excel('{}_flights_{}-{}_from_{}_to_{}.xlsx'.format(strftime("%Y%m%d-%H%M"),
                                                                       self.city_from, self.city_to,
                                                                       self.date_start, self.date_end),
                          index=False)


    def page_scrape(self):
        """This function scrapes KAYAK and retrieves all relevant info about each flight.
        That info is returned in a dataframe"""
        xp_sections = '//*[@class="section duration allow-multi-modal-icons"]'
        flight_legs = [value.text for value in self.driver.find_elements_by_xpath(xp_sections)]
        flights_dep, flights_ret = self.split_list(flight_legs)

        # If lists are empty, probably some captcha issue, --> raise SystemExit
        if not flights_dep:
            raise SystemExit

        xp_dates = '//div[@class="section date"]'
        xp_prices = '//a[@class="booking-link "]/span[@class="price option-text"]/span[@class = "price-text"]'
        xp_stops = '//div[@class="section stops"]/div[1]'
        xp_stops_cities = '//div[@class="section stops"]/div[2]'
        xp_schedule = '//div[@class="section times"]'

        duration_dep, duration_ret, section_names_dep, section_names_ret = ([] for _ in range(4))

        for flight in flights_dep:
            duration, *route = flight.split('\n')
            duration_dep.append(duration)
            section_names_dep.append(''.join(route))

        for flight in flights_ret:
            duration, *route = flight.split('\n')
            duration_ret.append(duration)
            section_names_ret.append(''.join(route))

        dates = [value.text for value in self.driver.find_elements_by_xpath(xp_dates)]
        dates_dep, dates_ret = self.split_list(dates)

        dates_dep = [d.split() for d in dates_dep]
        dates_ret = [d.split() for d in dates_ret]

        day_dep = list(map(itemgetter(0), dates_dep))
        day_ret = list(map(itemgetter(0), dates_ret))
        weekday_dep = list(map(itemgetter(1), dates_dep))
        weekday_ret = list(map(itemgetter(1), dates_ret))

        # getting the prices
        prices = self.driver.find_elements_by_xpath(xp_prices)
        prices_list = [price.text.replace('$', '') for price in prices if price.text != '']
        prices_list = list(map(int, prices_list))

        # the stops are a big list with one leg on the even index and second leg on odd index
        stops = [stop.text[0].replace('n', '0') for stop in self.driver.find_elements_by_xpath(xp_stops)]
        stops_dep, stops_ret = self.split_list(stops)

        stops_cities = [stop.text for stop in self.driver.find_elements_by_xpath(xp_stops_cities)]
        stops_names_dep, stops_names_ret = self.split_list(stops_cities)

        # this part gets me the airline company and the departure and arrival times, for both legs
        schedules = self.driver.find_elements_by_xpath(xp_schedule)
        hours, carrier = ([] for _ in range(2))
        for schedule in schedules:
            hour, carr = schedule.text.split('\n')
            hours.append(hour)
            carrier.append(carr)
        # split the hours and carriers, between a and b legs
        hours_dep, hours_ret = self.split_list(hours)
        carrier_dep, carrier_ret = self.split_list(hours)


        flight_data = {'Out Day': day_dep,
                       'Out Weekday': weekday_dep,
                       'Out Duration': duration_dep,
                       'Out Cities': section_names_dep,
                       'Return Day': day_ret,
                       'Return Weekday': weekday_ret,
                       'Return Duration': duration_ret,
                       'Return Cities': section_names_ret,
                       'Out Stops': stops_dep,
                       'Out Stop Cities': stops_names_dep,
                       'Return Stops': stops_ret,
                       'Return Stop Cities': stops_names_ret,
                       'Out Time': hours_dep,
                       'Out Airline': carrier_ret,
                       'Return Time': hours_ret,
                       'Return Airline': carrier_ret,
                       'Price': prices_list
                       }


        flights_df = pd.DataFrame(data=flight_data)
        flights_df['timestamp'] = strftime("%Y%m%d-%H%M")  # scraping time
        return flights_df


scrape = WebscrapeKayak(city_from='ORD', city_to='ATH', date_start='2020-06-30', date_end='2020-07-20')
scrape.run()
