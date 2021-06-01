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

output_path = dir_path+'/_score_golf_output.xlsx'
writer = pd.ExcelWriter(output_path, engine='xlsxwriter')


# ********* START UP CHROME AND GO TO THE SCORE GOLF WEBSITE ********
driver = webdriver.Chrome(executable_path=r'/Users/kevin/Desktop/chromedriver')

driver.get("http://scoregolf.com/golf-course-guide/")
time.sleep(5)

# Setup lists to store the golf course data
course_list=[]
prov_list=[]
reg_list=[]
starval_list=[]
starrat_list=[]
access_list=[]
ovholes_list=[]
holes_list=[]
crserat_list=[]
crseslope_list=[]
crsyards_list=[]
par_list=[]

# Get links to all regional lists
region_links=[]
region_names=[]
div_container = driver.find_element_by_css_selector('#page-section > div > div.large-12.columns.page-wrapper > div.row.inner-page-wrapper > div.ext-row-content > div > div > div > div.block.course-search-block > div.crs-province > ul')
provinces = div_container.find_elements_by_tag_name('li')
for p in provinces:
    regions = p.find_elements_by_tag_name('h5')
    for reg in regions:
        region_link = reg.find_element_by_tag_name('a').get_attribute('href')
        region_name = reg.find_element_by_tag_name('span').get_attribute('innerHTML')
        if 'golf-courses-by-cities' not in region_link:
            region_links.append(region_link)
            region_names.append(region_name)
        else:
            pass

# Loop through each regional golf course list in each province and retrieve course details
for link,name in zip(region_links,region_names):
    driver.get(link)
    time.sleep(2)

    # Find number of rows/golf courses in the regional table
    table = driver.find_element_by_css_selector('#page-section > div > div.large-12.columns.page-wrapper > div.row.inner-page-wrapper > div.ext-row-content > div > div > div.block > div:nth-child(1) > div.block.region-filter > div > table > tbody')
    rows = table.find_elements_by_tag_name("tr")

    for num in range(1,len(rows)+1):
        row_data = driver.find_element_by_css_selector('#facName'+str(num))

        # Get course name
        cname = row_data.find_element_by_tag_name('span').get_attribute('innerHTML')

        # Get province of course
        prov_value = driver.find_element_by_css_selector('#page-section > div > div.large-12.columns.page-wrapper > div.row.inner-page-wrapper > div.ext-row-content > div > div > div:nth-child(1) > div:nth-child(1) > ul > li:nth-child(2) > a').get_attribute('innerHTML')
        prov_value = prov_value.replace('Golf Courses','').strip()

        # Get course's star rating
        stars_div = driver.find_element_by_css_selector('#page-section > div > div.large-12.columns.page-wrapper > div.row.inner-page-wrapper > div.ext-row-content > div > div > div.block > div:nth-child(1) > div.block.region-filter > div > table > tbody > tr:nth-child('+str(num)+') > td.facRate.hide-for-small-only > div')
        stars = stars_div.find_elements_by_tag_name("i")
        star_value = stars_div.find_element_by_tag_name("span").get_attribute('innerHTML')
        if len(stars) == 0:
            star_rating = 'Not Rated'
        else:
            star_rating=0
            for s in stars:
                if s.get_attribute('class') == 'fa fa-star':
                    star_rating+=1
        
        # Get link to course details and click it!
        detail_link = row_data.find_elements_by_tag_name("a")
        detail_link = detail_link[0].get_attribute('href')
        driver.get(detail_link)
        time.sleep(2)

        # Get access type
        try:
            access = driver.find_element_by_css_selector('#page-section > div > div.large-12.columns.page-wrapper > div.row.inner-page-wrapper > div.ext-row-content > div > div > div:nth-child(1) > div.block.cg-wrapper > div.facility-info-wrapper > div.large-9.medium-9.small-12.columns > div:nth-child(1) > div:nth-child(1) > div > div.block.mobPaddingTop > label.block-label').get_attribute('innerHTML')
            access = access.replace('/','').strip()
        except:
            access = 'No Info'
        

        # Get overall number of holes
        try:
            ov_holes = driver.find_element_by_css_selector('#page-section > div > div.large-12.columns.page-wrapper > div.row.inner-page-wrapper > div.ext-row-content > div > div > div:nth-child(1) > div.block.cg-wrapper > div.facility-info-wrapper > div.large-9.medium-9.small-12.columns > div:nth-child(1) > div:nth-child(1) > div > div.block.mobPaddingTop > label.label-info').get_attribute('innerHTML')
        except:
            ov_holes = 'No Info'


        # Get extra info from label bar for each course
        try:
            info = driver.find_element_by_css_selector('#courseratingsblock > div')
            info = info.find_element_by_tag_name("label").text

            if 'Holes' in info:
                holes = info[:info.find('Holes')].strip()
            else:
                holes = 'No Info'

            if 'Par' in info:
                par = info[info.find('Par'):]

                # par might be the last item in the string so adjust
                if ',' in par:
                    par = par[:par.find(',')].strip()
                    par = par.replace('Par','').strip()
                else:
                    par = par.replace('Par','').strip()
            else:
                par = 'No Info'

            if 'yds' in info:
                yards = info[:info.find('yds')]
                yards = yards[yards.rfind(',')+1:].strip()
            else:
                yards = 'No Info'

            if 'Slope' in info:
                slope = info[info.find('Slope'):]

                # Slope might be the last item in the string so adjust for that scenario
                if ',' in slope:
                    slope = slope[:slope.find(',')].strip()
                    slope = slope.replace('Slope','').strip()
                else:
                    slope = slope.replace('Slope','').strip()
            else:
                slope = 'No Info'

            if 'Rating' in info:
                c_rating = info[info.find('Rating'):]
                c_rating = c_rating.replace('Rating','').strip()
            else:
                c_rating = 'No Info'
        except:
            holes = 'No Info'
            par = 'No Info'
            yards = 'No Info'
            slope = 'No Info'
            c_rating = 'No Info'
        
        # Print results for each course to investigate any issues
        print('Course Name:',cname)
        print('Province:',prov_value)
        print('Region:',name)
        print('Star Value:',star_value)
        print('Star Rating:',star_rating)
        print('Access:',access)
        print('# of Holes:',ov_holes)
        print('Cleaned Info: **********\n',holes,par,yards,slope,c_rating,'\n************************')
        print('Original Info: **********\n',info,'\n***********************\n')

        # Append data to our on-going lists
        course_list.append(cname)
        prov_list.append(prov_value)
        reg_list.append(name)
        starval_list.append(star_value)
        starrat_list.append(star_rating)
        access_list.append(access)
        ovholes_list.append(ov_holes)
        crserat_list.append(c_rating)
        crseslope_list.append(slope)
        crsyards_list.append(yards)
        par_list.append(par)
        holes_list.append(holes)

        # Return to regional course list
        driver.get(link)
        time.sleep(2)

            
# Close window
driver.quit()

# Setup pandas dataframe and export
score_golf = pd.DataFrame(
    {'Course': course_list,
     'Province': prov_list,
     'Region': reg_list,
     'Star Value': starval_list,
     'Star Rating': starrat_list,
     'Access': access_list,
     'Overall Holes': ovholes_list,
     'Rating': crserat_list,
     'Slope': crseslope_list,
     'Yards': crsyards_list,
     'Par': par_list,
     'Holes': holes_list,
     }
)

# Export data and save file
score_golf.to_excel(writer,sheet_name='Courses',index=False)
writer.save()

