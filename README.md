# Avito Chat Labeling Automation  

## 📌 Project Overview  
This project automates the classification of buyer-seller chat messages on Avito. Initially, as part of a part-time data labeling and collecting job, I manually assigned answer classes to chat messages. To streamline and automate this process, I developed a machine learning model capable of predicting the correct answer class based on chat data.  

## 🚀 Features  
- **Data Collection**: A JavaScript script for Tampermonkey was used to capture and store labeled chat data during work.  
- **Model Training**: A lightweight text classification model from Kaggle ([source](https://www.kaggle.com/code/mikhailma/russian-text-classification-in-15-minute-pl-0-95)) was trained on the collected dataset.  
- **Automated Labeling**: The system identifies buttons and responses on the Avito labeling interface using Selenium WebDriver and applies the trained model to classify chats in a fully automated mode.  

## ⚙️ Technology Stack  
- **Data Collection**: JavaScript (Tampermonkey extension)  
- **Machine Learning**: Python, Kaggle, NLP text classification model  
- **Automation**: Selenium WebDriver  

## 🎯 Why This Project?  
Manually labeling chats was time-consuming and repetitive. This project was an opportunity to:  
- Reduce manual effort through automation.  
- Explore and implement machine learning for text classification.  
- Gain hands-on experience with web scraping and automation tools.  

## 🛠️ How It Works  
1. The Tampermonkey script logs manually labeled answers during work.  
2. Collected data is used to train a neural network for text classification.  
3. The trained model is integrated with Selenium, which automatically classifies chat messages based on predicted labels.  
