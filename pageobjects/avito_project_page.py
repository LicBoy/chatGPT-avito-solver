from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pageobjects.avito_page import AvitoPage

class AvitoProjectPage(AvitoPage):
    """
    A class used to represent Avito Project Page

    ...

    Attributes
    ----------
    ***_loc : tuple
        a tuple with selector type and selector itself

    Methods
    ----------
    get_question_number()
        Returns the number of question (oid);
        Uses self._progress_bar_loc
    wait_next_question_load(last_question_number)
        Waits until next question is loaded from last one (next_question_number = last_question_number + 1);
        Returns true on success wait, false if element wasn't found after wait time;
        Uses self._question_num_loc
    get_ad_name()
        Returns the title of question (ad_name);
        Uses self._ad_name_loc
    get_ad_descr()
        Returns the description of question (ad_descr);
        Uses self._ad_descr_loc
    get_ad_msgs() : list[dict{'msg': str, 'from': str}]
        Returns the list of msgs dictionaries with keys 'msg', 'from';
        Uses self._msg_text_loc
    get_chat_info()
        Returns dictionary with current question's number, name, description and all messages.\n
        Dict has following return type: {'oid': str, 'ad_name': str, 'ad_descr': str, 'messages': [{'msg': str, 'from': str(one of 'seller', 'buyer')}]}
            
    """
    def __init__(self, url: str, browser: webdriver.Chrome, login_creds: dict, project_id) -> None:
        super().__init__(url, browser, login_creds)
        self.project_id = project_id

        self._ad_name_loc = (By.XPATH, '//div[@class="wrapper_pre"][1]//pre')
        self._ad_descr_loc = (By.XPATH, '//div[@class="wrapper_pre"][3]//pre')
        self._msg_text_loc = (By.XPATH,
            "//div[@class='messages']//div[contains(@class, 'row')]/div[@class='message text']")
        self._progress_bar_loc = (By.CSS_SELECTOR, ".progress_bar > * > * ")
        self._question_num_loc = (By.XPATH,
            '//div[@class="progress_bar"]/div/div[contains(text(),"<NUMBER_REPLACE>")]')
        self._answer_btn_loc = (By.XPATH, 
            "//div[@class = 'answers']/div[contains(text(), '<ANS_TEXT>')]")
        self._submit_btn_loc = (By.TAG_NAME, "button")
        self._empty_task_msg_loc = (By.CSS_SELECTOR,
            ".message")
        self._some_error_msg_loc = (By.CSS_SELECTOR,
            ".el-notification")
    
    def get_question_number(self) -> str:
        ad_text = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((self._progress_bar_loc[0], self._progress_bar_loc[1]))
        ).text
        return (ad_text.split(' ')[2]).split('.')[0]
    
    def wait_next_question_load(self, last_question_number) -> bool:
        num_replaced = self._question_num_loc[1].replace("<NUMBER_REPLACE>", str(last_question_number+1))
        elem = WebDriverWait(self.browser, 60).until(
            EC.presence_of_element_located((self._question_num_loc[0], num_replaced))
        )
        return elem is not None
        
    def get_ad_name(self) -> str:
        ad_text = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((self._ad_name_loc[0], self._ad_name_loc[1]))
        ).text
        return ad_text
    
    def get_ad_descr(self) -> str:
        ad_descr = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((self._ad_descr_loc[0], self._ad_descr_loc[1]))
        ).text
        return ad_descr

    def get_ad_msgs(self) -> list[dict]:
        msg_texts = WebDriverWait(self.browser, 20).until(
            EC.presence_of_all_elements_located((self._msg_text_loc[0], self._msg_text_loc[1]))
        )
        res = []
        for elem in msg_texts:
            parent_elem =  elem.find_element(By.XPATH, '..')
            msg_from = 'seller' if ('seller' in parent_elem.get_attribute('class')) else 'buyer'
            res.append({'msg': elem.text, 'from': msg_from})
        return res
    
    def get_chat_info(self) -> dict:
        """
        Returns dictionary with following keys:
        ----------
        oid : str
            oid, equals to chat number in Avito page
        ad_name : str
            the title of ad
        ad_descr : str
            the description of ad
        messages : list <dict>
            the list of msgs dictionaries, where each dict has keys:
                msg : str
                    the text of msg
                from : one of ['seller', 'buyer']
                    who sent the msg
        """
        return {
            'oid' : self.get_question_number(),
            'ad_name' : self.get_ad_name(),
            'ad_descr' : self.get_ad_descr(),
            'messages' : self.get_ad_msgs(),
        }
    
    def click_answer(self, ans_text) -> None:
        ans_loc = self._answer_btn_loc[1].replace("<ANS_TEXT>", ans_text)
        ad_descr = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((self._answer_btn_loc[0], ans_loc))
        )
        ad_descr.click()

    def click_submit_btn(self) -> None:
        submit_btn = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((self._submit_btn_loc[0], self._submit_btn_loc[1]))
        )
        submit_btn.click()

    def tasks_ended(self) -> bool:
        tasks_ended_element = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((self._empty_task_msg_loc[0], self._empty_task_msg_loc[1]))
        )
        return tasks_ended_element is not None and len(self.browser.find_elements(self._msg_text_loc[0],
            self._msg_text_loc[1])) == 0

    def some_error_msg_appeared(self) -> bool:
        some_error_element = self.browser.find_elements(self._some_error_msg_loc[0],
                                                    self._some_error_msg_loc[1])
        return len(some_error_element) > 0