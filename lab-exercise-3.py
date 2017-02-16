# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest

class DeAnza_A_Z(unittest.TestCase):
    # This method will get run once at the beginning of every test
    def setUp(self):
        # Set the browser to be used and provide the path to the downloaded chromedriver
        self.driver = webdriver.Chrome('C:\Users\Andre\Desktop\chromedriver') 
   
        # Wait for 30 seconds for objects to become visible to the user/test
        self.driver.implicitly_wait(30)                                   

        # Set the static part of the URL to be tested
        self.base_url = "http://deanza.edu/"                             

        # Initialize an array of errors
        self.verificationErrors = []

    # This method is a single test of the proper functioning of 3 links on De Anza's A-Z page
    def test_a_z_links(self):
        driver = self.driver

        # Append the rest of the De Anza URL onto the base_url set in setUp() above
        driver.get(self.base_url + "/directory/dir-az.html")

        # Click on the "Academic Calendar" link
        driver.find_element_by_link_text("Academic Calendar").click()

        # Check that the link works by comparing expected page title to actual page title
        self.assertEqual("De Anza College :: Academic Calendar :: Home", driver.title)

        # Go back to A-Z Website Directory page
        driver.back()

        # Repeat the click/assert/back with the next link
        driver.find_element_by_link_text("Academic Freedom Policy").click()
        self.assertEqual("De Anza College :: About De Anza :: Academic Freedom", driver.title)
        driver.back()

        # Repeat the click/assert/back with still another link
        driver.find_element_by_link_text("Academic Probation").click()
        self.assertEqual("De Anza College :: Policies :: Standards for Probation", driver.title)
        driver.back()
        
        # Click/assert/back with another link
        driver.find_element_by_link_text("Prerequisite Clearance Request").click()
        self.assertEqual("De Anza College :: Assessment Center :: Prerequisites, Corequisites and Advisories :: Overview", driver.title)
        driver.back()
        
        # Additional click/assert/back
        driver.find_element_by_link_text("Athletics").click()
        self.assertEqual("De Anza College :: Athletics :: Welcome to Athletics", driver.title)
        driver.back()
        
        # Another click/assert/back
        driver.find_element_by_link_text("Kirsch Center for Environmental Studies").click()
        self.assertEqual("De Anza College :: Kirsch Center for Environmental Studies :: A Building That Teaches", driver.title)
        driver.back()
        
    
    def tearDown(self):
        # Quit the browser
        self.driver.quit()
      
        # Make sure the initial array of errors is still empty
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
