from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AvitoPage():
    def __init__(self, url: str, browser: webdriver.Chrome, login_creds: dict) -> None:
        self.url = url
        self.browser = browser
        self.login_creds = {
            "login": login_creds["login"],
            "password" : login_creds["password"],
        }

        self._login_btn_loc = [By.CSS_SELECTOR, '.button']
        self._logout_btn_loc = [By.CSS_SELECTOR, '.logout']
        self._login_inputs_loc = [By.TAG_NAME, 'input']
        self._project_btn_loc  = [By.XPATH, "//a[contains(text(), '<PROJECT_ID>')]"]
        self._projects_menu_loc = [By.CSS_SELECTOR, ".projects"]
        

    def open(self):
        self.browser.get(self.url)

    def login(self):
        login_btns = WebDriverWait(self.browser, 20).until(
                EC.presence_of_all_elements_located((self._login_inputs_loc[0], self._login_inputs_loc[1]))
        )
        username_input = login_btns[0]; password_input = login_btns[1]
        username_input.send_keys(self.login_creds['login'])
        password_input.send_keys(self.login_creds['password'])

        login_btn = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((self._login_btn_loc[0], self._login_btn_loc[1]))
        )
        login_btn.click()

    def projects_page_is_open(self):
        return len(self.browser.find_elements(self._projects_menu_loc[0], self._projects_menu_loc[1])) > 0

    def choose_project(self, project_id):
        project_btn_loc = self._project_btn_loc[1].replace("<PROJECT_ID>", str(project_id))
        project_link = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((self._project_btn_loc[0], project_btn_loc))
        )
        project_link.click()
        return True

    def logout(self):
        logout_btn = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((self._logout_btn_loc[0], self._logout_btn_loc[1]))
        )
        logout_btn.click()