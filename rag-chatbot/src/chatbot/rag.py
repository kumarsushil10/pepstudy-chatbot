import sys
from utils.exception import CustomException
from utils.logger import logging
from models.operations import get_session_history, save_message

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_ollama import OllamaLLM
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.runnables.history import RunnableWithMessageHistory

class RAGSystem:
    def __init__(self, path_dir):
        self.path_dir = path_dir
        self.retriever = self.indexing()
        self.llm = OllamaLLM(model='llama3.2')
        self.qa_system_prompt = (
            """ 
                You are an AI assistant designed to help students from Class 6 to Class 12.
                Your goal is to provide clear, accurate, and well-structured answers based on the given context.
                Carefully analyze the context before answering, and explain step by step in a simple and understandable way.
                If necessary, break complex concepts into smaller parts to enhance student comprehension.
                <context> {context} </context> """
        )
        self.contextualize_q_system_prompt = (
            """
            Given a chat history and the latest user question, rewrite the question 
            so that it is fully self-contained and understandable without previous context. 
            - Preserve the original intent and meaning.  
            - If no changes are needed, return the question as is.  
            - Do NOT provide an answer. """
        )

    def indexing(self):
        try:
            logging.info("RAGSystem indexing method called")
            loader = PyPDFDirectoryLoader(self.path_dir)
            documents = loader.load()
            logging.info("file loading succesfully completed")

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splitted_documents = text_splitter.split_documents(documents=documents)
            logging.info("Document splitter succesfully completed")

            embeddings = OllamaEmbeddings(model='llama3.2')
            faiss_db = FAISS.from_documents(documents=splitted_documents, embedding=embeddings)
            logging.info("Embedded and stored in FAISS vector store succesfully completed")

            retriever = faiss_db.as_retriever()
            return retriever
        
        except Exception as e:
            logging.error(f"Error in RAGSystem indexing : {str(e)}")
            raise CustomException(e, sys)

    def generator(self, input):
        try: 
            logging.info("RAGSystem generator method called")
            chat_prompt = ChatPromptTemplate.from_messages([
                ("system", self.qa_system_prompt),
                ("human", "{input}")
            ])
            logging.info("chat prompt creation succesful")

            prompt_llm_chain = create_stuff_documents_chain(llm=self.llm, prompt=chat_prompt)
            logging.info("document_chain created")

            retrieval_chain = create_retrieval_chain(self.retriever, prompt_llm_chain)
            logging.info("retriever chain created")

            response = retrieval_chain.invoke({"input": input})
            logging.info(f"Generated response = {response} ")
            return response["answer"]
        except Exception as e:
            logging.error(f"Error in RAGSystem generator : {str(e)}")
            raise CustomException(e, sys)

    def generator_with_memory(self, session_id, input):
        try:
            logging.info("RAGSystem generator_with_memory method called")
            contextualize_q_prompt = ChatPromptTemplate.from_messages([
                ("system", self.contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ])

            history_aware_retriever = create_history_aware_retriever(self.llm, self.retriever, contextualize_q_prompt)
            logging.info("history_aware_retriever created")

            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", self.qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ])
            question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
            logging.info("question_answer_chain created")

            rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
            logging.info("rag_chain created")

            conversational_rag_chain = RunnableWithMessageHistory(
                rag_chain,
                get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer",
            )
            logging.info("conversational_rag_chain created")

            response = conversational_rag_chain.invoke(
                {"input": input},
                config={"configurable": {"session_id": session_id}} 
            )
            # logging.info(f"Generated response with memory = {response} ")

            return response["answer"]
        except Exception as e:
            logging.error(f"Error in RAGSystem generator_with_memory : {str(e)}")
            raise CustomException(e, sys)

    def invoke_and_save(self, session_id, input_text):
        try:
            logging.info("RAGSystem invoke_and_save method called")
            save_message(session_id, "human", input_text)
            logging.info(f"human input message saved")
            response = self.generator_with_memory(session_id, input_text)
            logging.info(f"response from generator_with_memory = {response}")
            save_message(session_id, "ai", response)
            logging.info(f"ai response message saved")
            return response
        except Exception as e:
            logging.error(f"Error in RAGSystem invoke_and_save : {str(e)}")
            raise CustomException(e, sys)