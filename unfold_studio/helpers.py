import os
import random
import subprocess
from datetime import datetime
from django.conf import settings
import subprocess
import logging
import re

log = logging.getLogger('django')    

def compile_ink(inkcode):
    """ Writes inkcode to a file, calls to external program inklecate
    to process file, and returns a dict with status, result, and message."""

    fn = "{:%Y_%m_%d_%H_%M_%S_}".format(datetime.now()) + str(random.random())[2:] + '.ink'
    fqn = os.path.join(settings.INK_DIR, fn)
    try: 
        with open(fqn, 'w') as inkfile:
            inkfile.write(inkcode)
    except IOError as e:
        return {"status": "error", "message": e}
    try:
        message = subprocess.check_output(["inklecate", fqn]).decode("utf-8")
        with open(fqn + ".json", encoding="utf-8-sig") as outfile:
            result = outfile.read()
        if message:
            return {
                "status": "warning", 
                "message": message.replace(fqn, "your story"), 
                "result": result,
                "line": line_num(message) or 0
            }
        else:
            return {
                "status": "ok", 
                "result": result, 
                "message": "ink compiled successfully",
                "line": 0
            }
    except subprocess.CalledProcessError as e:
        message = e.output.decode("utf-8")
        log.info(message)
        return {
            "status": "error", 
            "message": message.replace(fqn, "your story"),
            "line": line_num(message) or 0
        }

    
def line_num(message):
    "Extract line number from error or warning"
    match = re.search("line (\d+)", message)
    if match: 
        return int(match.group(1))
