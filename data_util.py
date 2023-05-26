import json, os, re, csv, random
import pandas as pd

class DataUtil():
    ascii_codes_regex = r"\\[a-zA-Z0-9]{5}"
    legal_chars_regex = r"[^-\w\s\u0400-\u04FF\u0020\r\n.,!?()%$@+=:;`'\"]"

    def save_json(self, data, save_path):
        with open(save_path, 'w+', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        return json_data

    def clean_json(self, json_data):
        for key in ['ad_name', 'ad_descr']:
            json_data[key] = self.filter_text(json_data[key])
        json_data['messages'] = self.clean_json_messages(json_data['messages'])
        return json_data

    def clean_json_messages(self, msgs_array):
        replaced_buyer_msg_once = False
        replaced_seller_msg_once = False
        msg_indeces_to_delete = []
        for i in range(len(msgs_array)):
            cur_msg_text = msgs_array[i]['msg']
            filtered_text = self.filter_text(cur_msg_text)
            if filtered_text == '':
                if not replaced_buyer_msg_once and msgs_array[i]['from'] == 'buyer':
                    replaced_buyer_msg_once = True
                    msgs_array[i]['msg'] = '.'
                elif not replaced_seller_msg_once and msgs_array[i]['from'] == 'seller':
                    replaced_seller_msg_once = True
                    msgs_array[i]['msg'] = '.'
                else:
                    msg_indeces_to_delete.append(i)
            else:
                msgs_array[i]['msg'] = filtered_text
        delete_amount = 0
        for index in msg_indeces_to_delete:
            msgs_array.pop(index - delete_amount)
            delete_amount += 1
        return msgs_array

    def filter_text(self, text):
        filtered_text = re.sub(self.ascii_codes_regex, "", text)
        filtered_text = re.sub(self.legal_chars_regex, "", filtered_text)
        return filtered_text.strip()
    
    def move_jsons_to_folder(self, input_folder, output_folder, clean_jsons=True, copy=True):
        if input_folder == "C:\\Users\\user\\Downloads\\chats" and copy == False:
            raise Exception(f"Trying to Cut Files from {input_folder}! Can't lose base questions dataset!")
        if input_folder == output_folder and copy == False:
            copy = True
        json_files = [file for file in os.listdir(input_folder) if file.endswith('.json') and file.startswith('question')]
        os.makedirs(output_folder, exist_ok=True)
        for filename in json_files:
            input_file = os.path.join(input_folder, filename)
            json_data = self.load_json(input_file)
            if clean_jsons == True:
                json_data = self.clean_json(json_data)
            save_path = os.path.join(output_folder, os.path.basename(input_file))
            if os.path.exists(save_path): #File already exists in output folder
                continue
            self.save_json(json_data, save_path)
            if copy == False:
                os.remove(input_file)

    def add_oid_to_jsons(self, input_folder):
        json_files = [file for file in os.listdir(input_folder) if file.endswith('.json') and file.startswith('question')]
        for filename in json_files:
            input_file = os.path.join(input_folder, filename)
            json_data = self.load_json(input_file)

            oid = filename.split('_')[1].split('.')[0]
            if ("oid" in json_data and json_data["oid"] != oid) or "oid" not in json_data:
                if ("oid" in json_data and json_data["oid"] != oid):
                    print(f"!!! FILE {filename} in {input_folder} had other 'oid'. Replaced with actual one")
                json_data["oid"] = oid
                save_path = os.path.join(input_folder, os.path.basename(input_file))
                self.save_json(json_data, save_path)

    def jsons_to_csv(self, output_file, input_folder=None, input_jsons=None, random_select=None, test=False):
        if input_folder is not None:
            json_files = [file for file in os.listdir(input_folder) if file.endswith('.json') and file.startswith('question')]
            if isinstance(random_select, int) and random_select > 0:
                json_files = random.sample(json_files, random_select)
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as csv_file:
                writer = csv.writer(csv_file)
                column_names_row = ["oid", "text"] if test else ["oid", "category", "text"]
                writer.writerow(column_names_row)
                for filename in json_files:
                    input_file = os.path.join(input_folder, filename)
                    json_data = self.load_json(input_file)
                    cur_row = self.json_to_csv_row(json_data, test)
                    writer.writerow(cur_row)
        elif input_jsons is not None:
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as csv_file:
                writer = csv.writer(csv_file)
                column_names_row = ["oid", "text"] if test else ["oid", "category", "text"]
                writer.writerow(column_names_row)
                for json in input_jsons:
                    cur_row = self.json_to_csv_row(json, test)
                    writer.writerow(cur_row)
                

    def json_to_csv_row(self, json: dict, test: bool=False):
        oid = json["oid"]
        ad_name = json["ad_name"]
        ad_descr = json["ad_descr"]
        messages = json.get("messages", [])
        category = None
        if "answers" in json:
            category = json["answers"]["correct"] if "correct" not in json["answers"]["correct"] else json["answers"]["correct"]["correct"]

        text_start_pattern = 'Описание: <AD_NAME> <AD_DESCR> | Чат:'
        fixed_json = self.fix_many_tokens(oid, text_start_pattern, ad_name, ad_descr, messages)
        ad_name = fixed_json["ad_name"]
        ad_descr = fixed_json["ad_descr"]
        if ad_descr == '' or ad_descr is None:
            text_start_pattern = 'Описание: <AD_NAME> | Чат:'
        messages = fixed_json.get("messages", [])
        text = text_start_pattern.replace('<AD_NAME>', ad_name).replace('<AD_DESCR>', ad_descr)
        for message in messages:
            msg_from = 'Продавец' if message["from"] == 'seller' else 'Покупатель'
            text += f' {msg_from}: {message["msg"]};'
        if test:
            return [oid, text]
        else:
            return [oid, category, text]

    # 2048 for rubert-tiny2, 512 for rubert-tiny
    def fix_many_tokens(self, 
            oid: str, text_pattern: str, ad_name: str, ad_descr: str, msgs: list, 
            descr_to_msg_remove_ratio : tuple[int, int]=(3, 1), 
            max_tokens: int=2048):
        def count_full_text_len(text_pattern: str, ad_name: str, ad_descr: str, msgs: list[dict]):
            if text_pattern.count('<') != text_pattern.count('>'):
                raise Exception(f'Not equal amount of <> in text pattern!')
            start_text_len = len(text_pattern.split(' ')) - text_pattern.count('<') + len(ad_name.split(' ')) + len(ad_descr.split(' '))
            ad_msgs_len = 0
            for msg in msgs:
                msg = msg['msg']
                msg_len = len(msg.split(' '))
                ad_msgs_len += msg_len + 1 # + 'Buyer:' or 'Seller:'
            return start_text_len + ad_msgs_len

        max_tokens -= 2 # 2 tokens are used for start and end of text
        text_token_amount = count_full_text_len(text_pattern, ad_name, ad_descr, msgs)
        if text_token_amount > max_tokens:
            print(f'Chat {oid}: Got {text_token_amount}, when max token amount={max_tokens}. Reducing text.')
            descr_remove_ratio = descr_to_msg_remove_ratio[0]
            msgs_remove_ratio = descr_to_msg_remove_ratio[1]
            tokens_tobe_removed = text_token_amount - max_tokens

            ad_descr_list = ad_descr.split(' ')
            MIN_MSGS_AMOUNT = 5
            tokens_tobe_removed_prev = tokens_tobe_removed
            while tokens_tobe_removed > 0:
                if len(ad_descr_list) > 0:
                    for _ in range(descr_remove_ratio):
                        ad_descr_list.pop()
                        tokens_tobe_removed -= 1
                        if tokens_tobe_removed <= 0 or len(ad_descr_list) == 0:
                            break
                if len(msgs) > MIN_MSGS_AMOUNT:
                    for _ in range(msgs_remove_ratio):
                        tokens_in_msg = len(msgs[0]['msg'].split(' '))
                        del msgs[0]
                        tokens_tobe_removed -= (tokens_in_msg + 1) # +1 because of 'Buyer:' or 'Seller:'
                        if tokens_tobe_removed <= 0 or len(msgs) <= MIN_MSGS_AMOUNT:
                            break
                if tokens_tobe_removed_prev == tokens_tobe_removed:
                    crash_save_path = f"working\crash_{max_tokens}tokens\question_{oid}_text.json"
                    self.save_json(data={
                        "oid" : oid,
                        "ad_name" : ad_name,
                        "ad_descr" : ' '.join(ad_descr_list),
                        "messages" : msgs
                    },
                    save_path=crash_save_path)
                    raise Exception(f"Tried to reduce {oid} question's tokens. WENT INTO INFINITE LOOP, CHECK MANUALLY!\nSaved crash info to {crash_save_path}")
                tokens_tobe_removed_prev = tokens_tobe_removed
            
            ad_descr = ' '.join(ad_descr_list)
        return {
            "ad_name" : ad_name,
            "ad_descr" : ad_descr,
            "messages" : msgs
        } 

    def update_csv_with_labels(self, preds_csv, json_folder):
        def get_correct_answer(json_file_path):
            data = self.load_json(json_file_path)
            return data['answers']['correct'] if "correct" not in data['answers']['correct'] else data['answers']['correct']["correct"]

        df = pd.read_csv(preds_csv)
        df['correct'] = ''
        for index, row in df.iterrows():
            oid = row['oid']
            json_files = [filename for filename in os.listdir(json_folder) if (filename.startswith(f"question_{oid}") and filename.endswith(".json"))]

            if len(json_files) > 0:
                json_file_name = json_files[0]
                json_file_path = os.path.join(json_folder, json_file_name)

                correct_answer = get_correct_answer(json_file_path)
                df.at[index, 'correct'] = correct_answer
        df.to_csv(preds_csv, index=False, encoding='utf-8-sig')

    def count_correct_preds(self, csv_path='preds.csv', preds_col='predict', targets_col='correct'):
        df = pd.read_csv(csv_path)

        filtered_df = df[df[preds_col] != df[targets_col]]
        # Get the 'oid' values from the filtered rows
        oid_values = filtered_df['oid'].tolist()
        print(f"Wrong predictions:", oid_values)

        correct_predictions = (df[preds_col] == df[targets_col]).sum()
        total_predictions = len(df)
        percent_correct = (correct_predictions / total_predictions) * 100
        return (percent_correct, correct_predictions)