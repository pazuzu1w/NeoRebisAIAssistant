from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, \
    QComboBox, QLabel, QColorDialog, QFontDialog, QSlider
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from model import init_model, send_message_async, get_available_models, DEFAULT_MODEL
from dotenv import load_dotenv
from enhance_vectordb import EnhancedVectorDatabase
from user_profile import UserProfile
from personality_system import PersonalityManager
import os

load_dotenv()

class ChatWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, chat, message, vectordb, user_profile, personality_manager):
        super().__init__()
        self.chat = chat
        self.message = message
        self.vectordb = vectordb
        self.user_profile = user_profile
        self.personality_manager = personality_manager

    def run(self):
        try:
            # Get relevant context
            similar_messages = self.vectordb.search_similar(self.message)
            relevant_summaries = self.vectordb.get_relevant_summaries(self.message)

            # Get user preferences and top topics
            user_preferences = self.user_profile.preferences
            top_topics = self.user_profile.get_top_topics()

            # Get personality prompt
            personality_prompt = self.personality_manager.get_personality_prompt()

            # Construct the full message with context
            context = f"User Preferences: {user_preferences}\nTop Topics: {top_topics}\n"
            context += f"Similar Messages: {similar_messages}\nRelevant Summaries: {relevant_summaries}\n"
            context += f"Personality: {personality_prompt}\n\n"
            full_message = f"{context}User message: {self.message}"

            response = self.chat.send_message(full_message)
            self.vectordb.add_message(self.message)
            self.vectordb.add_message(response.text)
            self.finished.emit(response.text)
        except Exception as e:
            self.error.emit(str(e))

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neo Rebis Interface")
        self.vectordb = EnhancedVectorDatabase('neo_rebis.db')
        self.user_profile = UserProfile("default_user")
        self.personality_manager = PersonalityManager()

        # Color Customization
        self.bg_color = QColor(15, 16, 18)
        self.text_color = QColor(0, 197, 255)
        self.user_color = QColor(0, 255, 0)

        # Font Customization
        self.font = QFont("JetBrains Mono", 14)

        self.chat = None

        self.initUI()

        # Initialize with default model
        self.initialize_model_and_chat(DEFAULT_MODEL)

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Chat Display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(self.font)
        layout.addWidget(self.chat_display)

        # Input Area
        input_layout = QHBoxLayout()
        self.input_text = QLineEdit()
        self.input_text.setFont(self.font)
        input_layout.addWidget(self.input_text)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        # Model Selection
        self.model_dropdown = QComboBox()
        self.model_dropdown.setFont(self.font)
        self.update_model_dropdown()
        self.model_dropdown.currentTextChanged.connect(self.on_model_changed)
        layout.addWidget(QLabel("Select Model:"))
        layout.addWidget(self.model_dropdown)

        # System Prompt Input
        self.system_prompt_input = QLineEdit()
        self.system_prompt_input.setFont(self.font)
        self.system_prompt_input.setPlaceholderText("Enter System Prompt (optional)")
        self.system_prompt_input.textChanged.connect(self.on_system_prompt_changed)
        layout.addWidget(QLabel("System Prompt:"))
        layout.addWidget(self.system_prompt_input)

        # Customization Buttons
        customize_layout = QHBoxLayout()
        self.bg_button = QPushButton("Background Color")
        self.bg_button.clicked.connect(self.choose_bg_color)
        customize_layout.addWidget(self.bg_button)
        self.text_button = QPushButton("Text Color")
        self.text_button.clicked.connect(self.choose_text_color)
        customize_layout.addWidget(self.text_button)
        self.font_button = QPushButton("Font")
        self.font_button.clicked.connect(self.choose_font)
        customize_layout.addWidget(self.font_button)
        layout.addLayout(customize_layout)

        # Apply System Prompt button
        self.apply_system_prompt_button = QPushButton("Apply System Prompt")
        self.apply_system_prompt_button.clicked.connect(self.apply_system_prompt)
        layout.addWidget(self.apply_system_prompt_button)

        # Add UI elements for user profile and personality
        self.add_profile_ui()
        self.add_personality_ui()

        self.update_colors()

    def add_profile_ui(self):
        profile_layout = QVBoxLayout()
        profile_layout.addWidget(QLabel("User Preferences"))

        # Add preference inputs (e.g., communication style, interests)
        self.pref_inputs = {}
        for pref in ["communication_style", "interests"]:
            pref_layout = QHBoxLayout()
            pref_layout.addWidget(QLabel(pref.replace("_", " ").title()))
            pref_input = QLineEdit()
            pref_input.setText(self.user_profile.get_preference(pref, ""))
            pref_input.textChanged.connect(lambda text, p=pref: self.update_preference(p, text))
            self.pref_inputs[pref] = pref_input
            pref_layout.addWidget(pref_input)
            profile_layout.addLayout(pref_layout)

        self.layout().addLayout(profile_layout)

    def add_personality_ui(self):
        personality_layout = QVBoxLayout()
        personality_layout.addWidget(QLabel("AI Personality Traits"))

        # Add sliders for each personality trait
        self.trait_sliders = {}
        for trait in ["formality", "humor", "empathy", "creativity", "assertiveness"]:
            trait_layout = QHBoxLayout()
            trait_layout.addWidget(QLabel(trait.title()))
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(int(self.personality_manager.personality.get_trait(trait) * 100))
            slider.valueChanged.connect(lambda value, t=trait: self.update_personality_trait(t, value / 100))
            self.trait_sliders[trait] = slider
            trait_layout.addWidget(slider)
            personality_layout.addLayout(trait_layout)

        self.layout().addLayout(personality_layout)

    def update_preference(self, preference, value):
        self.user_profile.update_preference(preference, value)

    def update_personality_trait(self, trait, value):
        self.personality_manager.update_personality(trait, value)

    def update_model_dropdown(self):
        models = get_available_models()
        self.model_dropdown.clear()
        self.model_dropdown.addItems(models)
        # Set the current index to the default model
        default_index = self.model_dropdown.findText(DEFAULT_MODEL)
        if default_index >= 0:
            self.model_dropdown.setCurrentIndex(default_index)

    def on_model_changed(self, model_name):
        self.initialize_model_and_chat(model_name)

    def on_system_prompt_changed(self):
        pass  # We'll apply the system prompt only when the button is clicked

    def initialize_model_and_chat(self, model_name):
        system_prompt = self.system_prompt_input.text()

        self.chat = init_model(model_name, system_prompt)
        if self.chat:
            self.display_message("Model initialized! Let's chat!", "System")
        else:
            self.display_message("Error initializing model. Check console.", "System")

    def send_message(self):
        message = self.input_text.text()
        self.input_text.clear()
        if message and self.chat:
            self.display_message(message, "You")
            self.worker = ChatWorker(self.chat, message, self.vectordb, self.user_profile, self.personality_manager)
            self.worker.finished.connect(self.process_response)
            self.worker.error.connect(self.handle_error)
            self.worker.start()

    def handle_error(self, error_message):
        self.display_message(f"Error: {error_message}", "System")

    def process_response(self, response_text):
        self.display_message(response_text, "Codebro")

    def display_message(self, message, sender):
        formatted_message = self.format_message(message)
        self.chat_display.append(f"<strong>{sender}:</strong><br>{formatted_message}<br>")

    def format_message(self, message):
        # Split the message into lines
        lines = message.split('\n')
        formatted_lines = []
        in_code_block = False
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                if in_code_block:
                    formatted_lines.append(
                        '<pre style="font-family: monospace; background-color: #f0f0f0; padding: 10px; margin: 5px 0;">')
                else:
                    formatted_lines.append('</pre>')
            else:
                if in_code_block:
                    formatted_lines.append(line.replace(' ', '&nbsp;'))
                else:
                    formatted_lines.append(line)

        return '<br>'.join(formatted_lines)

    def choose_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = color
            self.update_colors()

    def choose_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color
            self.update_colors()

    def choose_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.font = font
            self.chat_display.setFont(self.font)
            self.input_text.setFont(self.font)
            self.model_dropdown.setFont(self.font)
            self.system_prompt_input.setFont(self.font)

    def update_colors(self):
        style_sheet = f"""
            QWidget {{
                background-color: {self.bg_color.name()};
                color: {self.text_color.name()};
            }}
            QLineEdit {{
                color: {self.user_color.name()}; 
            }}
        """
        self.setStyleSheet(style_sheet)

    def apply_system_prompt(self):
        if self.model_dropdown.currentText():
            self.initialize_model_and_chat(self.model_dropdown.currentText())

    def closeEvent(self, event):
        self.vectordb.close()
        self.user_profile.save_profile()
        super().closeEvent(event)