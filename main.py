from selenium import webdriver
from avito_creds import LOGIN, PASSWORD
from pageobjects.avito_project_page import AvitoProjectPage
from data_util import DataUtil
import time, random, os

import numpy as np
import pandas as pd
from tqdm import tqdm

import torch
from torch.utils.data import DataLoader
from transformers import BertTokenizer

AVITO_URL = "https://centiman.avito.ru/"
browser = webdriver.Chrome()
avito_page = AvitoProjectPage(AVITO_URL, browser, {"login" : LOGIN, "password" : PASSWORD}, 739)

### PREPARE ###
tokenizer_path = 'cointegrated/rubert-tiny'
tokenizer = BertTokenizer.from_pretrained(tokenizer_path)

CLASSES = ['Да', 'Нет', 'Чат неинформативный']
labels = dict(zip(CLASSES, range(len(CLASSES))))

class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, df, tokenizer, phase='test'):
        self.phase = phase
        
        if self.phase == 'train':
            self.labels = [labels[label] for label in df['category']]
        elif self.phase == 'test':
            self.oid = [oid for oid in df['oid']]
            
        self.texts = [tokenizer(text, 
                               padding='max_length', max_length = 512, truncation=True,
                                return_tensors="pt") for text in df['text']]

    def classes(self):
        return self.labels

    def __len__(self):
        if self.phase == 'train':
            return len(self.labels)
        elif self.phase == 'test':
            return len(self.oid)

    def get_batch_labels(self, idx):
        return np.array(self.labels[idx])
    
    def get_batch_oid(self, idx):
        return np.array(self.oid[idx])

    def get_batch_texts(self, idx):
        return self.texts[idx]

    def __getitem__(self, idx):
        if self.phase == 'train':
            batch_texts = self.get_batch_texts(idx)
            batch_y = self.get_batch_labels(idx)
            return batch_texts, batch_y
        elif self.phase == 'test':
            batch_texts = self.get_batch_texts(idx)
            batch_oid = self.get_batch_oid(idx)
            return batch_texts, batch_oid

def inference(model, dataloader):
    all_oid = []
    all_labels = []
    label_prob = []
    
    # model.cuda()
    model.eval()
    with torch.no_grad():
        for test_input, test_oid in tqdm(dataloader):
            # test_oid = test_oid.cuda()
            mask = test_input['attention_mask'] #.cuda()
            input_id = test_input['input_ids'].squeeze(1) #.cuda()
            output = model(input_id, mask)
            all_oid.extend(test_oid)
            all_labels.extend(torch.argmax(output[0].softmax(1), dim=1))
            
            for prob in output[0].softmax(1):
                label_prob.append(prob)
        return ([oid.item() for oid in all_oid], [CLASSES[labels] for labels in all_labels], label_prob)

MODEL_NAME = "BertClassifier_last.pt"
inference_model = torch.load(f'{MODEL_NAME}', map_location=torch.device('cpu'))
avito_page.open()
avito_page.login()
avito_page.choose_project(791)
### MAIN LOOP ###

def get_cur_disp(text):
    MSG_MIN_LEN = 84
    MSG_AVG_LEN = 986
    MSG_MAX_LEN = 10212
    MAX_DISP = 2.5
    MIN_DISP = 0.6
    text_len = len(text)
    res_disp = text_len / MSG_AVG_LEN
    res_disp = min(res_disp, MAX_DISP)
    res_disp = max(res_disp, MIN_DISP)
    return res_disp

def plus_or_minus():
    if random.random() > 0.5:
        return True  # Represents the outcome with a 0.5 chance
    else:
        return False

from datetime import datetime
def save_model_predict_log(json_data, base_output_path="working\\model_predicts\\"):
    current_date = datetime.now().strftime('%d-%m-%Y')
    output_path = base_output_path + f"Predicts_{current_date}\\"
    os.makedirs(output_path, exist_ok=True)
    data_util.save_json(json_data, output_path + f"question_{json_data['oid']}_predict_log.json")

SELECT_ANS_BASE_TIME = 15
data_util = DataUtil()

while True:
    try: 
        chat_info = avito_page.get_chat_info()
    except:
        if avito_page.tasks_ended()== True:
            print(F"CHATS ENDED.")
            #No tasks, exit or refresh page until tasks are here
            break
        else:
            raise Exception(f"Couldn't get page info, unrecognized behaviour! Check Page!")
    chat_info = data_util.clean_json(chat_info)
    #check amount of msgs of buyer and seller
    buyer_len, seller_len = 0, 0
    for msg in chat_info['messages']:
        if msg['from'] == 'buyer':
            buyer_len += 1
        else:
            seller_len += 1

    label = None
    if buyer_len == 0 or seller_len == 0:
        print(f"No Message from one side, choosing '{CLASSES[2]}'")
        label = CLASSES[2]
    else:
        data_util.jsons_to_csv("working\\cur_question.csv", input_jsons=[chat_info], test=True)
        cur_question_csv = pd.read_csv('working\\cur_question.csv')
        test_dataset = CustomDataset(cur_question_csv, tokenizer, phase='test')
        test_dataloader = DataLoader(test_dataset, batch_size=1)
        inference_result = inference(inference_model, test_dataloader)

        oid = [i for i in inference_result[0]]
        labels = [i for i in inference_result[1]]
        prob = [i for i in inference_result[2]]

        oid = oid[0]
        label = labels[0]
        print("MODEL PREDICT:", oid, label)
        # correct_label = int(input("Input correct label:"))
        # correct_label = CLASSES[correct_label]

    # Wait time
    cur_disp = get_cur_disp(cur_question_csv['text'][0])
    cur_select_ans_random_time = random.uniform(0., cur_disp)
    cur_select_ans_random_time = cur_select_ans_random_time if plus_or_minus() else -cur_select_ans_random_time
    cur_select_ans_time = SELECT_ANS_BASE_TIME*cur_disp + cur_select_ans_random_time

    print(f"Time random wait: dispersion = {cur_disp}, random wait time = {cur_select_ans_time}")
    chat_info["predict_info"] = {}
    chat_info["predict_info"]["predict_label"] = label
    # chat_info["predict_info"]["correct_label"] = correct_label
    now_datetime = datetime.now().strftime('%d-%m-%Y, %H:%M:%S')
    chat_info["predict_info"]["predict_time"] = now_datetime
    chat_info["predict_info"]["random_wait"] = cur_select_ans_time
    with open('wait_times.txt', 'a+') as file:
        file.write(f'{now_datetime} {oid} {cur_select_ans_time}\n')
    save_model_predict_log(chat_info)

    time.sleep(cur_select_ans_time)
    avito_page.click_answer(label)
    time.sleep(0.5)
    avito_page.click_submit_btn()

    #Look for "SomeError" msg, if appeared, try to resubmit button
    while avito_page.some_error_msg_appeared():
        print(f"'Some Error' Appeared, trying to choose answer again...")
        time.sleep(10)
        browser.refresh()
        if chat_info["oid"] == avito_page.get_question_number():
            avito_page.click_answer(label)
            avito_page.click_submit_btn()     
    avito_page.wait_next_question_load(int(chat_info["oid"]))
    # screen_save_path = f"working\\crash_screenshots\\crash_{chat_info['oid']}_{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}.png"
    # print(f"Some error occured, saving screen to {screen_save_path}")
    # browser.save_screenshot(screen_save_path)
    # break

#END
time.sleep(3)
browser.quit()