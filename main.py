import logging
import requests

from bs4 import BeautifulSoup

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


def extract_address(div):
    return div.get_text(", ")


def extract_opening_times(div):
    return ""


def extract_capacity(div):
    return ""


def extract_cost(div):
    return ""


def extract_overnight_parking(div):
    return ""


def enrich_location(location: ParkAndRideLocation):
    details_map = fetch_detail_divs(location)
    if "Address" in details_map:
        location.address = extract_address(details_map["Address"])
    if "Opening times" in details_map:
        location.opening_times = extract_opening_times(details_map["Opening times"])
    if "Spaces" in details_map:
        location.capacity = extract_capacity(details_map["Spaces"])
    if "Charges" in details_map:
        location.cost = extract_cost(details_map["Charges"])
    if "Other information" in details_map:
        location.overnight_parking = extract_overnight_parking(details_map["Other information"])


def fetch_detail_divs(location):
    location_page = BeautifulSoup(requests.get(TFGM_BASE_URL + location.url).text, "html.parser")
    details_map = pair_divs_with_associated_headers(location_page)
    return details_map


def pair_divs_with_associated_headers(location_page):
    details_div = location_page.find("div", attrs={"class": "park-and-ride-location"})
    headers = [header.text for header in details_div.find_all("h3")]
    inner_divs = details_div.find_all("div")
    details_map = {}
    for i in range(len(headers)):
        details_map[headers[i]] = inner_divs[i]
    return details_map


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
