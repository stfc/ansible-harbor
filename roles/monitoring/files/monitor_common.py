#!/bin/python
from __future__ import division, print_function, absolute_import  # Ensure we stay Python 3 compat

import json
import sys

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2 for SL7
    from urllib2 import urlopen


def get_json_from_endpoint(target_url):
    result = urlopen(target_url)
    data = result.read().decode("utf-8")
    try:
        return json.loads(data)
    except ValueError:
        return "No JSON was returned"


def exit_with_endpoint_status(result, expected_result):
    if result != expected_result:
        print("Expected '{0}' got '{1}' instead.".format(expected_result, result))
        sys.exit(1)
    else:
        sys.exit(0)
