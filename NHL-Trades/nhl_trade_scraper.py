# -------------------------------------------------------------------
# PURPOSE: Web scrape NHLTRADETRACKER.COM
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
import json


# ********* SETUP OUTPUT FILE ********
dir_path = os.path.dirname(os.path.realpath(__file__))

output_path = dir_path+'/nhl_trade_output.xlsx'
writer = pd.ExcelWriter(output_path, engine='xlsxwriter')


# ********* START UP CHROME AND GO TO THE SCORE GOLF WEBSITE ********
driver = webdriver.Chrome(executable_path=r'/Users/kevin/Desktop/chromedriver')

driver.get("http://www.nhltradetracker.com/")
time.sleep(5)

# Setup lists to store the golf course data
season_list=[]
decade_list=[]
date_list=[]
month_list=[]
teamone_list=[]
teamone_acq_list=[]
teamone_p_list=[]
teamone_np_list=[]
teamtwo_list=[]
teamtwo_acq_list=[]
teamtwo_p_list=[]
teamtwo_np_list=[]

tot_acq_p_list=[]
tot_acq_np_list=[]
tot_acq_cash_list=[]
tot_acq_future_list=[]
tot_acq_loan_list=[]
tot_acq_pick_list=[]
tot_acq_other_list=[]
tot_acq_list=[]

teamone_cash_list=[]
teamone_future_list=[]
teamone_loan_list=[]
teamone_pick_list=[]
teamone_other_list=[]
teamtwo_cash_list=[]
teamtwo_future_list=[]
teamtwo_loan_list=[]
teamtwo_pick_list=[]
teamtwo_other_list=[]

# Category flags
cashChecks = ['cash','$','Cash','cash other considerations']
loanChecks = ['loan of ','rights to ','right to ']
pickChecks = ['round Pick','round pick','round pcik','rounnd','round (','compensatory pick','conditional pick','Conditional pick',' conditional ','conditionnal pick','draft pick']
futureChecks = ['future consideration','other considerations']

# Get links to all regional lists
year_links=[]
div_container = driver.find_element_by_css_selector('#wrapper > div.sidebar > div > table')
years = div_container.find_elements_by_tag_name('a')
for y in years:
    year_links.append(y.get_attribute('href'))

alldata = ''
for link in year_links:
    driver.get(link)
    
    # If there are multiple pages for a given year then iterate through
    try:
        page_links = []
        page_nums = driver.find_element_by_class_name('pagination')
        page_nums = page_nums.find_elements_by_tag_name('a')
        count=0
        for p in page_nums:
            if p.get_attribute('innerHTML') == '<< previous':
                pass
            elif p.get_attribute('innerHTML') == 'next >>':
                pass
            else:
                page_links.append(p.get_attribute('href'))
    except:
        page_links = []
        page_nums = ""
    page_links.insert(0,link)
        
    # Use set to reduce to uniques (needed to remove the link associated with the next and previous buttons), then sort data
    page_links = sorted(set(page_links))

    for p_link in page_links:
        driver.get(p_link)
        time.sleep(5)

        # Get the season or year of the current page
        season = driver.find_element_by_css_selector('#container > h3').get_attribute("innerHTML")
        season = season.replace('Trades','')
        season = season.strip()
        
        div_container = driver.find_element_by_css_selector('#container')
        trades = div_container.find_elements_by_tag_name('tbody')
        for trade in trades:
            # There are tables within the main trade tables so we only want to loop through main ones which have a strong element inside
            if len(trade.find_elements_by_tag_name('strong')) != 0:

                # Get the name of each team in the trade
                heading = trade.find_elements_by_tag_name('tr')[0]
                team_one = heading.find_elements_by_tag_name('td')[0]
                team_one = team_one.find_elements_by_tag_name('strong')[0].get_attribute('innerHTML')
                team_one = team_one.replace(' acquire','')
                team_two = heading.find_elements_by_tag_name('td')[2]
                team_two = team_two.find_elements_by_tag_name('strong')[0].get_attribute('innerHTML')
                team_two = team_two.replace(' acquire','')
                print(team_one,"traded with",team_two)

                # Get date of trade
                lower_row = trade.find_elements_by_tag_name('tr')[1]
                lower_tds = lower_row.find_elements_by_tag_name('td')
                for td in lower_tds:
                    innertxt = td.get_attribute('innerHTML')
                    for month in ['January','February','March','April','May','June','July','August','September','October','November','December']:
                        if month in innertxt and ',' in innertxt:
                            trade_date = innertxt
                            trade_month = month
                print(trade_date)

                # Get information on team one's acquisitions
                details_t1 = trade.find_elements_by_tag_name('tbody')[0]
                details_t1 = details_t1.find_elements_by_tag_name('td')[1]
                details_t1 = details_t1.find_elements_by_tag_name('span')
                t1_acq_count = len(details_t1)
                t1_acq_player_count = 0
                t1_acq_nonplayer_count = 0
                t1_acq_other_count = 0
                t1_acq_cash_count = 0
                t1_acq_pick_count = 0
                t1_acq_loan_count = 0
                t1_acq_future_count = 0
                t1_acquis = ''
                for s in details_t1:
                    if s.get_attribute('class') == 'link':
                        # Try to acquire inner html of ahref element but not all are nested inside an ahref
                        # so on exception simply pull the innerHTML and clean
                        try:
                            acq = s.find_elements_by_tag_name('a')[0].get_attribute('innerHTML').strip()
                        except:
                            acq = s.get_attribute('innerHTML').strip()
                            acq = acq.replace('<br>','').strip()
                        t1_acq_player_count += 1
                    else:
                        acq = s.get_attribute('innerHTML').strip()
                        acq = acq.replace('<br>','').strip()

                        # Identify why type of asset it is ****
                        if any(check in acq for check in cashChecks):
                            t1_acq_cash_count += 1
                        elif any(check in acq for check in pickChecks):
                            t1_acq_pick_count += 1
                        elif any(check in acq for check in loanChecks):
                            t1_acq_loan_count += 1
                        elif any(check in acq.lower() for check in futureChecks):
                            t1_acq_future_count += 1
                        else:
                            t1_acq_other_count += 1
                                
                        t1_acq_nonplayer_count += 1
                    acq = acq+'\n'
                    t1_acquis += acq
                #print(t1_acquis)

                # Get information on team two's acquisitions
                details_t2 = trade.find_elements_by_tag_name('tbody')[1]
                details_t2 = details_t2.find_elements_by_tag_name('td')[0]
                details_t2 = details_t2.find_elements_by_tag_name('span')
                t2_acq_count = len(details_t2)
                t2_acq_player_count = 0
                t2_acq_nonplayer_count = 0
                t2_acq_other_count = 0
                t2_acq_cash_count = 0
                t2_acq_pick_count = 0
                t2_acq_loan_count = 0
                t2_acq_future_count = 0
                t2_acquis = ''
                for s in details_t2:
                    if s.get_attribute('class') == 'link':
                        # Try to acquire inner html of ahref element but not all are nested inside an ahref
                        # so on exception simply pull the innerHTML and clean
                        try:
                            acq = s.find_elements_by_tag_name('a')[0].get_attribute('innerHTML').strip()
                        except:
                            acq = s.get_attribute('innerHTML').strip()
                            acq = acq.replace('<br>','').strip()
                        t2_acq_player_count += 1
                    else:
                        acq = s.get_attribute('innerHTML').strip()
                        acq = acq.replace('<br>','').strip()

                        # Identify why type of asset it is ****
                        if any(check in acq for check in cashChecks):
                            t2_acq_cash_count += 1
                        elif any(check in acq for check in pickChecks):
                            t2_acq_pick_count += 1
                        elif any(check in acq for check in loanChecks):
                            t2_acq_loan_count += 1
                        elif any(check in acq.lower() for check in futureChecks):
                            t2_acq_future_count += 1
                        else:
                            t2_acq_other_count += 1
                            
                        t2_acq_nonplayer_count += 1
                    acq = acq+'\n'
                    t2_acquis += acq
                #print(t2_acquis,"\n")


                season_list.append(season)
                date_list.append(trade_date)
                month_list.append(trade_month)
                teamone_list.append(team_one)
                teamone_acq_list.append(t1_acquis)
                teamone_p_list.append(t1_acq_player_count)
                teamone_np_list.append(t1_acq_nonplayer_count)
                
                teamtwo_list.append(team_two)
                teamtwo_acq_list.append(t2_acquis)
                teamtwo_p_list.append(t2_acq_player_count)
                teamtwo_np_list.append(t2_acq_nonplayer_count)
                
                tot_acq_p_list.append(t1_acq_player_count + t2_acq_player_count)
                tot_acq_np_list.append(t1_acq_nonplayer_count + t2_acq_nonplayer_count)
                tot_acq_list.append(t1_acq_player_count + t2_acq_player_count + t1_acq_nonplayer_count + t2_acq_nonplayer_count)
                
                teamone_cash_list.append(t1_acq_cash_count)
                teamone_future_list.append(t1_acq_future_count)
                teamone_loan_list.append(t1_acq_loan_count)
                teamone_pick_list.append(t1_acq_pick_count)
                teamone_other_list.append(t1_acq_other_count)
                teamtwo_cash_list.append(t2_acq_cash_count)
                teamtwo_future_list.append(t2_acq_future_count)
                teamtwo_loan_list.append(t2_acq_loan_count)
                teamtwo_pick_list.append(t2_acq_pick_count)
                teamtwo_other_list.append(t2_acq_other_count)

                tot_acq_cash_list.append(t1_acq_cash_count+t2_acq_cash_count)
                tot_acq_future_list.append(t1_acq_future_count+t2_acq_future_count)
                tot_acq_loan_list.append(t1_acq_loan_count+t2_acq_loan_count)
                tot_acq_pick_list.append(t1_acq_pick_count+t2_acq_pick_count)
                tot_acq_other_list.append(t1_acq_other_count+t2_acq_other_count)


# Close window
driver.quit()

# Setup pandas dataframe and export
nhl_trades = pd.DataFrame(
    {'Season': season_list,
     'Date': date_list,
     'Month': month_list,
     'Team One': teamone_list,
     'Team One Acquisitions': teamone_acq_list,
     'Team One Acquired Players': teamone_p_list,
     'Team One Acquired Non-Players': teamone_np_list,
     'Team One Acquired Cash': teamone_cash_list,
     'Team One Acquired Picks': teamone_pick_list,
     'Team One Acquired Futures': teamone_future_list,
     'Team One Acquired Rights/Loans': teamone_loan_list,
     'Team One Acquired Other': teamone_other_list,
     'Team Two': teamtwo_list,
     'Team Two Acquisitions': teamtwo_acq_list,
     'Team Two Acquired Players': teamtwo_p_list,
     'Team Two Acquired Non-Players': teamtwo_np_list,
     'Team Two Acquired Cash': teamtwo_cash_list,
     'Team Two Acquired Picks': teamtwo_pick_list,
     'Team Two Acquired Futures': teamtwo_future_list,
     'Team Two Acquired Rights/Loans': teamtwo_loan_list,
     'Team Two Acquired Other': teamtwo_other_list,
     'Total Players Traded': tot_acq_p_list,
     'Total Non-Players Traded': tot_acq_np_list,
     'Total Cash Traded': tot_acq_cash_list,
     'Total Futures Traded': tot_acq_future_list,
     'Total Rights/Loans Traded': tot_acq_loan_list,
     'Total Picks Traded': tot_acq_pick_list,
     'Total Other Traded': tot_acq_other_list,
     'Total Assets Traded': tot_acq_list,
     }
)

# Export data and save file
nhl_trades.to_excel(writer,sheet_name='Trades',index=False)
writer.save()

