#!/usr/bin/python3

import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TestServer(unittest.TestCase):

    # set up and tear down functions -----------------------------------------

    def setUp(self):

        # clear the database
        open('../database.db', 'w').close()

        # prepare the driver
        self.driver = webdriver.Firefox() # Chrome, Firefox
        self.driver.get("http://localhost:5000/init_db") # initialize the database
        self.driver.get("http://localhost:5000/") # open the website

    def tearDown(self):

        if not self.is_view('welcome'):
            self.log_out()

        self.driver.close()

    # unit tests -------------------------------------------------------------

    def test_login(self):

        driver = self.driver

        # check the welcome view is active
        self.assertTrue( self.is_view('welcome') )

        # try to log in a non-existent user
        self.log_in('non@existent.user', 'password')

        # check the feedback message
        element = driver.find_element_by_id("signInFeedback")
        self.assertEqual(element.text, 'Invalid email or password')
        self.assertTrue( self.is_view('welcome') )

        # try to log in an existent user with wrong password
        self.log_in('a@b.c', 'password')

        # check the feedback message
        element = driver.find_element_by_id("signInFeedback")
        self.assertEqual(element.text, 'Invalid email or password')
        self.assertTrue( self.is_view('welcome') )

        # try to log in an existent user with correct password
        self.log_in('a@b.c', '12345')
        self.assertTrue( self.is_view('profile') )

        # try to log out
        self.log_out()
        self.assertTrue( self.is_view('welcome') )

    def test_singup(self):

        driver = self.driver

        # check the welcome view is active
        self.assertTrue( self.is_view('welcome') )

        # try to register a user with different passwords
        element = driver.find_element_by_id("firstName")
        element.send_keys('Homer')
        element = driver.find_element_by_id("familyName")
        element.send_keys('Simpson')
        element = driver.find_element_by_id("city")
        element.send_keys('Springfield')
        element = driver.find_element_by_id("country")
        element.send_keys('US')
        element = driver.find_element_by_id("signupEmail")
        element.send_keys('safety@SNPP.com')
        element = driver.find_element_by_id("signupPassword")
        element.send_keys('homer123')
        element = driver.find_element_by_id("signupRepeatPassword")
        element.send_keys('1234567')
        element = driver.find_element(By.XPATH, '//button[text()="Sign up"]')
        element.click()

        element = driver.find_element_by_id('signUpFeedback')
        self.assertEqual(element.text, "Passwords don't match.")
        self.assertTrue( self.is_view('welcome') );

        # correct the password and try to sign up again
        element = driver.find_element_by_id("signupRepeatPassword")
        element.clear()
        element.send_keys('homer123', Keys.ENTER)

        self.assertTrue( self.is_view('profile') )

        # log out
        self.log_out()
        self.assertTrue( self.is_view('welcome') )

        # log in
        self.log_in('safety@SNPP.com', 'homer123')
        self.assertTrue( self.is_view('profile') )

        # log out
        self.log_out()
        self.assertTrue( self.is_view('welcome') )

    def test_home_tab(self):

        driver = self.driver

        self.assertTrue( self.is_view('welcome') )
        self.log_in('a@b.c', '12345')
        self.assertTrue( self.is_view('profile') )

        element = driver.find_element_by_id("infoFirstName")
        self.assertEqual(element.text, 'harry')
        element = driver.find_element_by_id("infoFamilyName")
        self.assertEqual(element.text, 'potter')
        element = driver.find_element_by_id("infoCity")
        self.assertEqual(element.text, 'Hogwarts')
        element = driver.find_element_by_id("infoCountry")
        self.assertEqual(element.text, 'Magic Land')
        element = driver.find_element_by_id("infoEmail")
        self.assertEqual(element.text, 'a@b.c')

        self.log_out()
        self.assertTrue( self.is_view('welcome') )

    def test_browse_tab(self):

        driver = self.driver
        self.assertTrue( self.is_view('welcome') )
        self.log_in('a@b.c', '12345')
        self.assertTrue( self.is_view('profile') )

        # go to the browser tab
        driver.find_element(By.XPATH, '//a[text()="Browse"]').click()

        # try to find a non existent user
        element = driver.find_element_by_id("searchUser")
        element.send_keys('non@existent.user')
        driver.find_element(By.XPATH, '//button[text()="Find"]').click()

        element = driver.find_element_by_id("searchUserFeedback")
        self.assertEqual(element.text, 'No such user')

        # try to find an existent user
        element = driver.find_element_by_id("searchUser")
        element.clear()
        element.send_keys('Carl@Luck.nl', Keys.ENTER)

        # wait up to 2 sec for the user to be found (the first name is displyed)
        wait = WebDriverWait(driver, 2)
        wait.until(EC.text_to_be_present_in_element((By.ID, "infoFirstName"), 'Carl'))
        element = driver.find_element_by_id("infoFamilyName")
        self.assertEqual(element.text, 'Luck')
        element = driver.find_element_by_id("infoCity")
        self.assertEqual(element.text, 'Amsterdam')
        element = driver.find_element_by_id("infoCountry")
        self.assertEqual(element.text, 'Netherlands')
        element = driver.find_element_by_id("infoEmail")
        self.assertEqual(element.text, 'Carl@Luck.nl')

        self.log_out()
        self.assertTrue( self.is_view('welcome') )

    def test_send_message(self):

        driver = self.driver
        self.assertTrue( self.is_view('welcome') )
        self.log_in('a@b.c', '12345')
        self.assertTrue( self.is_view('profile') )
        driver.find_element(By.XPATH, '//a[text()="Browse"]').click()
        element = driver.find_element_by_id("searchUser")
        element.send_keys('Carl@Luck.nl', Keys.ENTER)

        wait = WebDriverWait(driver, 2)
        wait.until(EC.text_to_be_present_in_element((By.ID, "infoFirstName"), 'Carl'))

        element = driver.find_element_by_id("postMessage")
        element.send_keys("Hello Carl!")
        driver.find_element(By.XPATH, '//button[text()="Post message"]').click()

        self.log_out()
        self.assertTrue( self.is_view('welcome') )
        self.log_in('Carl@Luck.nl', 'pass1')
        self.assertTrue( self.is_view('profile') )

        wait = WebDriverWait(driver, 2) # wait up to 2 sec for the message to be displayed
        wait.until(EC.text_to_be_present_in_element((By.ID, "homeMessageWall"), 'a@b.c: Hello Carl!'))

        self.log_out()
        self.assertTrue( self.is_view('welcome') )

    def test_change_password(self):

        driver = self.driver
        self.assertTrue( self.is_view('welcome') )
        self.log_in('Carl@Luck.nl', 'pass1')
        self.assertTrue( self.is_view('profile') )

        # go to the edit profile page
        driver.find_element(By.XPATH, '//a[text()="Account"]').click()
        driver.find_element(By.XPATH, '//a[text()="Edit Profile"]').click()

        # wrong original password
        element = driver.find_element_by_id('oldPassword')
        element.send_keys('pass0')
        element = driver.find_element_by_id('newPassword')
        element.send_keys('pass2')
        element = driver.find_element_by_id('newPasswordRepeat')
        element.send_keys('pass2')
        driver.find_element(By.XPATH, '//button[text()="Change Password"]').click()
        element = driver.find_element_by_id("passwordChangeFeedback")
        self.assertEqual(element.text, "Old Password incorrect")

        # passwords do not match
        element = driver.find_element_by_id('oldPassword')
        element.clear()
        element.send_keys('pass1')
        element = driver.find_element_by_id('newPassword')
        element.clear()
        element.send_keys('pass2')
        element = driver.find_element_by_id('newPasswordRepeat')
        element.clear()
        element.send_keys('pass3')
        driver.find_element(By.XPATH, '//button[text()="Change Password"]').click()
        element = driver.find_element_by_id("passwordChangeFeedback")
        self.assertEqual(element.text, "New passwords don't match.")

        # change passwords
        element = driver.find_element_by_id('newPasswordRepeat')
        element.clear()
        element.send_keys('pass2')
        driver.find_element(By.XPATH, '//button[text()="Change Password"]').click()
        element = driver.find_element_by_id("passwordChangeFeedback")
        self.assertEqual(element.text, "Password changed")

        # log out
        self.log_out()
        self.assertTrue( self.is_view('welcome') )

        # log in with the old password
        self.log_in('Carl@Luck.nl', 'pass1')
        element = driver.find_element_by_id("signInFeedback")
        self.assertEqual(element.text, 'Invalid email or password')
        self.assertTrue( self.is_view('welcome') )

        # log in with the new password
        self.log_in('Carl@Luck.nl', 'pass2')
        self.assertTrue( self.is_view('profile') )

        self.log_out()
        self.assertTrue( self.is_view('welcome') )

    # custom functions -------------------------------------------------------

    def log_in(self, email, password):
            driver = self.driver

            element = driver.find_element_by_id('inputEmail')
            element.clear()
            element.send_keys(email)

            element = driver.find_element_by_id('inputPassword')
            element.clear()
            element.send_keys(password)

            driver.find_element(By.XPATH, '//button[text()="Sign in"]').click()

    def log_out(self):
            driver = self.driver
            element = driver.find_element(By.XPATH, '//a[text()="Account"]')
            element.click()
            element = driver.find_element(By.XPATH, '//a[text()="Sign Out"]')
            element.click()

    # check check if the view 'view' is active
    def is_view(self, view):

        # check if a valid view was chosen
        if view not in ('profile', 'welcome'):
            raise ValueError('Unknown view')

        try:
            wait = WebDriverWait(self.driver, 2) # wait two seconds
            if view == 'profile':
                # look for the profileWall in the currentView
                element = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="currentView"]/div[@id="profileWall"]')))
            if view == 'welcome':
                # look for the welcomeWall in the currentView
                element = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="currentView"]/div[@id="welcomeWall"]')))
            return True
        except TimeoutException:
            # if TimeoutException is raised the view 'view' is not active
            return False

# run the tests
if __name__ == '__main__':
    unittest.main()
