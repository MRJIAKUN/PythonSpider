# _*_coding:utf-8 _*_
__author__ = 'david'
__date__ = '2018/5/28 0:47'

from selenium import webdriver

browser = webdriver.Chrome(executable_path="F:/chromedriver/chromedriver.exe")
browser.get("https://www.zhihu.com/signin")

# browser.find_element_by_css_selector(".SignFlow-accountInput input[name='username']").send_keys("13144485182")
# browser.find_element_by_css_selector(".SignFlowInput div input[name='password']").send_keys("CAISIYUA")
# browser.find_element_by_css_selector("button.SignFlow-submitButton").click()
# print(browser.page_source)

# browser.quit()