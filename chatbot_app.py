import tkinter as tk
from tkinter import Scrollbar, Text
import json
import random
import re
from datetime import datetime

# Function to load intents from JSON
def load_intents(file_path):
    try:
        with open(file_path, 'r') as file:
            intents = json.load(file)
        return intents
    except FileNotFoundError:
        print(f"Error: Intent file '{file_path}' not found.")
        return None


# Tokenize user input
def tokenize(sentence):
    return re.findall(r'\w+', sentence.lower())

# Stem words 
def stem(word):
    suffixes = ['ing', 'ly', 'ed', 'ious', 'ies', 'ive', 'es', 's', 'ment']
    for suffix in suffixes:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word

# Create bag of words
def bag_of_words(tokenized_sentence, vocabulary):
    tokenized_sentence = [stem(word) for word in tokenized_sentence]
    bag = [0] * len(vocabulary)

    for word in tokenized_sentence:
        if word in vocabulary:
            index = vocabulary.index(word)
            bag[index] = 1
    return bag

# Predict the intent from user input
def predict_intent(user_request, vocabulary, tags, tokenized_patterns):
    input_bag = bag_of_words(user_request, vocabulary)

    max_score = 0
    predicted_tag = None

    for tag, pattern_bag in tokenized_patterns:
        score = sum([1 if input_bag[i] == pattern_bag[i] else 0 for i in range(len(input_bag))])
        if score > max_score:
            max_score = score
            predicted_tag = tag

    return predicted_tag

# Generate chatbot response
def generate_chatbot_response(predicted_tag, intents, bot_name):
    if predicted_tag:
        for intent in intents['intents']:
            if predicted_tag == intent['tag']:
                return random.choice(intent['responses'])
    return f"{bot_name}: Sorry, I do not understand. Could you make it simpler, please?"

# Create chatbot vocabulary
def create_chatbot_vocabulary(file_path):
    intents = load_intents(file_path)

    all_words = []
    tags = []
    tokenized_patterns = []

    for intent in intents['intents']:
        tags.append(intent['tag'])
        for pattern in intent['patterns']:
            words = tokenize(pattern)
            all_words.extend(words)
            tokenized_patterns.append((intent['tag'], words))

    vocabulary = sorted(set([stem(w) for w in all_words]))
    return vocabulary, tags, tokenized_patterns

# Main chatbot logic for interfacing with the GUI
def chatbot_logic(sentence, bot_name="WieAct_Bot"):
    # Load and preprocess data
    vocabulary, tags, tokenized_patterns = create_chatbot_vocabulary('intent.json')

    # Tokenize and create bags for each pattern 
    tokenized_patterns = [(tag, bag_of_words(tokenized_pattern, vocabulary)) for tag, tokenized_pattern in tokenized_patterns]

    # Tokenize user input and predict intent
    tokenized_sentence = tokenize(sentence)
    predicted_tag = predict_intent(tokenized_sentence, vocabulary, tags, tokenized_patterns)

    # Generate chatbot response
    return generate_chatbot_response(predicted_tag, load_intents('intent.json'), bot_name)

# Define the GUI for the chatbot using Tkinter
class ChatBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WieAct_Bot")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        # Chat window area
        self.chat_area = Text(self.root, bd=1, bg="#f7d2f3", width=50, height=8, font=("Helvetica", 12), wrap=tk.WORD)
        self.chat_area.place(x=6, y=6, width=380, height=400)
        self.chat_area.config(state=tk.DISABLED)

        # Scrollbar for chat area
        scrollbar = Scrollbar(self.chat_area)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.config(command=self.chat_area.yview)

        # Input box for typing user input
        self.user_input = tk.Entry(self.root, font=("Helvetica", 14), bd=1, relief=tk.FLAT, bg="#FFFFFF", fg="#380237")
        self.user_input.place(x=6, y=420, width=300, height=30)
        self.user_input.insert(0, "")

        # Send button
        self.send_button = tk.Button(self.root, text="Send", font=("Helvetica", 15,"italic"), bg="#92a5e8", fg="#FFFFFF", bd=1, relief=tk.FLAT, command=self.on_send)
        self.send_button.place(x=320, y=420, width=70, height=30)

    # Function that processes user input and shows bot's response
    def on_send(self):
        user_message = self.user_input.get().strip()
        if user_message and user_message != "":
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.insert(tk.END, f"She: {user_message} ({datetime.now().strftime('%H:%M:%S')})\n", "user")
            self.chat_area.config(state=tk.DISABLED)

            # Get chatbot response
            bot_response = chatbot_logic(user_message)
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.insert(tk.END, f"WieAct_Bot: {bot_response} ({datetime.now().strftime('%H:%M:%S')})\n\n", "bot")
            self.chat_area.config(state=tk.DISABLED)

            # Scroll to the end of the text area
            self.chat_area.yview(tk.END)

            # Clear the user input box
            self.user_input.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatBotApp(root)
    root.mainloop()
