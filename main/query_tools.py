from collections import defaultdict
from main.models import SessionLocal, Pitch, Pitcher


# Class takes in pitcher name then returns dic of game pitch type lists
class PitcherQuery:
    def __init__(self, pitcherName):
        self.pitcher_names = self.get_pitcher_name(pitcherName)
        self.query_results = self.query_for_pitches()

    def query_for_pitches(self) -> defaultdict:
        session = SessionLocal()
        pitch_query = (
            session.query(Pitch)
            .join(Pitcher, Pitch.pitcher_id == Pitcher.pitcher_id)
            .filter(Pitcher.pitcher_name_normalized.ilike(
                self.pitcher_names["pitcher_name_normalized"]
            ))
            .order_by(Pitch.game_id.desc(), Pitch.pitch_number.asc())
        )
        pitch_dic = defaultdict(list[str])
        for entry in pitch_query:
            pitch_dic[str(entry.game_id)].append(entry.pitch_type)

        session.close()
        return pitch_dic

    def get_pitcher_name(self, p_name):
        session = SessionLocal()
        pitcher_query = (
            session.query(Pitcher)
            .filter(Pitcher.pitcher_name_normalized.ilike(p_name))
        )
        name_dict = {}
        for entry in pitcher_query:
            name_dict["pitcher_name"] = entry.pitcher_name
            name_dict["pitcher_name_normalized"] = (
                entry.pitcher_name_normalized
            )

        session.close()
        return name_dict
