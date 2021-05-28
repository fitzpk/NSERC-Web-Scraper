# -------------------------------------------------------------------
# PURPOSE: Web scrape ARWU rankings data by subject
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
import os


# ********* SETUP OUTPUT FILE ********
dir_path = os.path.dirname(os.path.realpath(__file__))
year = input('What year would you like to extract? ')

output_path = dir_path+'/'+year+'_output_file.xlsx'
writer = pd.ExcelWriter(output_path, engine='xlsxwriter')


# ********* START UP CHROME AND GO TO THE ARWU RANKINGS WEBSITE ********
driver = webdriver.Chrome(executable_path=r'/Users/kevin/Desktop/chromedriver')

driver.get("https://www.shanghairanking.com/rankings/gras/"+year)

time.sleep(5)

eng_subjects = driver.find_element_by_css_selector('#RS02 > div.subject-list')
subjects = eng_subjects.find_elements_by_tag_name("a")

links=[]
sub_names=[]
for s in subjects:
    link = s.get_attribute('href')
    sub_name = s.get_attribute('innerHTML')
    sub_name = sub_name.replace('</span>','')
    sub_name = sub_name[sub_name.find('>')+1:]
    links.append(link)
    sub_names.append(sub_name)
    print(link,sub_name)


# ********* RETRIEVE DATA FOR EACH INSTITUTION ON EACH PAGE IN EACH SUBJECT OF INTEREST ********
unis=[]
years=[]
subs=[]
ranks=[]
totals=[]
qs=[]
cncis=[]
ics=[]
tops=[]
awards=[]

for link,sub in zip(links,sub_names):
    driver.get(link)

    time.sleep(5)

    # find the number of pages we have to iterate through
    ul_list = driver.find_element_by_css_selector('#content-box > ul')
    pages = ul_list.find_elements_by_tag_name("li")
    num_pages = int(pages[-2].text)

    for page in range(2,num_pages+1):
        print(page)
        
        if page > 2:
            # Scroll up to ensure dropdown is visible
            driver.find_element_by_css_selector('#__layout > div > div.back-top').click()
            time.sleep(2)

        table = driver.find_element_by_css_selector('#content-box > div.rk-table-box')
        rows = table.find_elements_by_tag_name("tr")

        for num in range(1,len(rows)):
            # Get university name (some won't have a link so they have a different selector)
            try:
                uni = driver.find_element_by_css_selector('#content-box > div.rk-table-box > table > tbody > tr:nth-child('+str(num)+') > td.align-left > div > div.tooltip > div > a > span').get_attribute('innerHTML')
            except:
                uni = driver.find_element_by_css_selector('#content-box > div.rk-table-box > table > tbody > tr:nth-child('+str(num)+') > td.align-left > div > div.tooltip > div > span').get_attribute('innerHTML')
            uni = uni.strip()
            uni = uni.replace('amp;','')
            uni = uni.replace('&nbsp;',' ')
            
            # *!*!*!* WILL NEED TO EDIT NAMES WITH '&' and OTHER SYMBOLS !*!*!*!*

            # Get world rank
            rank = driver.find_element_by_css_selector('#content-box > div.rk-table-box > table > tbody > tr:nth-child('+str(num)+') > td:nth-child(1) > div').get_attribute('innerHTML')
            rank = rank.strip()

            # Get total score
            total_score = driver.find_element_by_css_selector('#content-box > div.rk-table-box > table > tbody > tr:nth-child('+str(num)+') > td:nth-child(4)').get_attribute('innerHTML')
            total_score = total_score.strip()

            # Get data for each indicator
            if year < 2020:
                indicators = ['PUB','CNCI','IC','TOP','AWARD']
            else:
                indicators = ['Q1','CNCI','IC','TOP','AWARD']
                
            for ind in indicators:
                # Open dropdown and select indicator
                driver.find_element_by_css_selector('#content-box > div.rk-table-box > table > thead > tr > th:nth-child(5) > div > div.rank-select > div.inputWrapper').click()
                driver.find_element_by_xpath("//ul[@class='options']//li[. = '"+ind+"']").click()
                
                # Get score value and clean it up
                score = driver.find_element_by_css_selector('#content-box > div.rk-table-box > table > tbody > tr:nth-child('+str(num)+') > td:nth-child(5)').get_attribute('innerHTML')
                score = score.strip()

                if ind == 'Q1':
                    q_score = score
                elif ind == 'CNCI':
                    cnci_score = score
                elif ind == 'IC':
                    ic_score = score
                elif ind == 'TOP':
                    top_score = score
                elif ind == 'AWARD':
                    award_score = score

            unis.append(uni)
            years.append(year)
            subs.append(sub)
            ranks.append(rank)
            totals.append(total_score)
            qs.append(q_score)
            cncis.append(cnci_score)
            ics.append(ic_score)
            tops.append(top_score)
            awards.append(award_score)

        # Click next page and sleep for 5 seconds to let it load
        try:
            selected_page = driver.find_element_by_css_selector('#content-box > ul > li.ant-pagination-item.ant-pagination-item-'+num_pages+'.ant-pagination-item-active')
            selected_page = int(selected_page.find_element_by_tag_name('a').text)
        except:
            selected_page = 0

        # If we aren't on the last page then click the next page button
        if selected_page == num_pages:
            pass
        else:
            pages[-1].click()
        time.sleep(5)

# Close window
driver.quit()

# Setup pandas dataframe and export
arwu = pd.DataFrame(
    {'Institution': unis,
     'Year': years,
     'Subject': subs,
     'World Rank': ranks,
     'Total Score': totals,
     'Q1': qs,
     'CNCI': cncis,
     'IC': ics,
     'TOP': tops,
     'AWARD': awards,
     }
)

arwu.to_excel(writer,sheet_name='2021',index=False)
writer.save()
