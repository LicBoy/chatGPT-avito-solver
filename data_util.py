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
    
    #TODO: DON'T COPY FILES WHICH ARE ALREADY IN FOLDER = INCREASE SPEED
    def move_jsons_to_folder(self, input_folder, output_folder, clean_jsons=True, copy=False):
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
                

    def json_to_csv_row(self, json, test=False):
        oid = json["oid"]
        ad_name = json["ad_name"]
        ad_descr = json["ad_descr"]
        messages = json.get("messages", [])
        text = f'Описание: {ad_name} {ad_descr} |'
        text += " Чат: "
        for message in messages:
            msg_from = 'Продавец' if message["from"] == 'seller' else 'Покупатель'
            text += f'{msg_from}: {message["msg"]}; '

        text = self.fix_many_tokens(oid, text, ad_name)
        if test:
            return [oid, text]
        else:
            category = json["answers"]["correct"] if "correct" not in json["answers"]["correct"] else json["answers"]["correct"]["correct"]
            return [oid, category, text]

    # 2048 for rubert-tiny2, 512 for rubert-tiny
    def fix_many_tokens(self, oid:str, text: str, ad_name:str, max_tokens:int=2048):
        max_tokens -= 2 # 2 tokens are used for start and end of text
        text_words = text.split(' ')
        if len(text_words) > max_tokens:
            print(f"{oid} Text is too long (more than {max_tokens} tokens!). Reduce it.")
            words_remove_amount =  len(text_words) - max_tokens
            ad_name_len = len(ad_name.split(' '))+1 #+1 because of "Описание:"
            index_of_chat_start = text_words.index('Чат:')

            if (index_of_chat_start-ad_name_len) > words_remove_amount:
                del text_words[ad_name_len:ad_name_len+words_remove_amount]
            else:
                words_remove_amount -= (index_of_chat_start-ad_name_len)
                last_actor_msg_index = text_words.index('Чат:')+1
                cur_actor_msg_index = last_actor_msg_index + 2
                
                for i in range(cur_actor_msg_index, len(text_words)):
                    if i == len(text_words)-1: 
                        #Text is TOOOO LONG! Can't cut to {max_tokens} amount!
                        raise Exception(f"Chat {oid}: #Text is TOOOO LONG! Can't cut to {max_tokens} amount!")
                    if text_words[i] in ['Продавец', 'Покупатель']:
                        last_actor_msg_index = cur_actor_msg_index
                        cur_actor_msg_index = i

                        words_remove_amount -= (cur_actor_msg_index - last_actor_msg_index)
                        if words_remove_amount < 0:
                            break
                del text_words[text_words.index('Чат:')+1:ad_name_len+cur_actor_msg_index+1]          
        return text

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