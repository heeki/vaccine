import argparse
import boto3
import json
from datetime import datetime, timedelta

class Admin:
    def __init__(self, table, config=None):
        self.config = config
        self.table = table
        self.client = boto3.client("dynamodb")

    # general
    def serde_user(self, item):
        print(json.dumps(item))
        output = {
            "user": item["user"]["S"],
            "notification_ttl": json.loads(item["notification_ttl"]["S"]),
            "preferences": json.loads(item["preferences"]["S"])
        }
        return output

    def get_item(self, user):
        response = self.client.get_item(
            TableName=self.table,
            Key={
                "user": { "S": user }
            }
        )
        body = serde_user(response["Item"])
        output = {
            "HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"],
            "ResponseBody": body
        }
        return output

    def get_items(self):
        response = self.client.scan(
            TableName=self.table
        )
        body = []
        for item in response["Items"]:
            if not item["user"]["S"].startswith("_"):
                body.append(self.serde_user(item))
        output = {
            "HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"],
            "ResponseBody": body
        }
        return output

    # store
    def put_store(self, store):
        payload = {
            "user": { "S": "_{}".format(store) },
            "url": { "S": self.config[store]["url"] },
            "headers": { "S": json.dumps(self.config[store]["headers"]) }
        }
        if "data" in self.config[store]:
            payload["data"] = { "S": json.dumps(self.config[store]["data"]) }
        response = self.client.put_item(
            TableName=self.table,
            Item = payload
        )
        print(json.dumps(response))
        return response

    # user
    def put_user(self, user):
        payload = {
            "user": { "S": user },
            "preferences": { "S": json.dumps(self.config["user_preferences"][user]) },
            "notification_ttl": { "S": {} },
            "ttl_in_seconds": { "N": str(self.config["user_preferences"][user]["ttl_in_seconds"]) }
        }
        stores = ["cvs", "riteaid"]
        ts_now = datetime.now() - timedelta(minutes=60)
        ts_now = ts_now.isoformat()
        payload["notification_ttl"]["S"] = json.dumps({store:ts_now for store in stores})
        response = self.client.put_item(
            TableName=self.table,
            Item = payload
        )
        print(json.dumps(response))
        return response

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="path to application configurations")
    ap.add_argument("--table", required=True, help="dynamodb table")
    args = ap.parse_args()

    with open(args.config) as f:
        config = json.load(f)
    
    a = Admin(args.table, config)
    stores = ["cvs", "riteaid", "walgreens"]
    for store in stores:
        a.put_store(store)
    for user in config["user_preferences"]:
        a.put_user(user)

if __name__ == "__main__":
    main()
