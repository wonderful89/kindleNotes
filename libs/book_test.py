#!/usr/local/bin/python3
# coding=utf-8
import re
import os, os.path
import shutil
import random
import string
import datetime
from operator import itemgetter, attrgetter

# import sys
# sys.path.append("../")

import book

sen1 = book.Sentence("fsakfl1", 2)
sen2 = book.Sentence("fsakfl2", 4)
chapter1 = book.Chapter("chapter1", [sen2, sen1], 3)
print("sen1 = ", sen1)
chapter1.sortSen()
print(chapter1)

