import itertools
import logging
from itertools import groupby

import requests
from bs4 import BeautifulSoup, Tag

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
    location.url = TFGM_BASE_URL + location_list_item.find("a").get("href")
    return location


def extract_address(content_element):
    return content_element.get_text(", ").strip()


def extract_opening_times(content_element):
    opening_times = []
    for row in content_element.find_all("tr"):
        day = row.find("td", attrs={"opening-times-day"}).text.rstrip(":")
        times = row.find("td", attrs={"opening-times-time"}).text
        opening_times.append({day: times})
    return opening_times


def extract_capacity(content_element):
    return content_element.get_text().strip()


def extract_cost(content_element):
    return content_element.get_text().strip()


def extract_overnight_parking(content_element):
    return ": Yes" in content_element.get_text()


def fetch_headers_and_content(location_page):
    """
    Map the content element for an attribute of a location page against its associated lowercase header.
    For example "Address" and "Opening times"
    :param location_page: BeautifulSoup object for a parsed Park and Ride location page.
    :return: A map in the form {HEADER: CONTENT_ELEMENT}
    """
    details_div = location_page.find("div", attrs={"class", "park-and-ride-location"})
    child_tags = [child for child in details_div.children if isinstance(child, Tag)]
    grouped_tags_raw = [list(y) for x, y in itertools.groupby(child_tags, lambda z: z.name == "hr") if not x]
    grouped_tags = [grouped_tags for grouped_tags in grouped_tags_raw if len(grouped_tags) == 2]
    return {header_tag.text.lower(): content_tag for (header_tag, content_tag) in grouped_tags}


def enrich_location(location: ParkAndRideLocation):
    location_page = BeautifulSoup(requests.get(location.url).text, "html.parser")
    location_content = fetch_headers_and_content(location_page)
    location.address = extract_address(location_content["address"])
    location.opening_times = extract_opening_times(location_content["opening times"])
    location.capacity = extract_capacity(location_content["spaces"])
    location.cost = extract_cost(location_content["charges"])
    location.overnight_parking = extract_overnight_parking(location_content["other information"])


def split_tag_list_on_hr(details_div):
    children = [child for child in details_div.children]
    return [list(group) for k, group in groupby(children, lambda x: x.name == "hr") if not k]


def main():
    locations = fetch_park_and_ride_locations()
    if not locations:
        logging.error(f"Failed to fetch Park and Ride locations from {PARK_AND_RIDE_BASE_URL}")
    for location in locations:
        enrich_location(location)
        print(location)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        handlers=[logging.StreamHandler(), logging.FileHandler('tfgmParkAndRideDetailsScraper.log')])
    main()
