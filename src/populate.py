import argparse
import boto3
import json

class Store:
    def __init__(self, config, table):
        self.config = config
        self.table = table
        self.client = boto3.client("dynamodb")

    def put_store(self, store):
        response = self.client.put_item(
            TableName=self.table,
            Item = {
                "user": { "S": "_{}".format(store) },
                "url": { "S": self.config[store]["url"] },
                "headers": { "S": json.dumps(self.config[store]["headers"]) }
            }
        )
        print(json.dumps(response))
        return response
    
    def put_user(self, user):
        response = self.client.put_item(
            TableName=self.table,
            Item = {
                "user": { "S": user },
                "preferences": { "S": json.dumps(self.config["user_preferences"][user]) }
            }
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
    s.put_store("cvs")
    s.put_store("riteaid")
    for user in config["user_preferences"]:
        s.put_user(user)

if __name__ == "__main__":
    main()
