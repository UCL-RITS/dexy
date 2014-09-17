from dexy.exceptions import UserFeedback
import dexy.filter

from urllib2 import urlopen
from urllib import urlencode
import re


class Yuml(dexy.filter.DexyFilter):
    """
    Dexy filter to use Yuml.me
    """
    aliases = ["yuml"]
    _settings = {

        "output-extensions": ['.png', '.svg', '.img', '.pdf', '.jpg','.json'],
        "input-extensions": ['.yuml'],
        "style": ("Diagram style: boring, plain, or scruffy","scruffy"),
        "output": True,
        "added-in-version": "1.0.15",
        "api-url": "http://yuml.me/diagram",
        "type": ("Diagram type, e.g. class","class")

    }

    def process(self):
        request = {}
        settings = self.setting_values()

        content=urlencode(self.input_data)
        self.log_debug("Fetching from YUML")
        url="/".join([settings["api-url"],settings["style"],settings["type"],content])+self.ext
        self.log_debug("Fetching YUML from {0}".format(url))

        response = urlopen(url)
        self.output_data.set_data(response.read())
        self.output_data.save()
        response.close()
