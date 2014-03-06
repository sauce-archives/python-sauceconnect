import libsauceconnect as connect


class SauceConnect():
    def __init__(self, user, api_key, vmhost, vmport, proxyhost=None, proxyport=None, kgpproxy=None, kgpproxyuserpwd=None):
        self.context = connect.sc_new()

        # set defaults
        connect.sc_set_int(self.context, connect.SC_PARAM_IS_SERVER, 0)
        connect.sc_set_string(self.context, connect.SC_PARAM_EXT_HOST, 'localhost')
        connect.sc_set_int(self.context, connect.SC_PARAM_EXT_PORT, 8080)
        connect.sc_set_int(self.context, connect.SC_PARAM_LOCAL_PORT, 4445)
        connect.sc_set_int(self.context, connect.SC_PARAM_LOGLEVEL, 1)

        connect.sc_set_string(self.context, connect.SC_PARAM_USER, user)
        connect.sc_set_string(self.context, connect.SC_PARAM_API_KEY, api_key)

        connect.sc_set_string(self.context, connect.SC_PARAM_KGP_HOST, vmhost)
        connect.sc_set_int(self.context, connect.SC_PARAM_KGP_PORT, vmport)

        if (proxyhost != None):
            print "Setting proxy host '%s'" % proxyhost
            connect.sc_set_string(self.context, connect.SC_PARAM_EXT_HOST, proxyhost)

        if (proxyport != None):
            print "Setting proxy port '%i'" % proxyport
            connect.sc_set_int(self.context, connect.SC_PARAM_EXT_PORT, proxyport)

        if (kgpproxy != None):
            connect.sc_set_string(self.context, connect.SC_PARAM_PROXY, kgpproxy)
            if (kgpproxyuserpwd != None):
                connect.sc_set_string(self.context, connect.SC_PARAM_PROXY_USERPWD, kgpproxyuserpwd)

        print "Initializing Sauce Connect"
        st = connect.sc_init(self.context)
        if (st != 0):
            print "sc_init() failed"

    def run(self):
        print "Starting to run Connect"

        connect.sc_run(self.context)

    def stop(self):
        print "Waiting for Connect to stop..."
        connect.sc_stop(self.context)
        print "Connect Stopped"

    def free(self):
        connect.sc_free(self.context)

    def status(self):
        return connect.sc_status(self.context)
