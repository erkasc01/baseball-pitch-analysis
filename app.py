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
    pname = request.args.get("pitcher-name")
    pquery = PitcherQuery(pname)
    try:
        mchain = MarkovChain(pquery.query_results)
        fpath = mchain.save_state_diagram(pname)
        fpath = fpath.split("static/")[1]
        return f'<img src="{url_for("static", filename=f"{fpath}")}" alt="State Diagram for {pname}" style="max-width:100%;">'

    except ValueError:
        print(f"What's wrong with you! {pname} is not an MLB pitcher!!")
        return "<div></di>"


if __name__ == "__main__":
    app.run(debug=True)
