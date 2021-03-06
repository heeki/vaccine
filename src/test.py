import json
import os
import unittest
from lib.availability import Availability
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
        cls.includes = range(5)
        cls.events = []
        for event in cls.includes:
            with open("etc/test_{}.json".format(event)) as f:
                cls.events.append(json.load(f))
        cls.context = Context()

    def test_notify(self):
        actual = self.av.notify(self.user, self.store, self.events[0])
        expected = "Vaccine availability at CVS (2257 Us Hwy 1, South North Brunswick, NJ 08902) for heeki."
        self.assertEqual(actual["message"], expected)
        self.av.data = self.events[2]
        actual = self.av.check_user(self.user,)
        self.assertTrue(len(actual["availability"][0]["availability_at"]) == 1)
        self.av.data = self.events[3]
        actual = self.av.check_user(self.user,)
        self.assertTrue(len(actual["availability"][0]["availability_at"]) == 0)

    def test_set_notification_ttl(self):
        ts_shift = datetime.now() - timedelta(minutes=30)
        self.av.set_notification_ttl(self.user, self.store, ts_shift, offline=True)
        actual = self.av.notify(self.user, self.store, self.events[1])
        self.assertEqual(actual["count"], 1)
        ts_shift = datetime.now() - timedelta(minutes=5)
        self.av.set_notification_ttl(self.user, self.store, ts_shift, offline=True)
        actual = self.av.notify(self.user, self.store, self.events[1])
        self.assertEqual(actual["count"], 0)

    def test_check_store(self):
        self.av.check_stores()
        response = self.events[4]
        included = ["heeki", "test"]
        actual = []
        for item in response:
            if item["user"] in included:
                actual.append(item)
        expected = [{"user": "heeki", "availability": [{"store": "CVS", "availability_at": []}, {"store": "RiteAid", "availability_at": []}]}, {"user": "test", "availability": [{"store": "CVS", "availability_at": []}, {"store": "RiteAid", "availability_at": []}]}]
        self.assertEqual(actual, expected)

    def test_put_emf(self):
        self.av.check_stores()
        actual = self.events[4]
        for item in actual:
            actual = self.av.put_emf(self.context, item["user"], item["availability"])
            self.assertEqual(len(actual["_aws"]["CloudWatchMetrics"][0]["Metrics"]), 2)
            self.assertEqual(actual["cvs"], 0)
            self.assertEqual(actual["riteaid"], 0)

if __name__ == "__main__":
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestAvailability('test_notify'))
    suite.addTest(TestAvailability('test_set_notification_ttl'))
    suite.addTest(TestAvailability('test_check_store'))
    suite.addTest(TestAvailability('test_put_emf'))
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    runner.run(suite)
