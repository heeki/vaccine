import json
import os
import unittest
from availability import Availability
from datetime import datetime, timedelta

class Context:
    def __init__(self):
        self.function_version = "$LATEST"
        self.aws_request_id = "be6a8229-532d-4294-8d2c-ea721871ea36"

class TestAvailability(unittest.TestCase):
    config = {}

    @classmethod
    def setUpClass(cls):
        with open("etc/environment.json") as f:
            cls.config = json.load(f)
        # os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "test"
        os.environ["TOPIC"] = cls.config["Fn"]["TOPIC"]
        os.environ["TABLE"] = cls.config["Fn"]["TABLE"]
        cls.av = Availability()
        cls.av.logging = False
        cls.av.pull_config()
        cls.user = "heeki"
        cls.store = "cvs"
        cls.notification = {
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
        cls.context = Context()

    def test_notify(self):
        actual = self.av.notify(self.user, self.store, self.notification)
        # expected = "\n".join(["Vaccine availability at {} ({}) for {}.".format(notifications["store"], location) for location in notifications["availability_at"]])
        expected = """Vaccine availability at CVS (BROWNS MILLS) for heeki.
Vaccine availability at CVS (ELIZABETH) for heeki.
Vaccine availability at CVS (ENGLEWOOD) for heeki.
Vaccine availability at CVS (EWING) for heeki.
Vaccine availability at CVS (GIBBSBORO) for heeki.
Vaccine availability at CVS (GLASSBORO) for heeki.
Vaccine availability at CVS (LAWRENCEVILE) for heeki.
Vaccine availability at CVS (LODI) for heeki.
Vaccine availability at CVS (LONG BRANCH) for heeki.
Vaccine availability at CVS (NORTH BRUNSWICK) for heeki.
Vaccine availability at CVS (NORTH PLAINFIELD) for heeki.
Vaccine availability at CVS (PENNSAUKEN) for heeki.
Vaccine availability at CVS (PLAINSBORO) for heeki.
Vaccine availability at CVS (TEANECK) for heeki.
Vaccine availability at CVS (WEST ORANGE) for heeki.
Vaccine availability at CVS (WILLINGBORO) for heeki."""
        self.assertEqual(actual["message"], expected)

    def test_set_notification_ttl(self):
        ts_shift = datetime.now() - timedelta(minutes=30)
        self.av.set_notification_ttl(self.user, self.store, ts_shift)
        actual = self.av.notify(self.user, self.store, self.notification)
        self.assertEqual(actual["count"], 16)
        ts_shift = datetime.now() - timedelta(minutes=5)
        self.av.set_notification_ttl(self.user, self.store, ts_shift)
        actual = self.av.notify(self.user, self.store, self.notification)
        self.assertEqual(actual["count"], 0)

    def test_check_store(self):
        self.av.check_stores()
        actual = self.av.check_users()
        expected = [{"user": "heeki", "availability": [{"store": "CVS", "availability_at": []}, {"store": "RiteAid", "availability_at": []}]}, {"user": "test", "availability": [{"store": "CVS", "availability_at": []}, {"store": "RiteAid", "availability_at": []}]}]
        self.assertEqual(actual, expected)

    def test_put_emf(self):
        self.av.check_stores()
        actual = self.av.check_users()
        for item in actual:
            actual = self.av.put_emf(self.context, item["user"], item["availability"])
            self.assertEqual("_aws" in actual, True)

if __name__ == "__main__":
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestAvailability('test_notify'))
    suite.addTest(TestAvailability('test_set_notification_ttl'))
    suite.addTest(TestAvailability('test_check_store'))
    suite.addTest(TestAvailability('test_put_emf'))
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    runner.run(suite)
