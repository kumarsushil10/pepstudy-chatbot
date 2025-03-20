# RAG Chatbot

This project implements a Retrieval-Augmented Generation (RAG) system with a chatbot interface.

## Setup

1. Run the setup script to create the conda environment and install dependencies:

    ```bash
    setup.bat
    ```

2. Start the application:

    ```bash
    python src/main.py
    ```

## Usage

Send a POST request to `http://localhost:5000/query` with a JSON payload containing the question.