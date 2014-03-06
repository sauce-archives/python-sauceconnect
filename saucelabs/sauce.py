import saucelabs.saucerest as saucerest
import os
from time import sleep
from sauceconnect import SauceConnect
from proxy import Proxy
from multiprocessing import Process
from sys import exit

class Connect():
    tunnelDefaults = {
        'squid_config':         {},
        'ssh_port':             443,
        'domain_names':         ['sauce-connect.proxy'],
        'fast_fail_regexps':    [''],
        'use_kgp':              True,
        'no_ssl_bump_domains':  [''],
        'direct_domains':       [''],
        'vm_version':           '2013',
        'use_caching_proxy':    False,
        'tunnel_identifier':    None,
        'metadata': {
            'release':          '4.0-rc1'
        }
    }

    def __init__(self, options={}):
        print "Initializing Connect"

        self.port = options['port'] if 'port' in options else 443;

        self.args = {
            'username': options.get('username', os.environ['SAUCE_USERNAME']),
            'accessKey': options.get('accessKey', os.environ['SAUCE_ACCESS_KEY']),
            'kgpProxy': options.get('kgpProxy', None),
            'kgpProxyUserPwd': options.get('kgpProxyUserPwd', None),
            'domain_names': [] if options.get('i', False) else ['sauce-connect.proxy'],
            'direct_domains': options.get('D', ""),
            'tunnel_identifier': options.get('i', None),
            'shared_tunnel': options.get('s', None),
            'no_ssl_bump_domains': options.get('B', ""),
            'fast_fail_regexps': options.get('F', ""),
            'proxy_host': options.get('proxy_host', "localhost"),
            'proxy_port': options.get('proxy_port', 8787)
        }

        self.api = saucerest.SauceRest(
            username = self.args['username'],
            password = self.args['accessKey']
        )

    def __enter__(self):
        print "Entering Connect context"
        self.startup_connect()

    def __exit__(self, type, value, traceback):
        print "Leaving Connect context"
        self.shutdown_connect()

    # there is no createTunnel method in the Python implementation of Sauce Rest API
    def create_tunnel(self, options):
        print "Creating Tunnel"
        data = dict(self.tunnelDefaults)
        data.update(options)

        ret = self.api.rest(url="/%s/tunnels" % self.args['username'],
            method="POST",
            data=data)

        if ('id' in ret):
            print "Tunnel id is '%s'" % ret['id']
            return ret['id']
        else:
            print "Unable to create tunnel"
            return -1

    def cleanup_tunnels(self):
        print "Cleaning up Tunnels"
        tunnels = self.api.list_tunnels()
        for tunnelId in tunnels:
            tunnel = self.api.show_tunnel(tunnelId)
            if self.conflicting_tunnel(tunnel):
                print "Found conflicting tunnel. Shutting it down."
                self.api.delete_tunnel(tunnelId)
                print "Tunnel '%s' was shutdown." % tunnelId

    def conflicting_tunnel(self, tunnel):
        if (self.args['tunnel_identifier'] != None) & (self.args['tunnel_identifier'] == tunnel['tunnel_identifier']):
            return True
        if (self.args['tunnel_identifier'] == None) & (tunnel['tunnel_identifier'] == None):
            return True
        return False

    def wait_tunnel(self, tunnel_id):
        print "Waiting for VM"
        while True:
            tunnel = self.api.show_tunnel(tunnel_id)
            if tunnel['status'] == 'running':
                print "VM is now running"
                print "VM host is '%s'" % tunnel['host']
                return tunnel
            sleep(0.5)

    def setup_connect(self, tunnel):
        print "Setting up Connect"
        connect = SauceConnect(self.args['username'],
            self.args['accessKey'],
            tunnel['host'],
            self.port,
            self.args['proxy_host'],
            self.args['proxy_port'],
            self.args['kgpProxy'],
            self.args['kgpProxyUserPwd'])
        self.connectProcess = Process(target=connect.run)
        self.connectProcess.start()
        print "Connect process: '%i'" % self.connectProcess.pid

        return connect

    def startup_connect(self):
        self.cleanup_tunnels()
        self.tunnel_id = self.create_tunnel(self.args)
        self.tunnel = self.wait_tunnel(self.tunnel_id)

        if self.args['proxy_host'] != None:
            self.start_proxy()
        else:
            print "hmmm"

        self.connect = self.setup_connect(self.tunnel)
        status = self.connect.status()
        if status < 0:
            print "Cannot start Sauce Connect."
            return -1

    def shutdown_connect(self):
        self.connect.stop()
        self.connect.free()
        self.connectProcess.terminate()
        self.stop_proxy()

    def start_proxy(self):
        print "Starting local proxy"
        proxy = Proxy(self.args['proxy_host'], self.args['proxy_port'])

        self.proxyProcess = Process(target=proxy.start_server)
        self.proxyProcess.start()

        print "Proxy process: '%i'" % self.proxyProcess.pid

        return proxy

    def stop_proxy(self):
        print "Stopping local proxy"
        self.proxyProcess.terminate()
