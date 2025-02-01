from bs4 import BeautifulSoup
import requests
from main.models import Pitch, Pitcher, SessionLocal
import concurrent.futures
import time
from unicodedata import normalize, combining

"""
This file contains the necessary classes to populate the baseball db

So far inside the db there is a pitcher table and a pitch table
"""


def unaccent(name_query):
    return (
            "".join(
                    c for c in normalize("NFKD", name_query)
                    if not combining(c)
                )
        )


def add_normalized_names():
    session = SessionLocal()
    query = session.query(Pitcher).all()
    for pitcher in query:
        normalized_name = unaccent(pitcher.pitcher_name.lower())
        pitcher.pitcher_name_normalized = normalized_name
    session.commit()
    session.close()
    print("INFO: Pitcher names normalized and db session closed.")


# Function to parse out pitcher names and IDs from main page
def populate_pitchers_table(base_url: str):
    db = SessionLocal()

    base_url_results = base_url + "#results"
    res = requests.get(url=base_url_results)

    souped_page = SoupFactory([res]).convert_to_soup()[0]
    pitcher_tds = souped_page.find_all("td", class_="player_name")
    count = 0
    for entry in pitcher_tds:
        pitcher_id_str = str(entry).split("id_")[1].split("\"")[0]

        pitcher_id_int = int(pitcher_id_str)

        existing_pitcher = db.query(Pitcher).filter_by(
            pitcher_id=pitcher_id_int).first()
        if not existing_pitcher:
            pitcher_name = str(entry).split(">\n")[1].split(" <")[0].split(",")
            stripped_name = [x.strip() for x in pitcher_name]
            pitcher_name_str = f"{stripped_name[1]} {stripped_name[0]}"
            print((
                f"Adding pitcher {pitcher_name_str} with id "
                f"{pitcher_id_int} to db"
            ))
            new_pitcher = Pitcher(
                                pitcher_name=pitcher_name_str,
                                pitcher_id=pitcher_id_int
                                )
            db.add(new_pitcher)
            db.commit()
            count += 1

        else:
            continue
    print(f"Finished adding {count} players to db. Closing connection now")
    db.close()


# Class that takes requests from baseball savant and preps them to be fed into
# parser
class SoupFactory:
    def __init__(self, reqs: list[requests.models.Response]):
        self.requests = reqs
        self.num_pages = len(reqs)
        self.valid_requests = self.check_response_codes()

    def check_response_codes(self):
        valid_requests = []
        for idx, req in enumerate(self.requests):
            try:
                if req.status_code == 200:
                    valid_requests.append(req)
            except ValueError:
                print((
                    f"Warning: No status code found for request {idx} with"
                    f" status code {req.status_code}"
                ))
        return valid_requests

    def convert_to_soup(self):
        souped_requests = []
        for idx, req in enumerate(self.valid_requests):
            try:
                text = req.text
                html_page = BeautifulSoup(text, "html.parser")
                souped_requests.append(html_page)
            except ValueError:
                print(f"Warn: Cannot parse text for request {idx}")
        if len(souped_requests) == 0:
            print((
                "Error: No requests could be parsed. "
                "Please ensure list of requests is non-empty."
            ))
            return
        else:
            return souped_requests


# This is expecting the main pitch page as an input
class GameUrlRetriever:
    def __init__(self, base_url):
        self.base_url = base_url
        self.main_page = self.get_main_page()
        self.urls = self.retrieve_urls(self.main_page)

    def get_main_page(self):
        base_url_results = self.base_url + "#results"
        result = [requests.get(base_url_results)]
        main_page = SoupFactory(result).convert_to_soup()
        return main_page

    def retrieve_urls(self, main_page):
        # Exract all trs which contain the information we need to make API
        # calls to the game pitch results
        pitcher_trs = self.main_page[0].find_all(
            "tr",
            class_="search_row default-table-row"
            )
        game_urls = []
        for entry in pitcher_trs:
            try:
                player_name_date = (
                            str(entry)
                            .split("player_name-date_")[1]
                            .split("\"")[0]
                        )
                player_name_date = player_name_date.split("_")
                player_id, date, game_id = (
                                player_name_date[0],
                                player_name_date[1],
                                player_name_date[2]
                            )
                game_url = self.base_url + (
                                f"&type=details&player_id="
                                f"{player_id}&ep_game_date="
                                f"{date}&ep_game_pk={game_id}"
                            )
                game_urls.append({
                            "game_url": game_url,
                            "player_id": player_id,
                            "game_id": game_id
                        })
            except ValueError:
                print((
                    "Warn: failed to parse player, date, and game"
                    " information from entry"
                ))
        return game_urls


# Class to take in the list of URLs and process them in parallel
class GameUrlProcessor:
    def __init__(self, game_dic_list: list):
        self.game_list = game_dic_list

    def process_urls(self):
        db = SessionLocal()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    self.fetch_url_and_extract_pitch,
                    game): game for game in self.game_list
                }
        for future in futures:
            for entry in future.result():
                if type(entry) is Pitch:
                    new_pitch = entry
                    db.add(new_pitch)

        db.commit()
        db.close()
        return futures

    def fetch_url_and_extract_pitch(self, game_info):
        try:
            time.sleep(0.5)
            response = requests.get(game_info["game_url"])
            html_page = SoupFactory([response]).convert_to_soup()
            trs = html_page[0].find_all("tr")[1:-1]
            trs.reverse()
            pitcher_id_int = int(game_info["player_id"])
            game_id_int = int(game_info["game_id"])
            results = []
            for idx, tr in enumerate(trs):
                pitch_data = []
                for elem in tr:
                    inner_text = elem.text.strip()
                    if inner_text != "":
                        pitch_data.append(inner_text)
                new_pitch = self.parse_pitch_info(
                                            pitch_data,
                                            pitcher_id_int,
                                            game_id_int,
                                            idx
                                        )
                results.append(new_pitch)
            return results

        except Exception as e:
            return f"Error: {e}"

    def parse_pitch_info(self, pitch_data, pitcher_id_int, game_id_int, idx):
        try:
            pitch_number_int = idx
            pitch_date_str = pitch_data[0]
            pitch_type_str = pitch_data[1]
            pitch_mph_flo = float(pitch_data[2])
            pitch_result_str = pitch_data[-2]
            pa_result_str = pitch_data[-1]
            if len(pitch_data) == 14:
                spin_rate_int = int(pitch_data[3])
            # Sometimes the spin rate is missing. This will account for that
            elif len(pitch_data) == 13:
                spin_rate_int = 0

            new_pitch = Pitch(
                    pitcher_id=pitcher_id_int,
                    game_id=game_id_int,
                    pitch_number=pitch_number_int,
                    pitch_type=pitch_type_str,
                    pitch_result=pitch_result_str,
                    pa_result=pa_result_str,
                    spin_rate=spin_rate_int,
                    pitch_mph=pitch_mph_flo,
                    pitch_date=pitch_date_str
                )
        except ValueError:
            print(pitch_data)
            print("Error parsing pitch data. Skipping row")
        return new_pitch
