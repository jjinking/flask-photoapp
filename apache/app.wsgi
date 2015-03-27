#!/usr/bin/env python

import os
import sys
import logging

logging.basicConfig(stream=sys.stderr)
parent_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.insert(0, parent_dir)

from app import create_app

application = create_app('production')
