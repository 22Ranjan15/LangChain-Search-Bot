# LangChain Search Bot with Streamlit UI

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Built with Streamlit](https://img.shields.io/badge/Built_with-Streamlit-red.svg)](https://streamlit.io)
[![Powered by LangChain](https://img.shields.io/badge/Powered_by-LangChain-purple.svg)](https://www.langchain.com)

## Overview

This project is a web application built using Streamlit that provides an interactive chat interface powered by LangChain and Google Gemini large language models. The chatbot can leverage external tools to answer user queries, including:

* **Web Search:** Using DuckDuckGo to find current information online.
* **Wikipedia:** Querying Wikipedia for encyclopedic knowledge.
* **Arxiv:** Searching the Arxiv repository for scientific papers.

The application requires a user-provided Google Gemini API key for its core functionality.

## Features

* **Interactive Chat:** Real-time conversation interface powered by Streamlit.
* **LLM Integration:** Utilizes Google Gemini models (`gemini-1.5-pro`, `gemini-2.0-flash-lite`, `gemini-2.0-flash`, etc.) via LangChain.
* **Tool Usage:** Employs a LangChain agent (`ZERO_SHOT_REACT_DESCRIPTION`) to intelligently decide when to use search tools.
    * DuckDuckGo Search Integration
    * Wikipedia Query Integration
    * Arxiv Paper Search Integration
* **Secure API Key Handling:** API keys are entered via a password field in the Streamlit sidebar and managed within the user's session state (not stored persistently).
* **Model Selection:** Allows users to choose between available Gemini models via the sidebar.
* **Chat Management:** Displays conversation history and provides an option to clear the chat.
* **Streaming Responses:** Shows the agent's thought process and final response in real-time (using `StreamlitCallbackHandler`).

## Tech Stack

* **Language:** Python 3.10+
* **Web Framework:** Streamlit
* **LLM Framework:** LangChain
* **LLM Service:** Google Gemini API
* **Core Libraries:**
    * `streamlit`
    * `langchain`
    * `langchain-google-genai`
    * `langchain-community` (for tools and utilities)
    * `duckduckgo-search`
    * `wikipedia`
    * `arxiv`

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python:** Version 3.10 or higher.
2.  **pip:** Python package installer (usually comes with Python).
3.  **Google Gemini API Key:** You need an API key from Google AI Studio. You can get one here: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/22Ranjan15/LangChain-Search-Bot.git
    ```

2.  **Create and activate a virtual environment (recommended):**
    * **macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    * **Windows:**
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```

3.  **Install the required dependencies:**
    Create a file named `requirements.txt` in the project root with the following content:
    ```txt
    streamlit
    langchain
    langchain-google-genai
    langchain-community
    duckduckgo-search
    wikipedia
    arxiv
    ```
    Then run:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

* **API Key:** This application requires your Google Gemini API Key to function.
* **How to Provide:**
    1.  Launch the application (see Usage section below).
    2.  The application sidebar will prompt you to enter your API key.
    3.  Paste your key into the "Google Gemini API Key" password field.
    4.  Click the "Save API Key" button.
* **Security:** The API key is stored only in the Streamlit session state for the duration of your browser session. It is **not** saved to disk or embedded in the code. If you close the tab or refresh aggressively, you might need to re-enter it.

## Usage

1.  **Navigate to the project directory** in your terminal (ensure your virtual environment is activated).
2.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
3.  Streamlit will automatically open the application in your default web browser, or provide a local URL (e.g., `http://localhost:8501`).
4.  Enter your Google Gemini API key in the sidebar as prompted.
5.  Select your preferred Gemini model.
6.  Start chatting with the bot using the input field at the bottom of the page!
7.  To start a new conversation, use the "Clear Conversation" button in the sidebar.

## How It Works

1.  **User Input:** The user types a message into the Streamlit chat input.
2.  **Agent Initialization:** When a message is received (and the API key is set), a LangChain Agent (`ZERO_SHOT_REACT_DESCRIPTION`) is initialized with the selected Google Gemini LLM (`ChatGoogleGenerativeAI`) and the available tools (Search, Wikipedia, Arxiv).
3.  **Reasoning Loop (ReAct):**
    * The agent receives the user's input (and potentially chat history).
    * The LLM determines if it needs a tool to answer the query or if it can answer directly (**Thought**).
    * If a tool is needed, the LLM decides which tool to use and what input to give it (**Action** & **Action Input**).
    * The chosen tool is executed.
    * The result of the tool execution is returned (**Observation**).
    * This Thought-Action-Observation loop repeats until the LLM believes it has enough information to answer the user.
4.  **Final Response:** The LLM generates the final answer based on the conversation and tool results.
5.  **Streaming Output:** The `StreamlitCallbackHandler` intercepts the agent's thoughts and actions, displaying them in the Streamlit UI in real-time, followed by the final response.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (or state your chosen license).

## Acknowledgements

* Built using the powerful [Streamlit](https://streamlit.io/) framework.
* Leverages the flexible [LangChain](https://www.langchain.com) library for LLM orchestration.
* Powered by [Google Gemini](https://deepmind.google/technologies/gemini/).