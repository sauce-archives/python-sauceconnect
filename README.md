# Sauce Connect in C for Python
- - -

This is a Python library for using [Sauce Labs'](http://www.saucelabs.com) [Sauce Connect 4](http://saucelabs.com/docs/connect).

## Install `libsauceconnect`

  - follow instructions for [binary distribution](http://saucelabs.com/docs/connect)

Set the environment variable `SAUCE_CONNECT_DIR` to the root of the build (this will be the folder created by unzipping the downloaded file). Once this Python distribution is stable, the SauceConnect library will be included within it.

## Further dependencies

This library depends upon [Sauce Labs'](http://www.saucelabs.com) library for communicating with the REST API, [`python-saucerest`](https://github.com/OniOni/python-saucerest) and [`sauceclient`](http://cgoldberg.github.io/sauceclient/).


It also depends on a small number of standard C libraries:

  - `ssl` (version 1 or higher; can be set with `OPENSSL_DIR` environment variable)
  - `crypto`
  - `curl`
  - `event`
  - `event_openssl`

Ensure these are available on your system and the C compiler can find them.

## Build the library

The library is build with [`distutils`](http://docs.python.org/2/distutils/). To build and install, simply move to the directory with `setup.py` in it, and run

```shell
python setup.py install
```

## Write tests

Ideally the Sauce Connect instance is spun up early and remains on. This could be done in a [Fab](http://docs.fabfile.org/en/1.8/) script, or any other tool used in your development workflow. Toward this, it can be used through its context manager,

```python
import saucelabs.sauce as sauce

with sauce.Connect():
    # run your test code

```

Alternatively, it can be used in individual tests:

```python
import saucelabs.sauce as sauce
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
        self.connect.startupConnect()

        self.driver = webdriver.Remote(
            desired_capabilities=desired_capabilities,
            command_executor="http://%s:%s@ondemand.saucelabs.com:80/wd/hub" % (self.username, self.access_key)
        )
        self.driver.implicitly_wait(30)

    def test_sauce(self):
        # self.driver.get('http://localhost:3000/rails/info/properties')
        # self.assertTrue("Routes" in self.driver.title)
        self.driver.get('http://localhost:3000')
        self.assertTrue("Ruby" in self.driver.title)

    def tearDown(self):
        print("Link to your job: https://saucelabs.com/jobs/%s" % self.driver.session_id)
        data = json.dumps({ "passed": sys.exc_info() == (None, None, None) })
        rest = saucerest.SauceRest(
            username = self.username,
            password = self.access_key
        )
        # rest.update_job(self.driver.session_id, data) # broken?
        self.set_test_status(self.driver.session_id, data)
        self.driver.quit()
        self.connect.shutdownConnect()

    # saucerest is returning (False, 400, 'Bad request') for some reason
    def set_test_status(self, jobid, data):
        base64string = base64.encodestring('%s:%s' % (self.username, self.access_key))[:-1]
        connection = httplib.HTTPConnection("saucelabs.com")
        connection.request('PUT', '/rest/v1/%s/jobs/%s' % (self.username, jobid),
                       data,
                       headers={"Authorization": "Basic %s" % base64string})
        result = connection.getresponse()
        return result.status == 200

if __name__ == '__main__':
    unittest.main()
```

## Authors

  - Isaac Murchie ([imurchie](https://github.com/imurchie))

## License

License - [Apache 2](http://www.apache.org/licenses/LICENSE-2.0)
