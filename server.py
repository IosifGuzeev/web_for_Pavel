from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import json

from dateutil import parser, tz, relativedelta

API_LINK = "api/v1/"


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    @staticmethod
    def _process_date(date_as_string):
        date = json.loads(date_as_string.replace("'", "\""))
        date['date'] = parser.parse(date['date'])
        if 'tz' in date and date['tz'] is not None:
            date['tz'] = tz.gettz(date['tz'])
            date['date'].replace(tzinfo=date['tz'])
        return date

    def _process_tz(self, tz_as_str):
        try:
            timezone = tz.gettz(tz_as_str)
        except:
            self._set_response()
            self.wfile.write(f"Cant get time for given timezone ({tz_as_str})\n".encode('utf-8'))
            return None
        return timezone

    def do_GET(self):
        o = urlparse(self.path)
        resp_name = o.path[1:]
        args = parse_qs(o.query)
        logging.info(resp_name)
        logging.info(args)
        if resp_name == "":
            self._set_response()
            self.wfile.write("Server current time:\n".encode('utf-8'))
            self.wfile.write(str(datetime.now()).encode('utf-8'))
        elif resp_name == "favicon.ico":
            self.send_response(404)
        else:
            timezone = self._process_tz(resp_name)
            if timezone is not None:
                self._set_response()
                self.wfile.write(f"Current time for timezone with name {resp_name}:\n".encode('utf-8'))
                time = str(datetime.now(tz=timezone))
                logging.info(time)
                self.wfile.write(time.encode('utf-8'))

    def do_POST(self):
        global API_LINK

        o = urlparse(self.path)
        resp_name = o.path[1:]
        args = parse_qs(o.query)
        logging.info(resp_name)
        logging.info(args)
        if resp_name.startswith(API_LINK):
            resp_name = resp_name.replace(API_LINK, '')
            if resp_name == "time":
                if 'tz' in args:
                    timezone = self._process_tz(args['tz'][0])
                    if timezone is not None:
                        self._set_response()
                        time = str(datetime.now(tz=timezone).time())
                        logging.info(time)
                        self.wfile.write(time.encode('utf-8'))
                else:
                    self._set_response()
                    time = str(datetime.now().time())
                    self.wfile.write(time.encode('utf-8'))
            elif resp_name == "date":
                if 'tz' in args:
                    timezone = self._process_tz(args['tz'][0])
                    if timezone is not None:
                        self._set_response()
                        time = str(datetime.now(tz=timezone).date())
                        logging.info(time)
                        self.wfile.write(time.encode('utf-8'))
                else:
                    self._set_response()
                    time = str(datetime.now().date())
                    self.wfile.write(time.encode('utf-8'))
            elif resp_name == "datediff":
                start = self._process_date(args['start'][0])
                end = self._process_date(args['end'][0])
                logging.info(start)
                logging.info(end)
                self._set_response()
                self.wfile.write(str(relativedelta.relativedelta(end['date'], start['date'])).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=S, port=8090):
    logging.basicConfig(level=logging.INFO)
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    run()
