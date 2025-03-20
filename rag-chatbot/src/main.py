import atexit
from utils.exception import CustomException
from utils.logger import logging
from chatbot.api import Api
from models.database import Base, engine
from models.operations import save_all_sessions

def main():
    logging.info("main method called")
    Base.metadata.create_all(engine)
    path_dir = r"C:\Users\kmrsu\OneDrive\Desktop\workSpace\pepstudy_chatbot\rag-chatbot\src\data"
    # path_dir = r"..\data"
    api = Api(path_dir=path_dir)
    api.start()

if __name__ == "__main__":
    atexit.register(save_all_sessions)
    main()