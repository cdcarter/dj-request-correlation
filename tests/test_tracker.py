import time
from unittest import TestCase

from dj_request_correlation.tracker import Tracker


class TestTracker(TestCase):
    def test_create_tracker(self,):
        tracker = Tracker()
        with tracker:
            time.sleep(2)
            with tracker.new_child("sub") as child_tracker:
                time.sleep(2)

        self.assertGreater(tracker.time, child_tracker.time)
