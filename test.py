import os

os.chdir(os.environ["PROGRAMFILES"] + "\\mediainfo")
from MediaInfoDLL3 import MediaInfo, Stream

MI = MediaInfo()

methods = [method_name for method_name in dir(MI)
 if callable(getattr(MI, method_name))]
for method in methods:
    print(method)