class IncidentTracker:
    """Decides when to open or resolve an incident from a stream of check results.

    Opens after `threshold` consecutive failures, so one blip (for example a
    service still starting up) does not create an incident.
    """

    def __init__(self, threshold=3):
        self.threshold = threshold
        self.consecutive_failures = 0
        self.is_open = False

    def update(self, ok):
        """Returns "open", "resolve" or None."""
        if ok:
            self.consecutive_failures = 0
            if self.is_open:
                self.is_open = False
                return "resolve"
            return None
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.threshold and not self.is_open:
            self.is_open = True
            return "open"
        return None
