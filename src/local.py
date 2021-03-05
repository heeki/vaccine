import argparse
import json
from lib.availability import Availability

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="path to application configurations")
    args = ap.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    av = Availability()
    av.set_config(config)
    av.check_stores()
    av.check_users()

if __name__ == "__main__":
    main()
