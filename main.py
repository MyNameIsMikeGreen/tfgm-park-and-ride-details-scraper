import logging
import requests

from bs4 import BeautifulSoup
from itertools import groupby

TFGM_BASE_URL = "https://tfgm.com"
PARK_AND_RIDE_BASE_URL = TFGM_BASE_URL + "/public-transport/park-and-ride"


class ParkAndRideLocation(object):

    __slots__ = ["name", "latitude", "longitude", "transport_mode", "url", "address", "opening_times", "capacity",
                 "cost", "overnight_parking"]

    def __str__(self):
        return f"Name: {self.name}; Latitude: {self.latitude}; Longitude: {self.longitude}; " \
               f"Transport Mode: {self.transport_mode}; URL: {self.url}; Address: {self.address}; " \
               f"Opening Times: {self.opening_times}; Capacity: {self.capacity}; Cost: {self.cost}; " \
               f"Overnight Parking: {self.overnight_parking};"


def fetch_park_and_ride_locations():
    directory_page = BeautifulSoup(requests.get(PARK_AND_RIDE_BASE_URL).text, "html.parser")
    location_list_items = directory_page.find("div", attrs={"ng-controller": "ParkAndRideController"}).find_all("li")
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


def extract_address(details_div):
    return details_div.find("div").get_text(", ")


def extract_opening_times(details_div):
    opening_times = []
    for row in details_div.find_all("tr"):
        day = row.find("td", attrs={"opening-times-day"}).text.rstrip(":")
        times = row.find("td", attrs={"opening-times-time"}).text
        opening_times.append({day: times})
    return opening_times


def extract_capacity(details_div):
    return ""


def extract_cost(details_div):
    return ""


def extract_overnight_parking(details_div):
    return ""


def enrich_location(location: ParkAndRideLocation):
    location_page = BeautifulSoup(requests.get(TFGM_BASE_URL + location.url).text, "html.parser")
    details_div = location_page.find("div", attrs={"class", "park-and-ride-location"})
    location.address = extract_address(details_div)
    location.opening_times = extract_opening_times(details_div)
    location.capacity = extract_capacity(details_div)
    location.cost = extract_cost(details_div)
    location.overnight_parking = extract_overnight_parking(details_div)


def split_tag_list_on_hr(details_div):
    children = [child for child in details_div.children]
    return [list(group) for k, group in groupby(children, lambda x: x.name == "hr") if not k]


def main():
    locations = fetch_park_and_ride_locations()
    if not locations:
        logging.error(f"Failed to fetch Park and Ride locations from {PARK_AND_RIDE_BASE_URL}")
    for location in locations:
        enrich_location(location)
    for location in locations:
        print(location)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        handlers=[logging.StreamHandler(), logging.FileHandler('tfgmParkAndRideDetailsScraper.log')])
    main()
