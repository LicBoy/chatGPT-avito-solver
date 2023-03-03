from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, math
from selenium.webdriver.support.ui import Select

avito_url = 'https://centiman.avito.ru/service-dataset-collector-frontend/login'
chatGPT_url = 'https://chat.openai.com/'

options = webdriver.ChromeOptions()
options.add_argument(r"--user-data-dir=C:\\Users\\ahmet\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
browser = uc.Chrome(options)
browser.maximize_window()
action = ActionChains(browser)

RESPONSE_WORD_TO_NUM = {
    'да' : 1,
    'нет': 2,
    'неинформативный' : 3
}
GPT_MSG_MAX_LEN = 16326

def chatGPT_try_login():
    global chatGPT_url

    loc_login_btns= '.btn-primary'
    loc_google_login_btn = 'button[data-provider~="google"]'
    loc_capcha_btn = "#challenge-stage input[type='button']"
    loc_google_account_btn = "[data-identifier='ahmetvaleevr@gmail.com']"

    try:
        capcha_btn = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, loc_capcha_btn))
        )
        capcha_btn.click()

        while input('Capcha detected!!!\nSolve it and type "solved": ').lower() != 'solved':
            continue
    except:
        print('Capcha wasnt found, moving further')

    login_btns = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, loc_login_btns))
    )
    login_btn = login_btns[0]
    login_btn.click()
    
    google_login_btn = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, loc_google_login_btn))
            )
    google_login_btn.click()

    if google_acc_login():
        while WebDriverWait(browser, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".prose button"))
            ) == None:
            print("CONFIRM LOGIN ON YOUR PHONE!")
    # #If double login needed
    # try:
    #     WebDriverWait(browser, 60).until(
    #             EC.presence_of_all_elements_located((By.CSS_SELECTOR, loc_login_btns))
    #             )
    #     login_btns = WebDriverWait(browser, 10).until(
    #         EC.presence_of_all_elements_located((By.CSS_SELECTOR, loc_login_btns))
    #     )
    #     login_btn = login_btns[0]
    #     login_btn.click()

    #     google_login_btn = WebDriverWait(browser, 10).until(
    #             EC.presence_of_element_located((By.CSS_SELECTOR, loc_google_login_btn))
    #             )
    #     time.sleep(1)
    #     google_login_btn.click()
    #     google_account_login_btn = WebDriverWait(browser, 10).until(
    #             EC.presence_of_element_located((By.CSS_SELECTOR, loc_google_account_btn))
    #             )
    #     time.sleep(1)
    #     google_account_login_btn.click()
    # except:
    #     print("Logged in in first attempt, no double login needed :)")

def google_acc_login():
    from CREDS import GOOGLE_USERNAME, GOOGLE_PASSWORD
    loc_username_input = '//*[@id ="identifierId"]'
    loc_password_input = '//*[@id ="password"]/div[1]/div / div[1]/input'
    loc_page_buttons = 'button>span'

    google_username_inp = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.XPATH, loc_username_input))
        )
    time.sleep(1)
    google_username_inp.send_keys(GOOGLE_USERNAME)
    time.sleep(0.5)
    google_username_inp.send_keys(Keys.ENTER)
    
    # google_password_inp = WebDriverWait(browser, 20).until(
    #     EC.presence_of_element_located((By.XPATH, loc_password_input))
    #     )
    google_password_inp = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.XPATH, loc_password_input))
        )
    google_password_inp.send_keys(GOOGLE_PASSWORD)
    time.sleep(0.5)
    google_password_inp.send_keys(Keys.ENTER)
    return True

def chatGPT_skip_intro():
    skip_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".prose button"))
            )
    skip_button.click()
    time.sleep(1)
    skip_button = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Next"]'))
        )
    skip_button.click()
    time.sleep(1)
    skip_button = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Done"]'))
        )
    skip_button.click()

def chatGPT_page_ready_to_be_asked():
    loc_textarea = 'textarea'
    try:
        return WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, loc_textarea))
        ) is not None
    except:
        print('ChatGPT not ready for working. Trying to login to all systems!')
        chatGPT_try_login()
        chatGPT_skip_intro()
        chatGPT_page_ready_to_be_asked()
        
def chatGPT_send_insturctions():
    from CREDS import GPT_RULES_TEXT
    loc_textarea = 'textarea'
    question_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, loc_textarea))
    )
    question_input.send_keys(GPT_RULES_TEXT)
    question_input.send_keys(Keys.ENTER)

def browser_wait_all_elements_located(By_Type, locator, amount_of_elements_to_wait):
    print(f"Waiting for {amount_of_elements_to_wait} elements to load")
    WebDriverWait(browser, 60).until(
            lambda browser: len(browser.find_elements(By_Type, locator)) == amount_of_elements_to_wait)
    print(f"Elements are loaded!")

def chatGPT_wait_for_answer(total_answers, return_ans=True):
    loc_answer_is_ready = '.markdown.prose:not(.result-streaming)>p'
    loc_stop_generating_btn = '.btn'
    timeout_time = 60
    GPT_answers = None
    try:
        browser_wait_all_elements_located(By_Type=By.CSS_SELECTOR, locator=loc_answer_is_ready, amount_of_elements_to_wait=total_answers)
        GPT_answers = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, loc_answer_is_ready))
        )
    except:
        stop_generating_btn = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, loc_stop_generating_btn))
        )
        stop_generating_btn.click()
        regenerate_response_btn = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, loc_stop_generating_btn))
        )
        regenerate_response_btn.click()
        print(f'Couldnt get response in {timeout_time} seconds. Trying new...')
        return chatGPT_wait_for_answer(total_answers, return_ans)
        
    return GPT_answers[-1] if return_ans else None
    
def chatGPT_ask(msg, text_area_element=None, mutliline=True):
    loc_textarea = 'textarea'
    question_input = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, loc_textarea))
    )
    if text_area_element is not None:
        question_input = text_area_element
    if mutliline:
        msg_lines = msg.split('\n')
        for msg_line in msg_lines:
            question_input.send_keys(msg_line)
            action.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
        question_input.send_keys(Keys.ENTER)
        return
    question_input.send_keys(msg)
    WebDriverWait(browser, 30).until(EC.text_to_be_present_in_element((By.TAG_NAME, loc_textarea), msg))
    question_input.send_keys(Keys.ENTER)

def chatGPT_ask_ramis(msg, text_area_element=None, mutliline=True):
    loc_textarea = 'textarea'
    question_input = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, loc_textarea))
    )

    JS_ADD_TEXT_TO_INPUT = """
    var elm = arguments[0], txt = arguments[1];
    elm.value += txt;
    elm.dispatchEvent(new Event('change'));
    """

    if text_area_element is not None:
        question_input = text_area_element
        question_input.clear()
        question_input.click()
    if mutliline:
        msg_lines = msg.split('\n')
        print('MSG LINES', msg_lines)
        for msg_line in msg_lines:
            #question_input.send_keys(msg_line)
            browser.execute_script(JS_ADD_TEXT_TO_INPUT, question_input, msg_line)
            action.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
        question_input.send_keys(Keys.ENTER)
        return
    #question_input.send_keys(msg)
    browser.execute_script(JS_ADD_TEXT_TO_INPUT, question_input, msg)
    WebDriverWait(browser, 30).until(EC.text_to_be_present_in_element((By.TAG_NAME, loc_textarea), msg))
    question_input.send_keys(Keys.ENTER)

def avito_try_login():
    from CREDS import AVITO_USERNAME, AVITO_PASSWORD, AVITO_PROJECT_ID
    try:
        browser.execute_script(f'''window.open("{avito_url}","_blank");''')
        WebDriverWait(browser, 10).until(EC.number_of_windows_to_be(2))
        browser.switch_to.window(browser.window_handles[1])
    except:
        print("Probably AVITO window was blocked! Give permission!!!")
        time.sleep(10)
        browser.execute_script(f'''window.open("{avito_url}","_blank");''')
        WebDriverWait(browser, 10).until(EC.number_of_windows_to_be(2))
        browser.switch_to.window(browser.window_handles[1])

    loc_login_btn = '.button'
    loc_login_inputs = 'input'
    loc_project_link = f"//a[contains(text(), '{AVITO_PROJECT_ID}')]"
    login_btns = WebDriverWait(browser, 20).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, loc_login_inputs))
        )
    
    username_input = login_btns[0]; password_input = login_btns[1];
    username_input.send_keys(AVITO_USERNAME)
    password_input.send_keys(AVITO_PASSWORD)

    time.sleep(1)
    login_btn = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, loc_login_btn))
        )
    login_btn.click()

    project_link = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, loc_project_link))
        )
    project_link.click()

def avito_get_question():
    #First, check if message is ok -> we have question on project
    loc_page_message = '.message'
    message_text = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, loc_page_message))).text
    if message_text == AVITO_NO_TASKS_MESSAGE:
        print('NO TASKS CURRENTLY ARE AVAILABLE. QUITING :(')
        browser.quit()

    loc_prewrappers = '.wrapper_pre>pre'
    loc_messages = '.row'
    loc_buyer_messages = '.messages>.row:not(.seller)>.message.text'
    loc_seller_messages = '.messages>.row.seller>.message.text'

    object_info = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, loc_prewrappers))
        )
    # name, description = object_info[0].text, object_info[2].text
    name, description = object_info[0].text, object_info[2].text

    all_messages = buyer_messages = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, loc_messages))
        )

    buyer_messages = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, loc_buyer_messages))
        )
    seller_messages = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, loc_seller_messages))
        )

    #'*Отправлен файл*'
    # res_descr = 'Описание:\n'+name+'\n'+description+'\nКонец описания\n\n'
    res_descr = name+'\nОписание:\n'+description
    res_chat = 'Чат пользователей:\n'
    i_buyer = 0; i_seller = 0;
    for elem in all_messages:
        if 'seller' in elem.get_attribute('class').split():
            cur_msg = seller_messages[i_seller].text
            i_seller += 1
            if cur_msg == '*Отправлен файл*':
                continue
            res_chat += 'Продавец: ' + cur_msg +'\n'
        else:
            cur_msg = buyer_messages[i_buyer].text
            i_buyer += 1
            if cur_msg == '*Отправлен файл*':
                continue
            res_chat += 'Покупатель: ' + cur_msg +'\n'

    if len(res_descr+res_chat) > GPT_MSG_MAX_LEN:
        print("Too long message detected. Message is cut to needed size!")
        amount_to_delete = len(res_descr+res_chat) - GPT_MSG_MAX_LEN
        res_descr = res_descr[:len(res_descr)-amount_to_delete]
    res_descr += '\nКонец описания\n\n'
    res_chat += 'Конец чата\n\nВыбери нужный ответ, учитывая инструкцию:\n1) Да\n2) Нет\n3) Чат неинформативный\nВ ответе напиши только цифру'
    return res_descr + res_chat

def avito_get_question_ramis():
    #First, check if message is ok -> we have question on project
    loc_page_message = '.message'
    message_text = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, loc_page_message))).text
    if message_text == AVITO_NO_TASKS_MESSAGE:
        print('NO TASKS CURRENTLY ARE AVAILABLE. QUITING :(')
        browser.quit()

    loc_prewrappers = '.wrapper_pre>pre'
    loc_messages = 'main>div>:nth-child(2)>:nth-child(3)>div>:nth-child(14)>div>div>*>pre'

    object_info = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, loc_prewrappers))
    )
    # name, description = object_info[0].text, object_info[2].text
    price, description = object_info[1].text, object_info[2].text

    all_messages_doubles = buyer_messages = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, loc_messages))
    )

    res_descr = 'Цена:\n'+price+'\nОписание:\n'+description+'\nКонец описания\n\n'
    res_chat = 'Чат пользователей:\n'
    for i in range(0, len(all_messages_doubles), 2):
        first, second = all_messages_doubles[i].text, all_messages_doubles[i+1].text
        if first != '': #buyer message
            if first == '*Отправлен файл*':
                continue
            res_chat += 'Покупатель: ' + first + '\n'
        else: #Seller message
            if first == '*Отправлен файл*':
                continue
            res_chat += 'Продавец: ' + second + '\n' 
    res_chat += 'Конец чата\n\nВыбери ответ, учитывая инструкцию:\nДа - 1\nНет - 2\nЧат неинформативный - 3\nВ ответе напиши только цифру!'
    print(res_descr+res_chat)
    return res_descr + res_chat

def avito_select_and_send_answer(answer_num):
    loc_answer_options = '.answer'
    loc_send_answer_button = 'button'
    object_info = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, loc_answer_options))
    )
    object_info[answer_num].click()
    send_answer_button = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, loc_send_answer_button))
    )
    send_answer_button.click()

def page_scroll_to_element(element):
    browser.execute_script("arguments[0].scrollIntoView();", element)

def chatGPT_edit_last_message(msg):
    loc_edit_message = '.self-end button'
    loc_edit_textarea = 'textarea'
    loc_edit_submit_btn = '.btn-primary'

    loc_edit_btn = '.items-center.text-sm>:nth-child(3)>div>:nth-child(2)>:nth-child(2)>button'

    print('fun1')
    edit_btn_loc = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, loc_edit_btn))
    )
    page_scroll_to_element(edit_btn_loc)
    edit_btn_loc = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, loc_edit_btn))
    )
    
    print(edit_btn_loc.location, edit_btn_loc.is_enabled(), edit_btn_loc.is_displayed(),
          edit_btn_loc.get_attribute('class'))
    
    action.move_to_element(edit_btn_loc).perform()
    #action.move_by_offset(edit_btn_loc.location['x'], edit_btn_loc.location['y']).perform()
    print("MOVED TO!")

    edit_btn_loc = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, loc_edit_btn))
    )

    edit_btn_loc.click()
    print('fun2')   
    browser_wait_all_elements_located(By_Type=By.TAG_NAME, locator=loc_edit_textarea, amount_of_elements_to_wait=2)
    all_textareas = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, loc_edit_textarea))
    )
    print('fun3')
    edit_last_msg_textarea = all_textareas[0]
    chatGPT_ask_ramis(msg, text_area_element=edit_last_msg_textarea, mutliline=True)
    print('fun4')
    edit_submit_btn = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, loc_edit_submit_btn))
    )
    print('fun5')
    edit_submit_btn.click()

def chatGPT_regenerate_last_response():
    loc_stop_generating_btn = '.btn'
    regenerate_response_btn = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, loc_stop_generating_btn))
    )
    regenerate_response_btn.click()
    return chatGPT_wait_for_answer(2, return_ans=True)

def chatGPT_parse_response(msg):
    ans = None
    words = msg.split()
    for word in words:
        if word.isdigit() and 0<int(word)<4:
            return int(word)
        word = word.lower()
        if word in RESPONSE_WORD_TO_NUM:
            return RESPONSE_WORD_TO_NUM[word]
    return ans

from CREDS import GPT_RULES_TEXT, AVITO_NO_TASKS_MESSAGE
browser.get(chatGPT_url)
try:
    if chatGPT_page_ready_to_be_asked():
        chatGPT_ask_ramis(GPT_RULES_TEXT)
        chatGPT_wait_for_answer(1, return_ans=False)
    #This fun creates new tab and switches to it
    avito_try_login()
    cur_question = avito_get_question_ramis()
    browser.switch_to.window(browser.window_handles[0])
    if chatGPT_page_ready_to_be_asked():
        chatGPT_ask_ramis(cur_question)
    chatGPT_last_response = chatGPT_wait_for_answer(2, return_ans=True).text
    chatGPT_ans_parsed = chatGPT_parse_response(chatGPT_last_response)
    while chatGPT_ans_parsed is None:
        #Regenerate response!!!
        chatGPT_last_response = chatGPT_regenerate_last_response()
        chatGPT_ans_parsed = chatGPT_parse_response(chatGPT_last_response)
    print("RESPONSE", chatGPT_last_response, "RES:", chatGPT_ans_parsed)
    browser.switch_to.window(browser.window_handles[1])
    #avito_select_and_send_answer(chatGPT_resolution)
    while input().lower() == 'next':
        cur_question = avito_get_question_ramis()
        browser.switch_to.window(browser.window_handles[0])
        chatGPT_edit_last_message(cur_question)
        chatGPT_resolution = int(chatGPT_wait_for_answer(total_answers=2, return_ans=True).text)
        browser.switch_to.window(browser.window_handles[1])
except:
    raise Exception("Some error raised!")
finally:
    # ожидание чтобы визуально оценить результаты прохождения скрипта
    time.sleep(10)
    # закрываем браузер после всех манипуляций
    browser.quit()