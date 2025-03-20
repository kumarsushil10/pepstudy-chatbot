import sys
from utils.exception import CustomException
from utils.logger import logging

from flask import Flask, request, jsonify
from .rag import RAGSystem

class Api:
    def __init__(self,path_dir):
        self.path_dir = path_dir
        self.app = Flask(__name__)
        self.rag_system = RAGSystem(self.path_dir)

    def start(self):
        try:
            logging.info("Chatbot start method called")
            @self.app.route("/query", methods=["POST"])
            def query():
                try:
                    logging.info("Chatbot start-query method called")

                    data = request.json
                    logging.info(f"requested json = {data}")

                    input = data.get("input", "")
                    logging.info(f"input from json = {input}")

                    answer = self.rag_system.generator(input)
                    logging.info(f"response from RAGSystem generator {answer}")
                    
                    return jsonify({"answer": answer})
                
                except Exception as e:
                    logging.error(f"Error in Chatbot start-query : {str(e)}")
                    raise CustomException(e,sys)
                


            @self.app.route("/chat", methods=["POST"])
            def chatAI():
                try:
                    logging.info("Chatbot start-chatAI method called")

                    data = request.json
                    logging.info(f"requested json = {data}")

                    input = data.get("input", "")
                    logging.info(f"input from json = {input}")

                    session_id = data.get("session_id", "")
                    logging.info(f"session_id from json = {session_id}")

                    answer = self.rag_system.invoke_and_save(session_id,input)
                    # logging.info(f"response from RAGSystem generator_with_memory = {answer}")
                    
                    return jsonify({
                        "session_id": session_id,
                        "response": answer})
                
                except Exception as e:
                    logging.error(f"Error in Chatbot start-chatAI : {str(e)}")
                    raise CustomException(e,sys)
                
            self.app.run(debug=True,host="0.0.0.0", port=5000)

        except Exception as e:
            logging.error(f"Error in Chatbot start : {str(e)}")
            raise CustomException(e,sys)