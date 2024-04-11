from eis.tests.functional import *

class TestViews(FunctionalTestBase):
        
    def test_03_login_fails(self):
        """Vale parooliga sisse logimine"""
        params = {'isikukood': 'ADMIN',
                  'parool': 'vale',
                  'sisene': 'Sisene',
                  'request_url': '',
                  'action': 'signin',
                  }
        res = self.testapp.post('/login/signin', params, status=200)
        self.assertTrue('Kasutajakonto puudub või on vale parool' in res.body.decode())

    def test_04_login_succeeds(self):
        """Sisse logimine"""
        params = {'isikukood': 'ADMIN',
                  'parool': 'admin',
                  'sisene': 'Sisene',
                  'request_url': '',
                  'action': 'signin',
                  }
        
        res = self.testapp.post('/login/signin', params, status=302)
        #print 'cookies: %s' % self.testapp.cookies
        res = res.follow()
        #print self.testapp.cookies        
        self.assertTrue('ADMIN ADMIN' in res.body.decode())

    def test_05_logout(self):
        "Välja logimine"
        self._login()
        #headers = {'HTTP_COOKIE': 'eis=%s' % self.testapp.cookies['eis']}
        #print headers
        res = self.testapp.get('/ylesanded')
        res = self.testapp.get('/login/signout', status=302)

    # def test_06_login_sel(self):
    #     "Sisselogimine (selenium)"
    #     from selenium import webdriver
    #     from selenium.webdriver.common.keys import Keys
    #     from selenium.common.exceptions import NoSuchElementException
    #     from selenium.webdriver.firefox.firefox_profile import FirefoxProfile        
    #     from selenium.webdriver.firefox.firefox_binary import FirefoxBinary        
    #     from subprocess import Popen, PIPE
    #     srv = 'http://localhost:6543'

    #     from pyvirtualdisplay import Display
    #     display = Display(visible=0, size=(800, 600))
    #     display.start()
    #     # path = "/cygdrive/c/Program Files (x86)/Mozilla Firefox/firefox.exe"        
    #     # firefoxBinary = FirefoxBinary(path)
    #     # firefoxProfile = FirefoxProfile()
    #     # ## Disable CSS
    #     # firefoxProfile.set_preference('permissions.default.stylesheet', 2)
    #     # ## Disable images
    #     # firefoxProfile.set_preference('permissions.default.image', 2)
    #     # ## Disable Flash
    #     # firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    #     # driver = webdriver.Firefox(firefoxProfile, firefoxBinary)

    #     path = "/cygdrive/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"
    #     driver = webdriver.Chrome(path)
    #     driver.get(srv + '/login/signin', status=200)
    #     elem = driver.find_element_by_name("isikukood")
    #     elem.send_keys("ADMIN")
    #     elem = driver.find_element_by_name("parool")
    #     elem.send_keys("admin")        
    #     elem.send_keys(Keys.RETURN)
    #     assert "ADMIN ADMIN" in driver.page_source
    #     driver.quit()
    #     display.stop()
        
