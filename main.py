import logging

import requests
from bs4 import BeautifulSoup

PARK_AND_RIDE_DIRECTORY_URL = "https://tfgm.com/public-transport/park-and-ride"


class ParkAndRideLocation(object):

    __slots__ = ["name", "latitude", "longitude", "transport_mode", "url"]

    def __str__(self):
        return f"Name: {self.name}; Latitude: {self.latitude}; Longitude: {self.longitude}; " \
               f"Transport Mode: {self.transport_mode}; URL: {self.url};"


def fetch_park_and_ride_locations():
    parsed_page = BeautifulSoup(requests.get(PARK_AND_RIDE_DIRECTORY_URL).text, "html.parser")
    location_list_items = parsed_page.find("div", attrs={"ng-controller": "ParkAndRideController"}).find_all("li")
    locations = [transform_location_list_item(location_list_item) for location_list_item in location_list_items]
    return locations


def transform_location_list_item(location_list_item):
    location = ParkAndRideLocation()
    location.name = location_list_item.text.strip()
    location.latitude = location_list_item.get("data-latitude")
    location.longitude = location_list_item.get("data-longitude")
    location.transport_mode = location_list_item.get("data-mode")
    location.url = location_list_item.find("a").get("href")
    return location


def enrich_location(location):
    # TODO: Go to URL of location, and extract additional data
    pass


def main():
    locations = fetch_park_and_ride_locations()
    if not locations:
        logging.error(f"Failed to fetch Park and Ride locations from {PARK_AND_RIDE_DIRECTORY_URL}")
    for location in locations:
        enrich_location(location)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        handlers=[logging.StreamHandler(), logging.FileHandler('tfgmParkAndRideDetailsScraper.log')])
    main()
