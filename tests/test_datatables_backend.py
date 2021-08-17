import pytest
from flask import url_for

from registry.donor.models import DonorsOverview
from tests.fixtures import sample_of_rc

from .helpers import login


class TestDataTablesBackend:
    @pytest.mark.parametrize("limit", (5, 10, 20, 50))
    def test_json_backend_limit(self, user, testapp, limit):
        # This is very limited subset of what datatables frontend
        # sends to the backend but it's enough for the simple test.
        params = {
            "draw": "1",
            "order[0][column]": "0",
            "order[0][dir]": "asc",
            "start": "0",
            "length": str(limit),
            "search[value]": "",
            "search[regex]": "false",
        }
        login(user, testapp)
        res = testapp.get(url_for("donor.overview_data"), params=params)
        assert res.status_code == 200
        assert len(res.json["data"]) == limit

    @pytest.mark.parametrize("rodne_cislo", sample_of_rc(3))
    def test_json_backend_search(self, user, testapp, rodne_cislo):
        params = {
            "draw": "1",
            "order[0][column]": "0",
            "order[0][dir]": "asc",
            "start": "0",
            "length": "10",
            "search[value]": rodne_cislo,
            "search[regex]": "false",
        }
        login(user, testapp)
        res = testapp.get(url_for("donor.overview_data"), params=params)
        assert res.status_code == 200
        assert len(res.json["data"]) == 1
        assert res.json["data"][0]["rodne_cislo"] == rodne_cislo

    @pytest.mark.parametrize("direction", ("asc", "desc"))
    def test_json_backend_order(self, user, testapp, direction):
        params = {
            "draw": "1",
            "order[0][column]": "0",
            "order[0][dir]": direction,
            "start": "0",
            "length": "10",
            "search[value]": "",
            "search[regex]": "false",
        }
        login(user, testapp)
        res = testapp.get(url_for("donor.overview_data"), params=params)
        assert res.status_code == 200
        assert len(res.json["data"]) == 10

        do = DonorsOverview.query.order_by(
            getattr(DonorsOverview.rodne_cislo, direction)()
        ).limit(10)

        for index, donor in enumerate(do):
            assert res.json["data"][index]["rodne_cislo"] == donor.rodne_cislo