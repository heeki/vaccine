import argparse
import boto3
import json
import os
import sys
import urllib.request
from datetime import datetime

class Availability:
    def __init__(self, debug=False):
        self.debug = debug
        self.config = {
            "cvs": {},
            "riteaid": {},
            "user_preferences": {},
            "notification_ttl": {},
            "ttl_in_seconds": 600
        }
        if "TOPIC" in os.environ:
            self.topic = os.environ["TOPIC"]
        if "TABLE" in os.environ:
            self.table = os.environ["TABLE"]
        self.client_sns = boto3.client("sns")
        self.client_ddb = boto3.client("dynamodb")

    # internal data
    def get_users(self):
        return self.config["user_preferences"].keys()

    def set_config(self, config):
        self.config = config

    def set_notification_ttl(self, user, store, ts):
        if user not in self.config["notification_ttl"]:
            self.config["notification_ttl"][user] = {}
        self.config["notification_ttl"][user][store] = ts.isoformat()
        self.put_user(user)

    # data persistence
    def pull_store(self, store):
        response = self.client_ddb.get_item(
            TableName=self.table,
            Key={
                "user": {
                    "S": "_{}".format(store)
                }
            }
        )["Item"]
        self.config[store] = {
            "url": response["url"]["S"],
            "headers": json.loads(response["headers"]["S"])
        }

    def pull_users(self):
        response = self.client_ddb.scan(
            TableName=self.table
        )["Items"]
        for item in response:
            user = item["user"]["S"]
            if not user.startswith("_"):
                if user not in self.config["user_preferences"]:
                    self.config["user_preferences"][user] = {}
                self.config["user_preferences"][user] = json.loads(item["preferences"]["S"])
                if user not in self.config["notification_ttl"]:
                    self.config["notification_ttl"][user] = {}

    def pull_config(self):
        self.pull_store("cvs")
        self.pull_store("riteaid")
        self.pull_users()

    def put_user(self, user):
        payload = {
            "user": { "S": user }
        }
        if user in self.config["user_preferences"]:
            payload["preferences"] = { "S": json.dumps(self.config["user_preferences"][user]) }
        if user in self.config["notification_ttl"]:
            payload["notification_ttl"] = { "S": json.dumps(self.config["notification_ttl"][user]) }
        response = self.client_ddb.put_item(
            TableName=self.table,
            Item = payload
        )
        return response

    # notifications
    def send_sns(self, user, subject, message):
        if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
            self.client_sns.publish(
                TopicArn=self.topic,
                Subject=subject,
                Message=message,
                MessageAttributes={
                    "user": {
                        "DataType": "String",
                        "StringValue": user
                    }
                }
            )

    def notify(self, user, store, notifications):
        store = store.lower()
        subject = "Vaccination availability alert"
        count = len(notifications["availability_at"])
        if count == 0:
            message = "No vaccine availability at {}.".format(notifications["store"])
            # self.send_sns(user, subject, message)
        else:
            message = "\n".join(["Vaccine availability for {} at {}.".format(notifications["store"], location) for location in notifications["availability_at"]])
            ts_now = datetime.now()
            if user in self.config["notification_ttl"] and store in self.config["notification_ttl"][user]:
                ts_last = datetime.fromisoformat(self.config["notification_ttl"][user][store])
                ts_diff = ts_now - ts_last
                if ts_diff.total_seconds() > self.config["ttl_in_seconds"]:
                    self.send_sns(user, subject, message)
                    self.set_notification_ttl(user, store, ts_now)
                else:
                    count = 0
            else:
                self.send_sns(user, subject, message)
                self.set_notification_ttl(user, store, ts_now)
        print(message)
        output = {
            "count": count,
            "message": message
        }
        return output

    # external api calls
    def get_availability(self, url, headers):
        request = urllib.request.Request(url)
        request.add_header("user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36")
        for header in headers:
            request.add_header(header, headers[header])
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            print(e)
            sys.exit(1)

        if response.status == 200:
            return json.loads(response.read().decode('utf-8'))
        else:
            sys.exit(1)

    def check_cvs(self, user):
        locations = []
        baseurl = self.config["cvs"]["url"]
        headers = self.config["cvs"]["headers"]
        response = self.get_availability(baseurl, headers)
        for store in response["responsePayloadData"]["data"]["NJ"]:
            if (store["status"] != "Fully Booked"): 
                locations.append(store["city"])
                print("(CVS) Vaccine availability at {}".format(store["city"]))
            elif self.debug:
                print("(CVS) No vaccine availability at {}".format(store["city"]))
        output = {
            "store": "CVS",
            "availability_at": locations
        }
        self.notify(user, "cvs", output)
        return output

    def check_riteaid(self, user):
        locations = []
        baseurl = self.config["riteaid"]["url"]
        headers = self.config["riteaid"]["headers"]
        for store in self.config["user_preferences"][user]["riteaid"]:
            url = "{}{}".format(baseurl, store)
            location = self.config["user_preferences"][user]["riteaid"][store]
            response = self.get_availability(url, headers)
            if (response["Data"]["slots"]["1"] or response["Data"]["slots"]["2"]):
                locations.append(location)
                print("(RiteAid) Vaccine availability at {}".format(location))
            elif self.debug:
                print("(RiteAid) No vaccine availability at {}".format(location))
        output = {
            "store": "RiteAid",
            "availability_at": locations
        }
        self.notify(user, "riteaid", output)
        return output

    def check_stores(self, user):
        response = {
            "user": user,
            "availability": []
        }
        response["availability"].append(self.check_cvs(user))
        response["availability"].append(self.check_riteaid(user))
        return response

    # observability
    def put_emf(self, context, user, locations):
        counts = {
            "cvs": 0,
            "riteaid": 0
        }
        for location in locations:
            if location["store"] == "CVS":
                counts["cvs"] = len(location["availability_at"])
            elif location["store"] == "RiteAid":
                counts["riteaid"] = len(location["availability_at"])
        message = {
            "_aws": {
                "Timestamp": int(datetime.now().timestamp()*1000),
                "CloudWatchMetrics": [
                    {
                        "Namespace": "VaccineAvailability",
                        "Dimensions": [["user"]],
                        "Metrics": [
                            {
                                "Name": "cvs",
                                "Unit": "Count"
                            },
                            {
                                "Name": "riteaid",
                                "Unit": "Count"
                            }
                        ]
                    }
                ]
            },
            "functionVersion": context.function_version,
            "requestId": context.aws_request_id,
            "user": user,
            "cvs": counts["cvs"],
            "riteaid": counts["riteaid"]
        }
        print(json.dumps(message))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="path to application configurations")
    ap.add_argument("--user", required=True, help="user from config.json")
    args = ap.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    av = Availability()
    av.set_config(config)
    for user in [args.user]:
        print("Performing availability checks for {}.".format(user))
        av.check_cvs(user)
        av.check_riteaid(user)

if __name__ == "__main__":
    main()
