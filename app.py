from flask import (
            Flask,
            render_template,
            request,
            url_for
        )
from main.markov import MarkovChain
from main.query_tools import PitcherQuery

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get-fsm", methods=["GET"])
def get_pitcher_diagram():

    try:
        p_name = request.args.get("pitcher-name")
        p_query = PitcherQuery(p_name)
        p_names = p_query.pitcher_names
        norm_name = p_names["pitcher_name_normalized"]

        name = p_names["pitcher_name"]
        m_chain = MarkovChain(p_query.query_results)
        f_path = m_chain.save_state_diagram(norm_name, name)
        f_path = f_path.split("static/")[1]
        return (
            f'<img src="{url_for("static", filename=f"{f_path}")}" '
            '"style="max-width:100%;" id="pitch-fsm-result">'
        )

    except (KeyError):
        print(f"What's wrong with you! {p_name} is not an MLB pitcher!!")
        return "<div></div>"


if __name__ == "__main__":
    app.run(debug=True)
