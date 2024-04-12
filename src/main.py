import os
import sys

import cultAuto


def main():
    ## Check for env vars
    if "AT" in os.environ and "ST" in os.environ and "DEV_ID" in os.environ:
        at = os.environ["AT"]
        st = os.environ["ST"]
        devId = os.environ["DEV_ID"]
    else:
        print("Set AT, ST and DEV_ID environment vars. Exiting.")
        sys.exit(1)
    ## Initialize class
    ca = cultAuto.cultAuto(at=at, st=st, deviceId=devId)
    ca.book_class_decision(centre_preference=("Banashankari", "Basavanagudi"))


main()
