import streamlit as st
import os
from groq import Groq
import random
import time

from langchain.chains import ConversationChain, LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

load_dotenv()

def typing_effect(text):
    placeholder = st.empty()
    typed_text = ""
    for char in text:
        typed_text += char
        placeholder.markdown(f"**Accounting Bot:** {typed_text}")
        time.sleep(0.0005)  # Adjust the speed of the typing effect
    return typed_text

def main():
    """
    This function is the main entry point of the application. It sets up the Groq client, the Streamlit interface, and handles the chat interaction.
    """

    groq_api_key = os.environ['GROQ_API_KEY']
    # Get Groq API key
    #groq_api_key = 

    # Display the Groq logo
    spacer, col = st.columns([5, 1])  
    with col:  
        st.image('groqcloud_darkmode.png')

    # The title and greeting message of the Streamlit application
    st.title("Chat with Accounting Bot!")
    st.write("Hello! I'm your friendly Accounting chatbot. I can help answer your questions, provide information, or just chat. I'm also super fast! Let's start our conversation!")

    # Add customization options to the sidebar
    st.sidebar.title('Customization')
    system_prompt = st.sidebar.text_input("System prompt:", value="You are Accounting Bot, an accounting chatbot that specializes on journal entry, financial analysis and budgeting.")
    model = 'llama3-70b-8192'
    conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value = 5)
    temperature = st.sidebar.slider('Response Temperature:', 0.0, 1.0, value=0.7)

    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)

    user_question = st.text_input("Ask a question:")

    # File uploader
    uploaded_file = st.file_uploader("Upload a document for review", type=["pdf", "docx", "txt"])

    # session state variable
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history=[]
    else:
        for message in st.session_state.chat_history:
            memory.save_context(
                {'input':message['human']},
                {'output':message['AI']}
                )


    # Initialize Groq Langchain chat object and conversation
    groq_chat = ChatGroq(
            groq_api_key=groq_api_key, 
            model_name=model
    )


    # If the user has asked a question or uploaded a file,
    if user_question or uploaded_file:

        # Construct a chat prompt template using various components
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=system_prompt
                ),  # This is the persistent system prompt that is always included at the start of the chat.

                MessagesPlaceholder(
                    variable_name="chat_history"
                ),  # This placeholder will be replaced by the actual chat history during the conversation. It helps in maintaining context.

                HumanMessagePromptTemplate.from_template(
                    "{human_input}"
                ),  # This template is where the user's current input will be injected into the prompt.
            ]
        )

        # Create a conversation chain using the LangChain LLM (Language Learning Model)
        conversation = LLMChain(
            llm=groq_chat,  # The Groq LangChain chat object initialized earlier.
            prompt=prompt,  # The constructed prompt template.
            verbose=True,   # Enables verbose output, which can be useful for debugging.
            memory=memory,  # The conversational memory object that stores and manages the conversation history.
        )
        
        # If a file is uploaded, include it in the prompt
        if uploaded_file:
            file_content = uploaded_file.read().decode("utf-8")
            user_question = f"Please review the following document:\n\n{file_content}\n\n{user_question}"
        
        # The chatbot's answer is generated by sending the full prompt to the Groq API.
        response = conversation.predict(human_input=user_question)
        message = {'human':user_question,'AI':response}
        st.session_state.chat_history.append(message)
        #st.write("Chatbot:", response)
        typing_effect(response)

if __name__ == "__main__":
    main()
