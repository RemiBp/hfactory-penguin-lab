from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_app_and_filter_interactions():
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    assert not app.exception
    assert app.metric[0].value == "344"
    model_mae = app.metric[3].value
    app.multiselect(key="species").set_value(["Gentoo"]).run()
    assert not app.exception
    assert app.metric[0].value == "124"
    assert app.metric[3].value == model_mae
    app.multiselect(key="species").set_value([]).run()
    assert not app.exception
    assert app.metric[0].value == "0"
    assert "No observations" in app.info[0].value
    app.multiselect(key="species").set_value(["Adelie"]).run()
    app.multiselect(key="islands").set_value(["Dream"]).run()
    app.multiselect(key="years").set_value([2007]).run()
    assert not app.exception
    assert int(app.metric[0].value) > 0
