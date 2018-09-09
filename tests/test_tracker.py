import time
from unittest import TestCase

from dj_request_correlation.tracker import Tracker


class TestTracker(TestCase):
    def test_create_tracker(self,):
        tracker = Tracker()
        with tracker:
            time.sleep(2)
            with tracker.track("sub") as child_tracker:
                time.sleep(2)

        tracker.log
