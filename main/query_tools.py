from main.models import SessionLocal, Pitch, Pitcher
from collections import defaultdict


# Class takes in pitcher name then returns dic of game pitch type lists
class PitcherQuery:
    def __init__(self, pitcherName):
        self.pitcher_name = pitcherName
        self.query_results = self.query_for_pitches()

    def query_for_pitches(self) -> defaultdict:
        session = SessionLocal()
        query = (
            session.query(Pitch)
            .join(Pitcher, Pitch.pitcher_id == Pitcher.pitcher_id)
            .filter(Pitcher.pitcher_name == self.pitcher_name)
            .order_by(Pitch.game_id.desc(), Pitch.pitch_number.asc())
        )
        pitch_dic = defaultdict(list[str])
        for entry in query:
            pitch_dic[str(entry.game_id)].append(entry.pitch_type)

        session.close()
        return pitch_dic
