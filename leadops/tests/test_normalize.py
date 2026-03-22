from app.core.normalize import (
    classify_trigger,
    normalize_address,
    normalize_owner_name,
    owner_occupancy_proxy,
)


def test_normalize_owner_name():
    assert normalize_owner_name("Mark Johnson, Jr.") == "MARK JOHNSON JR"


def test_normalize_address():
    assert normalize_address("123 Main Street") == "123 MAIN ST"


def test_classify_trigger():
    assert classify_trigger("deed change") == "deed_change"
    assert classify_trigger("", "Building", "ADU") == "adu_permit"


def test_owner_occupancy_proxy():
    assert owner_occupancy_proxy("yes") == "owner_occupied"
    assert owner_occupancy_proxy("no") == "absentee"