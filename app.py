import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchRun
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="LangChain Search Bot",
    page_icon="https://cdn.brandfetch.io/id9M89MUnI/theme/dark/logo.svg?c=1dxbfHSJFAPEGdCLU4o5B", 
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. Session State Initialization (User Input Only for API Key) ---
if "api_keys_set" not in st.session_state:
    # Always initialize as False, requiring user input via UI
    st.session_state.api_keys_set = False
    st.session_state.google_api_key = ""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! I'm a chatbot connected to the web (via DuckDuckGo, Wikipedia, Arxiv). How can I assist you today?"} # Friendlier greeting
    ]

# Default model
if "selected_model" not in st.session_state:
     st.session_state.selected_model = "gemini-1.5-pro" 

# Initialize temperature if not already set
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7  # Default value for temperature



# --- 3. Utility Functions ---
def clear_chat_history():
    """Clears the chat history and resets the initial message."""
    st.session_state.messages = [
         {"role": "assistant", "content": "Chat history cleared! How can I help you next?"}
    ]
    st.toast("Chat history cleared!", icon="🔄")

# --- 4. API Wrapper and Tool Initialization ---
try:
    api_wrapper_wiki = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)
    wiki = WikipediaQueryRun(api_wrapper=api_wrapper_wiki)
    api_wrapper_arxiv = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=500)
    arxiv = ArxivQueryRun(api_wrapper=api_wrapper_arxiv)
    search = DuckDuckGoSearchRun(name="Search")
    TOOLS = [search, arxiv, wiki]
except Exception as e:
    st.error(f"Error initializing tools: {e}")
    st.stop() # Stop execution if tools can't be initialized

# --- 5. Sidebar Configuration (More Organized) ---
st.sidebar.header("⚙️ Configuration")

# API Key Input - Always show input section, behavior changes based on api_keys_set
st.sidebar.subheader("🔑 API Key")
if not st.session_state.api_keys_set:
    # If key is NOT set, show the input field prominently
    google_api_key_input = st.sidebar.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="Enter your Google API key here",
        help="Required to use the chatbot. Get your key from Google AI Studio.",
        value=st.session_state.google_api_key, # Should be "" initially
        key="google_api_key_input_main"
    )
    if st.sidebar.button("Save API Key", key="save_api_key_main", use_container_width=True):
        if google_api_key_input:
            st.session_state.google_api_key = google_api_key_input
            st.session_state.api_keys_set = True
            # Update initial message now that key is set
            if len(st.session_state.messages) == 1 and "Please enter your Google Gemini API Key" in st.session_state.messages[0]['content']:
                 st.session_state.messages = [{"role": "assistant", "content": "API Key saved! How can I assist you today?"}]
            st.toast("API key saved!", icon="✅")
            st.rerun() # Rerun to enable chat input and update UI
        else:
            st.sidebar.error("Please enter a valid Google API key.")
else:
    # If key IS set, show success and allow modification within an expander
    st.sidebar.success("Google API Key is set.", icon="✔️")
    with st.sidebar.expander("Modify API Key", expanded=False):
        google_api_key_input = st.text_input(
            "New Google Gemini API Key",
            type="password",
            placeholder="Enter new key to update",
            key="google_api_key_input_modify"
        )
        if st.button("Update API Key", key="update_api_key", use_container_width=True):
            if google_api_key_input:
                st.session_state.google_api_key = google_api_key_input
                # api_keys_set remains True
                st.toast("API key updated!", icon="✅")
                st.rerun() # Rerun to reflect potential changes if needed
            else:
                 st.error("Please enter a valid Google API key to update.")
        if st.button("Clear API Key", key="clear_api_key", use_container_width=True):
             st.session_state.google_api_key = ""
             st.session_state.api_keys_set = False
             st.toast("API key cleared!", icon="🗑️")
             st.rerun()

# Model Selection
st.sidebar.subheader("Model Selection")
model_options = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-lite", "gemini-2.0-flash"] # Keep options concise unless more are needed
# Ensure default selection index is valid
default_model_index = 0
if st.session_state.selected_model in model_options:
    default_model_index = model_options.index(st.session_state.selected_model)

selected_model = st.sidebar.radio(
    "Choose the Gemini model:",
    options=model_options,
    index=default_model_index,
    key="model_selector",
    help="Select the underlying AI model. 'Pro' is more powerful but potentially slower/more expensive.",
    disabled=not st.session_state.api_keys_set # Disable model selection until key is set
)

# Update session state if selection changes
if selected_model != st.session_state.selected_model:
    st.session_state.selected_model = selected_model
    # No rerun needed unless model change requires immediate action

# --- Add Temperature Slider ---
st.sidebar.subheader("Model Temperature")
st.session_state.temperature = st.sidebar.slider(
    "Adjust creativity (0 = Deterministic, 1 = Max Creative):",
    min_value=0.0,
    max_value=1.0,
    value=st.session_state.temperature, # Use current session state value
    step=0.1,                          # Increment step
    key="temperature_slider",
    help="Lower values (e.g., 0.1) make the output more focused and predictable. Higher values (e.g., 0.9) generate more diverse and creative responses.",
    disabled=not st.session_state.api_keys_set # Disable until key is set
)

# Clear Chat Button
st.sidebar.subheader("💬 Manage Chat")
st.sidebar.button("Clear Conversation", on_click=clear_chat_history, use_container_width=True, help="Start a new chat session", disabled=not st.session_state.api_keys_set)

st.sidebar.markdown("---") # Divider
st.sidebar.info("Built with LangChain & Streamlit")

# --- 6. Main Chat Interface ---
st.title("🤖 LangChain Search Bot")
st.caption(f"Using model: `{st.session_state.selected_model}` | Tools: DuckDuckGo, Wikipedia, Arxiv")

# Display chat messages from history
for i, msg in enumerate(st.session_state.messages):
    st.chat_message(msg["role"]).write(msg['content'])

# Input field for user query - disabled if API key is not set
prompt = st.chat_input(
    placeholder="Please save API Key in sidebar to chat...",
    disabled=not st.session_state.api_keys_set # Key line: disable if key not set
)

if prompt:
    # This block only runs if chat_input is enabled (i.e., api_keys_set is True) and user enters text
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # --- 7. Agent Execution ---
    # No need for the redundant API key check here, as the chat input is disabled if it's missing.
    # However, keeping it adds an extra layer of safety in case of unexpected state changes.
    if not st.session_state.google_api_key:
         st.error("🛑 Error: Google Gemini API key is missing. Cannot proceed.")
         st.stop()

    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            google_api_key=st.session_state.google_api_key,
            model=f"models/{st.session_state.selected_model}",
            temperature=st.session_state.temperature, # Use the slider value
            streaming=True,
            convert_system_message_to_human=True
        )

        # Initialize Agent
        search_agent = initialize_agent(
            TOOLS,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors="I encountered an issue parsing the tool output. Please check the format.", # Slightly more user-friendly error
            verbose=False # Set verbose=False for cleaner production UI
        )

        # Display thinking indicator and execute agent
        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False, collapse_completed_thoughts=True)
            with st.spinner(f"Asking {st.session_state.selected_model}..."):
                response = search_agent.run(st.session_state.messages, callbacks=[st_cb]) # Pass history for context

            # Display the final response and add to history
            st.session_state.messages.append({'role': 'assistant', "content": response})
            # Ensure the response is written correctly within the chat message context
            st.write(response) # This should now correctly write inside the assistant's chat bubble


    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        st.error(error_message)
        # Append a user-friendly error message to the chat
        st.session_state.messages.append({'role': 'assistant', "content": f"Sorry, I encountered an error and couldn't complete your request. Please check the API key and model settings, or try again later."})
        # Optionally write the error message to the chat interface immediately
        st.chat_message("assistant").error("Sorry, I encountered an error. Please check the logs or try again.")


# --- 8. Optional: Footer ---
st.markdown("---")
st.caption("Ensure your Google API key has the necessary permissions and quotas.")