import argparse
import boto3
import json
from datetime import datetime, timedelta

class Store:
    def __init__(self, config, table):
        self.config = config
        self.table = table
        self.client = boto3.client("dynamodb")

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
    
    s = Store(config, args.table)
    stores = ["cvs", "riteaid", "walgreens"]
    for store in stores:
        s.put_store(store)
    for user in config["user_preferences"]:
        s.put_user(user)

if __name__ == "__main__":
    main()
