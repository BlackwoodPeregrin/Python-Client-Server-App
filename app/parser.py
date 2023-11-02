import re
import socket
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.data = []
        self.capture = False
        # self.raw_string = ' '

    def handle_starttag(self, tag, attrs):
        if tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "li", "em", "strong", "br", "u", "i"):
            self.capture = True

    def handle_endtag(self, tag):
        if tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "li", "em", "strong", "br", "u", "i"):
            self.capture = False

    def handle_data(self, data):
        if self.capture:
            self.data.append(data)

    def result_data(self):
        raw_string = " ".join(self.data)
        pattern = r"[^A-Za-z\s]"
        raw_result = re.sub(pattern, "", raw_string)
        result = " ".join(raw_result.split())
        return result


#
# parser = MyHTMLParser()
# parser.feed('<html><head><title>Test</title></head>'
#             '<body><h1>Parse me!</h1><p>This is P tag</p></body></html>')
#
# print(parser.result_data())