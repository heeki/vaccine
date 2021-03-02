import json
import os
import unittest
from availability import Availability
from datetime import datetime, timedelta

class TestAvailability(unittest.TestCase):
    config = {}

    @classmethod
    def setUpClass(cls):
        with open("etc/environment.json") as f:
            cls.config = json.load(f)
        # os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "test"
        os.environ["TOPIC"] = cls.config["Fn"]["TOPIC"]
        os.environ["TABLE"] = cls.config["Fn"]["TABLE"]

    def test_notify(self):
        av = Availability()
        av.pull_users()
        user = "heeki"
        store = "cvs"
        notifications = {
            "store": "CVS",
            "availability_at": [
                "BROWNS MILLS",
                "ELIZABETH",
                "ENGLEWOOD",
                "EWING",
                "GIBBSBORO",
                "GLASSBORO",
                "LAWRENCEVILE",
                "LODI",
                "LONG BRANCH",
                "NORTH BRUNSWICK",
                "NORTH PLAINFIELD",
                "PENNSAUKEN",
                "PLAINSBORO",
                "TEANECK",
                "WEST ORANGE",
                "WILLINGBORO"
            ]
        }
        actual = av.notify(user, store, notifications)
        # expected = "\n".join(["Vaccine availability for {} at {}.".format(notifications["store"], location) for location in notifications["availability_at"]])
        expected = """Vaccine availability for CVS at BROWNS MILLS.
Vaccine availability for CVS at ELIZABETH.
Vaccine availability for CVS at ENGLEWOOD.
Vaccine availability for CVS at EWING.
Vaccine availability for CVS at GIBBSBORO.
Vaccine availability for CVS at GLASSBORO.
Vaccine availability for CVS at LAWRENCEVILE.
Vaccine availability for CVS at LODI.
Vaccine availability for CVS at LONG BRANCH.
Vaccine availability for CVS at NORTH BRUNSWICK.
Vaccine availability for CVS at NORTH PLAINFIELD.
Vaccine availability for CVS at PENNSAUKEN.
Vaccine availability for CVS at PLAINSBORO.
Vaccine availability for CVS at TEANECK.
Vaccine availability for CVS at WEST ORANGE.
Vaccine availability for CVS at WILLINGBORO."""
        self.assertEqual(actual["message"], expected)

    def test_notification_ttl(self):
        av = Availability()
        av.pull_users()
        user = "heeki"
        store = "cvs"
        notifications = {
            "store": "CVS",
            "availability_at": [
                "BROWNS MILLS",
                "ELIZABETH",
                "ENGLEWOOD",
                "EWING",
                "GIBBSBORO",
                "GLASSBORO",
                "LAWRENCEVILE",
                "LODI",
                "LONG BRANCH",
                "NORTH BRUNSWICK",
                "NORTH PLAINFIELD",
                "PENNSAUKEN",
                "PLAINSBORO",
                "TEANECK",
                "WEST ORANGE",
                "WILLINGBORO"
            ]
        }
        actual = av.notify(user, store, notifications)
        self.assertEqual(actual["count"], 16)
        ts_shift = datetime.now() - timedelta(minutes=5)
        av.set_notification_ttl(user, store, ts_shift)
        actual = av.notify(user, store, notifications)
        self.assertEqual(actual["count"], 0)

if __name__ == "__main__":
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestAvailability('test_notify'))
    suite.addTest(TestAvailability('test_notification_ttl'))
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    runner.run(suite)
