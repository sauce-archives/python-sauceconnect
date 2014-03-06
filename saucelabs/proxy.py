import SimpleHTTPServer
import SocketServer
import httplib
import socket


class Proxy():
    def __init__(self, host, port):
        self.httpd = SocketServer.TCPServer((host, port), ProxyHandler)
        self.httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start_server(self):
        try:
            self.httpd.serve_forever()
        except socket.error, (value,message):
            return -1

    def stop_server(self):
        self.httpd.shutdown()



class ProxyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        url = self.parseUrl(self.path)

        headers = self.headers
        headers['uri'] = url['path']

        #
        res = self.mkWriter(url, headers)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(res))
        self.end_headers()
        self.wfile.write(res)

    def parseUrl(self, path):
        protocol = "http"
        tmp = path

        parts = path.split("//")
        if len(parts) > 1:
            protocol = parts[0]
            tmp = parts[1]

        parts = tmp.split("/")
        host = parts[0]
        rest = parts

        port = 80 if protocol == "http:" else 443

        if (host != None) & (host.find(":") != -1):
            tmp = host.split(":")
            host = tmp[0]
            port = tmp[1]

        path = ""
        if (rest != None) & (len(rest) > 1):
            for el in rest[1:len(rest)]:
                path += "/" + el

        return {
            "protocol": protocol,
            "host": host,
            "port": port,
            "path": path
        }

    def mkWriter(self, url, h):
        conn = httplib.HTTPConnection(url['host'], url['port'])
        conn.request("GET", url['path'])
        r1 = conn.getresponse()
        print r1.status, r1.reason

        return r1.read()


if __name__ == "__main__":
    proxy = Proxy("localhost", 8787)
    proxy.startServer()
