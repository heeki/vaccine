import json

class Store:
    def __init__(self):
        self.name = ""
        self.data = {}
        self.preferences = {}
        self.debug = False

    def set_data(self, payload):
        self.data = payload

    def set_preferences(self, payload, store):
        for user in payload:
            if user not in self.preferences:
                self.preferences[user] = {}
            self.preferences[user] = {k:v for (k,v) in payload[user][store].items()}

class CVS(Store):
    def __init__(self, debug=False):
        super().__init__()
        self.name = "CVS"
        self.debug = debug

    def set_preferences(self, payload):
        return super().set_preferences(payload, "cvs")

    def check_availability(self, user):
        availability = []
        for slot in self.data["responsePayloadData"]["data"]["NJ"]:
            if (slot["status"] != "Fully Booked"):
                availability.append(slot["city"])
        availability = list(filter(lambda x: x in self.preferences[user].keys(), availability))
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

    def set_preferences(self, payload):
        return super().set_preferences(payload, "riteaid")

    def check_availability(self, user, locations):
        availability = []
        for location in locations:
            try:
                if self.data is not None and self.data[location] is not None and (self.data[location]["Data"]["slots"]["1"] or self.data[location]["Data"]["slots"]["2"]):
                    availability.append(location)
            except TypeError as e:
                print(e)
                print(json.dumps(self.data))
        availability = list(filter(lambda x: x in self.preferences[user].keys(), availability))
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

    def set_preferences(self, payload):
        return super().set_preferences(payload, "walgreens")

    def check_availability(self, user):
        availability = []
        availability = list(filter(lambda x: x in self.preferences[user].keys(), availability))
        result = {
            "store": self.name,
            "availability_at": availability
        }
        return result
