import pandas as pd

def get_text_lengths(csv_file, column_name):
    # Read the CSV file and extract the desired column
    df = pd.read_csv(csv_file)
    column = df[column_name]
    
    # Initialize variables
    minimum_length = float('inf')
    maximum_length = float('-inf')
    cumulative_length = 0
    total_values = 0
    
    # Iterate through the text values and calculate lengths
    for text in column:
        length = len(str(text))
        cumulative_length += length
        total_values += 1
        minimum_length = min(minimum_length, length)
        maximum_length = max(maximum_length, length)
    
    # Calculate the average length
    average_length = cumulative_length / total_values
    
    # Return the results
    return minimum_length, average_length, maximum_length

CSV_PATH = "model_preds_history\\run_2\\train.csv"
COLUMN_NAME = 'text'

def count_from_text(text):
    MSG_MIN_LEN = 84
    MSG_AVG_LEN = 986
    MSG_MAX_LEN = 10212

    MAX_DISP = 5.
    MIN_DISP = 0.2
    
    text_len = len(text)
    print(f"DISPERSIONS: {MIN_DISP} - AVG=1 - {MAX_DISP}")
    res_disp = text_len / MSG_AVG_LEN
    res_disp = min(res_disp, MAX_DISP)
    res_disp = max(res_disp, MIN_DISP)
    print(f"CALCULATED DISP = {res_disp}")

TEXT_TEST =" Описание: Запчасти bmx Продам запчасти на bmx всё в хорошем состоянии Рама WTP Trust 2019 в 21 ростовке перья 13 в полностью задвинутом положении рулевой стакан 127мм стендовер 9 инвест каст дропауты с фризеровкой и интегрированными натяжителями цепи баттинг Цена 7000 рублей Вилка WTP Recore 2009 года 25 выбег шток 159мм Цена 1500 рублей За доп фото и вопросами в лс Пишите только по делу на тупые вопросы не отвечаю Продаëтся только то что тут есть не дербан| Чат: Покупатель:  Здравствуйте; Продавец:  Здравствуйте; Покупатель:  У вас есть колесо переднее; Покупатель:  С покрышкой и камерой; Продавец:  Уже продал;"
count_from_text(TEXT_TEST)
# res = get_text_lengths(CSV_PATH, COLUMN_NAME)
# min, avg, max = res[0], res[1], res[2]
# print(f"MIN: {min} | AVG: {avg} | MAX: {max}")