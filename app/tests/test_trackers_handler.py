from email_utils import handlers as trackers_handler


def test_returns_correct_tracker_for_domain():
    result = trackers_handler.check_is_url_a_tracker("https://trk.365offers.trade/test")

    assert result is not None, "Result should be a dict"
    assert result["name"] == "365offers"


def test_returns_correct_tracker_for_glob():
    result = trackers_handler.check_is_url_a_tracker("https://market.clio.com/trkabc")

    assert result is not None, "Result should be a dict"
    assert result["name"] == "Clio"


def test_returns_correct_tracker_for_regex():
    result = trackers_handler.check_is_url_a_tracker(
        "https://cloudhq-mkt3.net/mail_track?test=abc"
    )

    assert result is not None, "Result should be a dict"
    assert result["name"] == "cloudHQ"


def test_returns_none_if_no_trackers_available():
    result = trackers_handler.check_is_url_a_tracker(
        "https://www.thisurldoesnotexistAASdasdasdasdasda.com"
    )

    assert result is None, "Result should be None"
