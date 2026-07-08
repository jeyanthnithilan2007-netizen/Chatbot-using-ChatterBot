# chatbot.py - Fixed Version with Gradio Compatibility

import gradio as gr
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
import os
import sys
import logging

# Disable verbose logging
logging.basicConfig(level=logging.ERROR)

# --- Custom Function for Advanced Logic ---
def check_website_status():
    """Check if a website is up or down"""
    try:
        import urllib.request
        import urllib.error
        # You can change this to any website you want to monitor
        HOSTNAME = 'https://www.google.com'
        urllib.request.urlopen(HOSTNAME, timeout=5)
        return '✅ The website is up and running!'
    except urllib.error.URLError:
        return '❌ The website appears to be down.'
    except Exception as e:
        return f'⚠️ Error checking website: {str(e)}'

# --- Initialize the Chatbot ---
print("Initializing the God Mode Chatbot...")

chatbot = ChatBot(
    "InternshipGodBot",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database_uri="sqlite:///database.sqlite3",
    read_only=False,  # Set to False initially to allow training
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': "I am sorry, but I don't have an answer for that yet. Could you rephrase your question?",
            'maximum_similarity_threshold': 0.80
        },
        "chatterbot.logic.TimeLogicAdapter",
    ]
)

# --- Smart Training Function ---
def train_chatbot():
    """Train the chatbot with multiple data sources"""
    
    print("Starting training process...")
    
    # Check if database already has content
    if chatbot.storage.count() > 0:
        print(f"Database already has {chatbot.storage.count()} responses. Skipping training.")
        return
    
    # Method 1: Try to train with ChatterBot corpus
    try:
        print("Attempting to train with ChatterBot corpus...")
        corpus_trainer = ChatterBotCorpusTrainer(chatbot)
        
        # Try different corpus paths
        corpus_options = [
            "chatterbot.corpus.english",
            "chatterbot.corpus.english.greetings",
            "chatterbot.corpus.english.conversations"
        ]
        
        for corpus in corpus_options:
            try:
                print(f"  Training with: {corpus}")
                corpus_trainer.train(corpus)
                print(f"  ✓ Successfully trained with {corpus}")
            except Exception as e:
                print(f"  ✗ Failed to train with {corpus}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Corpus training failed: {str(e)}")
        print("Falling back to custom training data...")
    
    # Method 2: Always train with custom data (this is reliable)
    print("\nTraining with custom conversation data...")
    custom_trainer = ListTrainer(chatbot)
    
    # Comprehensive training data
    training_data = [
        # Greetings and introductions
        "Hello",
        "Hi there! How can I help you today?",
        "Hi",
        "Hello! Welcome to the Internship God Mode Chatbot.",
        "Hey",
        "Hey there! What can I do for you?",
        
        # Name and identity
        "What is your name?",
        "I am InternshipGodBot, your powerful assistant for this project!",
        "Who are you?",
        "I'm an advanced chatbot built with ChatterBot and Gradio for an internship project.",
        "What's your name?",
        "You can call me InternshipGodBot - I'm here to help!",
        
        # Project information
        "What is this project?",
        "This is a professional multi-layered chatbot project designed for an internship final presentation.",
        "Tell me about yourself",
        "I'm a state-of-the-art chatbot featuring rule-based matching, comprehensive training, and a beautiful interface.",
        "What can you do?",
        "I can answer questions, tell you the time, check website status, and learn from our conversations!",
        
        # Functionality
        "What time is it?",
        "Let me check that for you!",
        "Check website",
        "I'll check the website status for you.",
        "Is the website working?",
        "Let me verify that...",
        
        # Farewells
        "Goodbye",
        "Goodbye! It was a pleasure chatting with you.",
        "Bye",
        "Bye! Have a great day!",
        "Thanks",
        "You're welcome! Happy to help.",
        "Thank you",
        "My pleasure! Is there anything else I can assist you with?",
    ]
    
    # Train in batches to avoid memory issues
    batch_size = 10
    for i in range(0, len(training_data), batch_size):
        batch = training_data[i:i+batch_size]
        try:
            custom_trainer.train(batch)
            print(f"  ✓ Trained batch {i//batch_size + 1}/{(len(training_data)-1)//batch_size + 1}")
        except Exception as e:
            print(f"  ✗ Error training batch: {str(e)}")
    
    # Add some domain-specific knowledge
    domain_data = [
        "What is artificial intelligence?",
        "AI is the simulation of human intelligence processes by machines, especially computer systems.",
        "What is machine learning?",
        "ML is a subset of AI that enables systems to learn and improve from experience without explicit programming.",
        "What is natural language processing?",
        "NLP is a branch of AI that helps computers understand, interpret, and manipulate human language.",
        "What is ChatterBot?",
        "ChatterBot is a Python library for creating conversational AI agents using machine learning.",
        "What is Gradio?",
        "Gradio is a Python library that makes it easy to create UIs for machine learning models.",
    ]
    
    try:
        custom_trainer.train(domain_data)
        print("  ✓ Trained with domain-specific knowledge")
    except Exception as e:
        print(f"  ✗ Error training domain data: {str(e)}")
    
    print(f"\n✅ Training complete! The chatbot has {chatbot.storage.count()} responses in its database.")

# --- Train the chatbot ---
train_chatbot()

# --- Define the Response Function for Gradio ---
def response_function(message, history):
    """Process user message and return chatbot response"""
    
    # Check for special commands
    message_lower = message.lower()
    
    # Special case: website check
    if any(phrase in message_lower for phrase in ['check website', 'is the website up', 'website status']):
        return check_website_status()
    
    # Special case: show help
    if message_lower in ['help', 'commands', 'what can you do']:
        return """Available commands:
• Ask me anything about AI, ML, or NLP
• "What time is it?" - Check current time
• "Check website" - Check if a website is online
• "Help" - Show this help message
• Ask about the project or my capabilities"""
    
    # Get response from chatbot
    try:
        response = chatbot.get_response(message)
        return response.text
    except Exception as e:
        return f"⚠️ I encountered an error: {str(e)}. Please try again."

# --- Set up the Gradio Chat Interface ---
print("\nSetting up the professional interface...")

def auth_check(username, password):
    """Simple authentication for the demo"""
    # In production, use environment variables or a secure database!
    return username == "intern" and password == "godmode2026"

# FIXED: Create the interface without the 'theme' parameter
# If you want to change the theme, you can use CSS or upgrade Gradio
interface = gr.ChatInterface(
    fn=response_function,
    title="🚀 Internship God Mode Chatbot",
    description="""
    A professional, multi-layered chatbot built with ChatterBot and Gradio.
    
    **Features:**
    • Advanced conversation handling
    • Time awareness
    • Website status checking
    • Professional UI
    • Secure access
    """,
    # Remove the 'theme' parameter if it's causing issues
    # theme="soft",  # Comment this out for compatibility
    examples=[
        ["Hello"],
        ["What is your name?"],
        ["What is artificial intelligence?"],
        ["What time is it?"],
        ["Check website"],
        ["Help"]
    ],
    cache_examples=False
)

# --- Launch the Server ---
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 GOD MODE CHATBOT IS READY!")
    print("="*60)
    print("\n✅ Local URL: http://127.0.0.1:7860")
    print("\n🔐 Authentication Credentials:")
    print("   Username: intern")
    print("   Password: godmode2026")
    print("\n📱 Share this public link with your supervisors!")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=True,  # Creates a public link
        auth=auth_check,
        debug=False
    )