:: filepath: /C:/Users/kmrsu/OneDrive/Desktop/workSpace/pepstudy_chatbot/rag-chatbot/setup.bat
@echo off

:: Create a conda environment
conda create -n pepstudy_chatbot python=3.9 -y

:: Activate the conda environment
call conda activate pepstudy_chatbot

:: Install the required packages
pip install -r requirements.txt

echo Setup complete. Conda environment created and dependencies installed.