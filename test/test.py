import saucelabs.sauce as sauce
from sauceclient import SauceClient
import unittest
from selenium import webdriver
import sys
import os
import httplib
import base64
import saucelabs.saucerest as saucerest
try:
    import json
except ImportError:
    import simplejson as json


class SauceConnectTest(unittest.TestCase):
    def setUp(self):
        self.username = os.environ['SAUCE_USERNAME']
        self.access_key = os.environ['SAUCE_ACCESS_KEY']

        desired_capabilities = webdriver.DesiredCapabilities.CHROME
        desired_capabilities['browserName'] = 'chrome'
        desired_capabilities['version'] = ''
        desired_capabilities['platform'] = ''
        desired_capabilities['name'] = 'Testing Python SauceConnect'

        self.connect = sauce.Connect()
        self.connect.startup_connect()

        self.driver = webdriver.Remote(
            desired_capabilities=desired_capabilities,
            command_executor="http://%s:%s@ondemand.saucelabs.com:80/wd/hub" % (self.username, self.access_key)
        )
        self.driver.implicitly_wait(30)

    def test_sauce(self):
        # just hit a bare-bones Rails installation
        self.driver.get('http://localhost:3000')
        self.assertTrue("Ruby" in self.driver.title)

    def tearDown(self):
        print("Link to your job: https://saucelabs.com/jobs/%s" % self.driver.session_id)
        job_passed = sys.exc_info() == (None, None, None)
        sc = SauceClient(self.username, self.access_key)
        sc.jobs.update_job(self.driver.session_id, passed=job_passed)
        self.driver.quit()
        self.connect.shutdown_connect()

if __name__ == '__main__':
    unittest.main()
