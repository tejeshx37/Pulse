from tracker import IncidentTracker


def test_single_failure_does_not_open():
    t = IncidentTracker(threshold=3)
    assert t.update(False) is None


def test_opens_after_threshold_consecutive_failures():
    t = IncidentTracker(threshold=3)
    assert t.update(False) is None
    assert t.update(False) is None
    assert t.update(False) == "open"


def test_success_resets_failure_count():
    t = IncidentTracker(threshold=3)
    t.update(False)
    t.update(False)
    t.update(True)
    assert t.update(False) is None


def test_does_not_open_twice():
    t = IncidentTracker(threshold=2)
    t.update(False)
    assert t.update(False) == "open"
    assert t.update(False) is None


def test_resolves_on_recovery():
    t = IncidentTracker(threshold=2)
    t.update(False)
    t.update(False)
    assert t.update(True) == "resolve"
    assert t.update(True) is None
