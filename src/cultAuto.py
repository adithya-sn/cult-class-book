import sys

import requests
from urllib3.util import Retry


class cultAuto:
    def __init__(self, at: str, st: str, deviceId: str):
        self.deviceId = deviceId
        retry_strat = Retry(total=3, backoff_factor=0.5)
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strat)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        ## Build headers
        self.headers = {"cookie": f"st={st};at={at};deviceId={deviceId}"}

    def get_cult_centres(
        self,
        area_primary_str: str = "",
        area_secondary_str: str = "",
        centre_id_max: int = 100,
    ):
        """
        Get all Cult fit centres in your city
        It's stored as cityName/cityId
        """
        ## Initialize vars to store the ids
        area_primary_data, area_secondary_data = {}, {}
        area_primary_found = area_secondary_found = False
        centres_url = "https://www.cult.fit/api/cult/classes?center"
        centre_id = 1
        while True:
            # print(centre_id)
            response = self.session.get(
                f"{centres_url}={centre_id}", headers=self.headers
            )
            # print(f"{centre_id}: {response.json()['title']}")
            if (
                area_primary_str.lower() in response.json()["title"].lower()
                and not area_primary_found
            ):
                area_primary_found = True
                area_primary_data = response.json()
            if (
                area_secondary_str.lower() in response.json()["title"].lower()
                and not area_secondary_found
            ):
                area_secondary_found = True
                area_secondary_data = response.json()
            ## Increment and break
            if (
                area_primary_found and area_secondary_found
            ) or centre_id == centre_id_max + 1:
                break
            centre_id += 1
        ## Decide on data to send
        if area_primary_found and area_secondary_found:
            return [area_primary_data, area_secondary_data]
        elif area_primary_found:
            return [area_primary_data, None]
        elif area_secondary_found:
            return [None, area_secondary_data]
        else:
            print(f"Centre data not found.")
            return [None, None]

    def book_class(self, class_id: int):
        booking_url = f"https://www.cult.fit/api/cult/class/{class_id}/book"
        response = self.session.post(f"{booking_url}", headers=self.headers)
        print(f"Status: {response.status_code} and Response: {response.text}")
        return response.status_code

    def book_class_decision(
        self,
        centre_preference: tuple,
        booking_class: str = "HRX WORKOUT",
        time_preference: list = ["18:00:00", "19:00:00"],
    ):
        """
        Book Cult class on the latest available perference
        """
        class_booked = False
        primary_centre_clean: dict = {}
        secondary_centre_clean: dict = {}
        centre_data_primary, centre_data_secondary = self.get_cult_centres(
            centre_preference[0], centre_preference[1]
        )
        ## Exit if no centre data
        if not centre_data_primary and not centre_data_secondary:
            print("Centre data missing, exiting.")
            sys.exit(1)
        ## Go through both the centres and build clean, consumable data from it
        if centre_data_primary:
            ## Clean the data returned
            for centre_time_slot in centre_data_primary["classByDateList"][-1][
                "classByTimeList"
            ]:
                ## If multiple activities in each time slot
                for activity in centre_time_slot["classes"]:
                    if (
                        activity["workoutName"] == booking_class
                        and activity["availableSeats"] > 0
                    ):
                        primary_centre_clean[centre_time_slot["id"]] = activity["id"]
        if centre_data_secondary:
            ## Clean the data returned
            for centre_time_slot in centre_data_secondary["classByDateList"][-1][
                "classByTimeList"
            ]:
                ## If multiple activities in each time slot
                for activity in centre_time_slot["classes"]:
                    if (
                        activity["workoutName"] == booking_class
                        and activity["availableSeats"] > 0
                    ):
                        secondary_centre_clean[centre_time_slot["id"]] = activity["id"]

        ## Now to check preferred centres and book
        if primary_centre_clean:
            ## Iterate through the time slots
            for time_slot in time_preference:
                if time_slot in primary_centre_clean:
                    response = self.book_class(primary_centre_clean[time_slot])
                    if response >= 200 and response < 300:
                        print(f"Class booked")
                        class_booked = True
                        break
        ## Secondary centre booking
        if secondary_centre_clean and not class_booked:
            ## Iterate through the time slots
            for time_slot in time_preference:
                if time_slot in secondary_centre_clean:
                    response = self.book_class(secondary_centre_clean[time_slot])
                    if response >= 200 and response < 300:
                        print(f"Class booked")
                        class_booked = True
                        break
        if not class_booked:
            print(f"Class not booked :/")
