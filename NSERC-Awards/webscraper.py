# -------------------------------------------------------------------
# PURPOSE: Web scrape NSERC research awards data by competition year
# by using the database provided on their website.
# -------------------------------------------------------------------

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
import time
import pandas as pd

def collectLinks(year):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    output_path = dir_path+'/NSERCLinks_' +  str(year) + '.xlsx'
    
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    
    # --------------------------------------------------------------
    # ********* START UP CHROME AND GO TO THE NSERC WEBSITE ********
    driver = webdriver.Chrome(executable_path=r'/Users/kevin/Desktop/chromedriver')
    driver.get("https://www.nserc-crsng.gc.ca/ase-oro/Results-Resultats_eng.asp")

    # ----------------------------------------
    # ********* ENTER SEARCH CRITERIA ********

    # Change CSS style off dropdown to make it visible and then select competition year range
    driver.execute_script("document.getElementById('competitionyearfrom').style.display = 'block';")
    Select(driver.find_element_by_css_selector('select#competitionyearfrom')).select_by_value(str(year))

    time.sleep(5)

    driver.execute_script("document.getElementById('competitionyearto').style.display = 'block';")
    Select(driver.find_element_by_css_selector('select#competitionyearto')).select_by_value(str(year))

    # Change CSS style off dropdown to make it visible and set fiscal year range to blank
    driver.execute_script("document.getElementById('fiscalyearfrom').style.display = 'block';")
    Select(driver.find_element_by_css_selector('select#fiscalyearfrom')).select_by_value("0")

    time.sleep(5)

    driver.execute_script("document.getElementById('fiscalyearto').style.display = 'block';")
    Select(driver.find_element_by_css_selector('select#fiscalyearto')).select_by_value("0")

    # Change CSS style to make it visible and select area of application dropdown value
    # ** NOTE: 703 = aerospace. You need to look up the values for each area.
    #driver.execute_script("document.getElementById('AreaApplication').style.display = 'block';")
    #Select(driver.find_element_by_css_selector('select#AreaApplication')).select_by_value("703")

    # Launch your search criteria
    driver.find_element_by_css_selector('#buttonSearch').click()
    time.sleep(15)

    # -------------------------------------------------
    # ********* NOW ON THE SEARCH RESULTS PAGE ********

    # Select 100 rows in the dropdown
    Select(driver.find_element_by_name('result_length')).select_by_value("100")
    time.sleep(20)

    # Click on last button and go to last page
    driver.find_element_by_css_selector('#result_last').click()
    time.sleep(20)

    # Get the number of pages by finding the value of the last page
    pages = driver.find_element_by_css_selector('.paginate_active').get_attribute('innerHTML')
    pages = int(pages)
    time.sleep(20)

    # Click on first button and go back to the first page
    driver.find_element_by_css_selector('#result_first').click()
    time.sleep(20)

    # Establish variables for the while loop
    nameList=[]
    titleList=[]
    linkList=[]
    amountList=[]
    yearList=[]
    progList=[]
    onPage=1

    # while the current page number is <= the total number of pages
    while onPage <= pages:
        
        # Get lists containing values from each column
        names = driver.find_elements_by_css_selector("table#result.display tr td:nth-child(1)")
        titles = driver.find_elements_by_css_selector("table#result.display tr td:nth-child(2)")
        links = driver.find_elements_by_css_selector("table#result.display tr td:nth-child(2) a")
        amounts = driver.find_elements_by_css_selector("table#result.display tr td:nth-child(3)")
        years = driver.find_elements_by_css_selector("table#result.display tr td:nth-child(4)")
        progs = driver.find_elements_by_css_selector("table#result.display tr td:nth-child(5)")

        # Iterate through column lists and retrieve data
        for name in names:
            nameList.append(name.text)

        for title in titles:
            titleList.append(title.text)

        for link in links:
            linkList.append(link.get_attribute("href"))

        for amount in amounts:
            amountList.append(amount.text)

        for year in years:
            yearList.append(year.text)

        for prog in progs:
            progList.append(prog.text)

        # Click on next page button, let it load, and then add to the counter
        driver.find_element_by_css_selector('#result_next').click()
        time.sleep(20)
        onPage+=1

    # After loop is finished quit chrome, create dataframe, and export it
    time.sleep(15)
    driver.quit()

    nsercLinks = pd.DataFrame(
        {'Name': nameList,
         'Title': titleList,
         'Link': linkList,
         'Amount': amountList,
         'Year': yearList,
         'Program': progList,
         }
    )

    nsercLinks.to_excel(writer,sheet_name='Award Summary Links',index=False)
    writer.save()


year = input("Enter the grant year you want to extract : ")
collectLinks(year)

contin='y'
while contin == 'y':
    again = input("Do you want to extract another year? (Y/N) : ")
    if again in ["N","n"]:
        contin = "n"
    elif again in ["Y","y"]:
        year = input("Enter the grant year you want to extract : ")
        collectLinks(year)
        
    
    

