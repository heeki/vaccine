import json

class Store:
    def __init__(self):
        self.name = ""
        self.data = {}
        self.preferences = {}
        self.debug = False

    def set_data(self, payload):
        self.data = payload

    def set_preferences(self, payload):
        self.preferences = payload

class CVS(Store):
    def __init__(self, debug=False):
        super().__init__()
        self.name = "CVS"
        self.debug = debug

    def check_availability(self, user):
        availability = []
        for slot in self.data["responsePayloadData"]["data"]["NJ"]:
            if (slot["status"] != "Fully Booked"):
                availability.append(slot["city"])
                print("({}) Vaccine availability at {}".format(self.name, slot["city"]))
            elif self.debug:
                print("({}}) No vaccine availability at {}".format(self.name, slot["city"]))
        availability = list(filter(lambda x: x in self.preferences[user]["cvs"].keys(), availability))
        result = {
            "store": self.name,
            "availability_at": availability
        }
        return result

class RiteAid(Store):
    def __init__(self, debug=False):
        super().__init__()
        self.name = "RiteAid"
        self.debug = debug

    def check_availability(self, user, locations):
        availability = []
        for location in locations:
            if (self.data[location]["Data"]["slots"]["1"] or self.data[location]["Data"]["slots"]["2"]):
                availability.append(location)
                print("({}}) Vaccine availability at {}".format(self.name, location))
            elif self.debug:
                print("({}}) No vaccine availability at {}".format(self.name, location))
        availability = list(filter(lambda x: x in self.preferences[user]["riteaid"].keys(), availability))
        result = {
            "store": self.name,
            "availability_at": availability
        }
        return result

class Walgreens(Store):
    def __init__(self, debug=False):
        super().__init__()
        self.name = "Walgreens"
        self.debug = debug

    def check_availability(self, user):
        availability = []
        availability = list(filter(lambda x: x in self.preferences[user]["walgreens"].keys(), availability))
        result = {
            "store": self.name,
            "availability_at": availability
        }
        return result
