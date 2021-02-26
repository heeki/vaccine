import argparse
import boto3
import json
import os
import sys
import urllib.request

if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
   topic = os.environ["TOPIC"]
   client = boto3.client("sns")

class Availability:
   def __init__(self, config):
      self.config = config

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

   def notify(self, notifications):
      if len(notifications["availability_at"]) == 0:
         message = "No vaccine availability for {}.".format(notifications["store"])
      else:
         subject = "Vaccination availability alert"
         message = ""
         for notification in notifications["availability_at"]:
            message += "Vaccine availability for {} at {}.\n".format(notification["store"], notification["location"])
         if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
            client.publish(
               TopicArn=topic,
               Subject=subject,
               Message=message
            )
      print(message)
      return notifications

   def check_cvs(self):
      locations = []
      response = self.get_availability(self.config["cvs"]["url"], self.config["cvs"]["headers"])
      for store in response["responsePayloadData"]["data"]["NJ"]:
         if (store["status"] != "Fully Booked"): 
            locations.append(store["city"])
      output = {
         "store": "CVS",
         "availability_at": locations
      }
      return output

   def check_riteaid(self):
      locations = []
      for store in self.config["riteaid"]["stores"]:
         url = "{}{}".format(self.config["riteaid"]["url"], store)
         response = self.get_availability(url, self.config["riteaid"]["headers"])
         if (response["Data"]["slots"]["1"] or response["Data"]["slots"]["2"]):
            locations.append(store["city"])
      output = {
         "store": "RiteAid",
         "availability_at": locations
      }
      return output

def main():
   ap = argparse.ArgumentParser()
   ap.add_argument("--config", required=True, help="path to application configurations")
   args = ap.parse_args()

   with open(args.config) as f:
      config = json.load(f)

   av = Availability(config)
   av.notify(av.check_cvs())
   av.notify(av.check_riteaid())

if __name__ == "__main__":
   main()
