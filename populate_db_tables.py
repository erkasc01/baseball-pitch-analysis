from main.baseball_db_generator import (
    GameUrlRetriever,
    GameUrlProcessor,
    populate_pitchers_table
)
from main.models import SessionLocal

db = SessionLocal()
# Get urls and prep info for the url processor
url = ("https://baseballsavant.mlb.com/statcast_search?hfPT=&hfAB=&hfGT=R%7C&h"
       "fPR=&hfZ=&hfStadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea=2024%7C&hfS"
       "it=&player_type=pitcher&hfOuts=&hfOpponent=&pitcher_throws=&batter_sta"
       "nds=&hfSA=&game_date_gt=&game_date_lt=&hfMo=&hfTeam=&home_road=&hfRO=&"
       "position=&hfInfield=&hfOutfield=&hfInn=&hfBBT=&hfFlag=&metric_1=&group"
       "_by=name-date&min_pitches=0&min_results=0&min_pas=0&sort_col=pitches&p"
       "layer_event_sort=api_p_release_speed&sort_order=desc")

# Hit the URL and extract all of the pitchers
populate_pitchers_table(url)

# Get list of game URLs and extract pitch data
game_urls = GameUrlRetriever(url)
gup = GameUrlProcessor(game_urls.urls)
gup.process_urls()
