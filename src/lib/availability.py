import asyncio
import boto3
import json
import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from lib.store import CVS, RiteAid, Walgreens

class Availability:
    def __init__(self, debug=False):
        self.debug = debug
        self.config = {
            "user_preferences": {},
            "notification_ttl": {},
            "ttl_in_seconds": 600
        }
        # self.stores = ["cvs", "riteaid", "walgreens"]
        self.stores = ["cvs", "riteaid"]
        for store in self.stores:
            self.config[store] = {}
        if "TOPIC" in os.environ:
            self.topic = os.environ["TOPIC"]
        if "TABLE" in os.environ:
            self.table = os.environ["TABLE"]
        self.client_sns = boto3.client("sns")
        self.client_ddb = boto3.client("dynamodb")
        self.data = {}
        self.logging = True

    # internal data
    def get_all_stores(self):
        aggregate = {}
        for user in self.get_users():
            for store in self.stores:
                for location in self.config["user_preferences"][user][store]:
                    if store not in aggregate:
                        aggregate[store] = {}
                    aggregate[store][location] = self.config["user_preferences"][user][store][location]
        return aggregate

    def get_users(self):
        return self.config["user_preferences"].keys()

    def set_config(self, config):
        for store in self.stores:
            if store in config:
                self.config[store] = config[store]
        for user in config["user_preferences"]:
            self.config["user_preferences"][user] = config["user_preferences"][user]
            self.config["notification_ttl"][user] = {}
            self.config["ttl_in_seconds"] = config["user_preferences"][user]["ttl_in_seconds"]

    def set_notification_ttl(self, user, store, ts, offline=False):
        if user not in self.config["notification_ttl"]:
            self.config["notification_ttl"][user] = {}
        self.config["notification_ttl"][user][store] = ts.isoformat()
        if not offline:
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
        self.config[store]["url"] = response["url"]["S"]
        self.config[store]["headers"] = json.loads(response["headers"]["S"])
        if "data" in response:
            self.config[store]["data"] = response["data"]["S"]

    def pull_config(self):
        response = self.client_ddb.scan(
            TableName=self.table
        )["Items"]
        for item in response:
            user = item["user"]["S"]
            if not user.startswith("_"):
                if user not in self.config["user_preferences"]:
                    self.config["user_preferences"][user] = {}
                if "preferences" in item:
                    self.config["user_preferences"][user] = json.loads(item["preferences"]["S"])
                if user not in self.config["notification_ttl"]:
                    self.config["notification_ttl"][user] = {}
                if "notification_ttl" in item:
                    self.config["notification_ttl"][user] = json.loads(item["notification_ttl"]["S"])
            else:
                value = item["user"]["S"]
                store = value[1:len(value)]
                if store not in self.config:
                    self.config[store] = {}
                self.config[store]["url"] = item["url"]["S"]
                self.config[store]["headers"] = json.loads(item["headers"]["S"])
                if "data" in item:
                    self.config[store]["data"] = item["data"]["S"]

    def put_user(self, user):
        payload = {
            "user": { "S": user }
        }
        if user in self.config["user_preferences"]:
            payload["preferences"] = { "S": json.dumps(self.config["user_preferences"][user]) }
        if user in self.config["notification_ttl"]:
            payload["notification_ttl"] = { "S": json.dumps(self.config["notification_ttl"][user]) }
        print(json.dumps(payload))
        response = self.client_ddb.put_item(
            TableName=self.table,
            Item = payload
        )
        return response

    # notifications
    def send_sns(self, user, store, subject, message):
        output = True
        if user in self.config["notification_ttl"] and store in self.config["notification_ttl"][user]:
            ts_now = datetime.now()
            ts_last = datetime.fromisoformat(self.config["notification_ttl"][user][store])
            ts_diff = ts_now - ts_last
            if int(ts_diff.total_seconds()) > self.config["ttl_in_seconds"]:
                if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
                    debugging = {
                        "notification_ttl": self.config["notification_ttl"][user][store],
                        "ttl_in_seconds": self.config["ttl_in_seconds"],
                        "ts_now": ts_now.isoformat(),
                        "ts_last": ts_last.isoformat(),
                        "ts_diff": int(ts_diff.total_seconds())
                    }
                    print(json.dumps(debugging))
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
                    self.set_notification_ttl(user, store, ts_now)
            else:
                output = False
        return output

    def notify(self, user, store, notifications):
        store = store.lower()
        subject = "Vaccination availability alert"
        in_scope = list(filter(lambda x: x in self.config["user_preferences"][user][store].keys(), notifications["availability_at"]))
        count = len(in_scope)
        if count == 0:
            message = "No vaccine availability at {} for {}.".format(notifications["store"], user)
        else:
            aggregate = self.get_all_stores()
            message = "\n".join(["Vaccine availability at {} ({}) for {}.".format(notifications["store"], aggregate[store][location], user) for location in in_scope])
            if not self.send_sns(user, store, subject, message):
                count = 0
        if self.logging:
            print(message)
        output = {
            "count": count,
            "message": message
        }
        return output

    # external api calls
    def get_availability(self, url, headers, data=None):
        request = urllib.request.Request(url)
        request.add_header("user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36")
        for header in headers:
            request.add_header(header, headers[header])
        try:
            if data is None:
                response = urllib.request.urlopen(request)
            else:
                response = urllib.request.urlopen(request, data=json.dumps(data).encode("utf-8"))
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error = {
                "code": e.code,
                "reason": e.reason,
                "url": url
            }
            print(json.dumps(error))
        return {}

    def check_store(self, store, location=None):
        baseurl = self.config[store]["url"]
        headers = self.config[store]["headers"]
        output = {
            "store": store,
            "location": location
        }
        if store == "cvs":
            output["response"] = self.get_availability(baseurl, headers)
        elif store == "riteaid":
            url = "{}{}".format(baseurl, location)
            output["response"] = self.get_availability(url, headers)
        elif store == "walgreens":
            data = self.config[store]["data"]
            output["response"] = self.get_availability(baseurl, headers, data)
        # print(json.dumps(output))
        return output

    async def check_stores(self, parallel=True):
        aggregate = self.get_all_stores()
        output = {store:{} for store in self.stores}
        if parallel:
            responses = []
            with ThreadPoolExecutor(max_workers=10) as ex:
                loop = asyncio.get_event_loop()
                tasks = [
                    loop.run_in_executor(
                        ex, self.check_store, *(store, location)
                    ) for store in aggregate for location in aggregate[store]
                ]
                for response in await asyncio.gather(*tasks):
                    responses.append(response)
            for response in responses:
                store = response["store"]
                location = response["location"]
                if store == "cvs":
                    output[store] = response["response"]
                elif store == "riteaid":
                    output[store][location] = response["response"]
        else:
            for store in aggregate:
                if store == "cvs":
                    response = self.check_store(store)
                    output[store] = response["response"]
                elif store == "riteaid":
                    for location in aggregate[store]:
                        response = self.check_store(store, location)
                        output[store][location] = response["response"]
        self.data = output
        return output

    def check_user(self, user):
        output = {
            "user": user,
            "availability": []
        }
        for store in self.stores:
            result = {}
            availability = []
            if store == "cvs":
                s = CVS()
                s.set_data(self.data["cvs"])
                s.set_preferences(self.config["user_preferences"])
                result = s.check_availability(user)
            elif store == "riteaid":
                s = RiteAid()
                s.set_data(self.data["riteaid"])
                s.set_preferences(self.config["user_preferences"])
                result = s.check_availability(user, self.config["user_preferences"][user]["riteaid"])
            elif store == "walgreens":
                s = Walgreens()
                s.set_data(self.data["walgreens"])
                s.set_preferences(self.config["user_preferences"])
                result = s.check_availability(user)
            output["availability"].append(result)
            self.notify(user, store, result)
        return output

    def check_users(self):
        output = []
        for user in self.get_users():
            output.append(self.check_user(user))
        if not self.logging:
            print(json.dumps(output))
        return output

    # observability
    def put_emf(self, context, user, locations):
        counts = { store: 0 for store in self.stores}
        for location in locations:
            counts[location["store"].lower()] = len(location["availability_at"])
        message = {
            "_aws": {
                "Timestamp": int(datetime.now().timestamp()*1000),
                "CloudWatchMetrics": [
                    {
                        "Namespace": "VaccineAvailability",
                        "Dimensions": [["user"]],
                        "Metrics": []
                    }
                ]
            },
            "functionVersion": context.function_version,
            "requestId": context.aws_request_id,
            "user": user
        }
        for store in self.stores:
            metric = {
                "Name": store,
                "Unit": "Count"
            }
            message["_aws"]["CloudWatchMetrics"][0]["Metrics"].append(metric)
        for store in counts:
            message[store] = counts[store]
        print(json.dumps(message))
        return message
