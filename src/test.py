import json
import unittest
from availability import Availability

class TestAvailability(unittest.TestCase):
    @classmethod
    def setupClass(cls):
        print("initialization")

    def test_notify(self):
        av = Availability()
        user = "test"
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
        actual = av.notify(user, notifications)
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
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestAvailability('test_notify'))
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    runner.run(suite)
