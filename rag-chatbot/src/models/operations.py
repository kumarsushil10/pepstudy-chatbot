import sys
from .database import get_db
from .chat_history import Session, Message
from sqlalchemy.exc import SQLAlchemyError
from utils.logger import logging
from utils.exception import CustomException

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# Function to save a single message
def save_message(session_id: str, role: str, content: str):
    logging.info("save_message method called")
    db = next(get_db())
    try:
        session = db.query(Session).filter(Session.session_id == session_id).first()
        logging.info(f"session info  = {session}")
        if not session:
            logging.info("session not found")
            session = Session(session_id=session_id)
            db.add(session)
            db.commit()
            db.refresh(session)
            logging.info(f"session created = {session}")

        db.add(Message(session_id=session.id, role=role, content=content))
        db.commit()
        logging.info(f"message saved with session = {session_id} role = {role} and content = {content}")
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error in save_message : {str(e)}")
        raise CustomException(e, sys)
    except Exception as e:
        logging.error(f"Error in save_message : {str(e)}")
        raise CustomException(e, sys)
    finally:
        db.close()

# Function to load chat history
def load_session_history(session_id: str) -> BaseChatMessageHistory:
    logging.info("load_session_history method called")
    db = next(get_db())
    chat_history = ChatMessageHistory()
    logging.info(f"chat_history created = {chat_history}")
    try:
        session = db.query(Session).filter(Session.session_id == session_id).first()
        logging.info(f"session info  = {session}")
        if session:
            for message in session.messages:
                chat_history.add_message({"role": message.role, "content": message.content})
        logging.info(f"chat_history load_session_history loaded with session = {session_id}")
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error in loading session history: {str(e)}")
        raise CustomException(e, sys)
    except Exception as e:
        logging.error(f"Error in loading session history: {str(e)}")
        raise CustomException(e, sys)
    finally:
        db.close()

    return chat_history

store = {}
# Modify the get_session_history function to use the database
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    logging.info("get_session_history method called")
    if session_id not in store:
        store[session_id] = load_session_history(session_id)
    logging.info(f"chat_history get_session_history loaded with session = {session_id}")
    return store[session_id]

# Ensure you save the chat history to the database when needed
def save_all_sessions():
    logging.info("save_all_sessions method called")
    for session_id, chat_history in store.items():
        for message in chat_history.messages:
            save_message(session_id, message["role"], message["content"])
        logging.info(f"chat_history save_all_sessions saved with session = {session_id}")
    logging.info(f"chat_history save_all_sessions saved all sessions")
