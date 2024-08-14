from idlelib.search import SearchDialog
import google.generativeai as genai
from entityDB import EntityDB
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, \
    QComboBox, QLabel, QColorDialog, QFontDialog, QSlider, QDialog, QDialogButtonBox, QCheckBox, QMessageBox, \
    QFileDialog
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QLocale, QTimer
from model import init_model, send_message_async, get_available_models, DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT, History
from dotenv import load_dotenv
from enhance_vectordb import EnhancedVectorDatabase, logger
from user_profile import UserProfile
from personality_system import PersonalityManager
import os
import datetime
import pyttsx3
import threading
import logging
import pyaudio
import speech_recognition as sr



load_dotenv()


class SpeechRecognitionWorker(QThread):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.running = True

    def run(self):
        while self.running:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source)

                text = self.recognizer.recognize_google(audio)
                self.result_ready.emit(text)
            except Exception as e:
                self.error_occurred.emit(str(e))

    def stop(self):
        self.running = False



class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Logs and VectorDB")
        self.layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search query...")
        self.layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.accept)
        self.layout.addWidget(self.search_button)

        self.setLayout(self.layout)


class LogManager:
    def __init__(self):
        self.log_dir = "logs"
        self.ensure_log_directory()
        self.current_log_file = self.create_new_log_file()
        self.lock = threading.Lock()


    def ensure_log_directory(self):
        today = datetime.date.today().strftime('%Y-%m-%d')
        self.date_dir = os.path.join(self.log_dir, today)
        if not os.path.exists(self.date_dir):
            os.makedirs(self.date_dir)

    def create_new_log_file(self):
        start_time = datetime.datetime.now().strftime('%H-%M-%S')
        filename = f"{start_time}.log"
        full_path = os.path.join(self.date_dir, filename)
        return full_path

    def log_message(self, sender, message):
        with self.lock:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"\n[{timestamp}] {sender}: {message}\n"
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)

    def search_logs(self, query):
        results = []
        try:
            for filename in os.listdir(self.log_dir):
                if filename.endswith(".log"):
                    with open(os.path.join(self.log_dir, filename), 'r', encoding='utf-8') as f:
                        for line in f:
                            if query.lower() in line.lower():
                                results.append(line.strip())
        except Exception as e:
            print(f"Error searching logs: {e}")
        return results



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
        self.entity_list = EntityDB.list_entities()
    def run(self):
        try:
            # Get relevant context
            #similar_messages = self.vectordb.search_similar(self.message)
            #relevant_summaries = self.vectordb.get_relevant_summaries(self.message)

            # Get user preferences and top topics
            user_preferences = self.user_profile.preferences
            top_topics = self.user_profile.get_top_topics()
            first_name = self.user_profile.get_first_name("first_name_key")
            last_name = self.user_profile.get_last_name("last_name_key")
            alias = self.user_profile.get_alias("alias_key")
            bio = self.user_profile.get_bio("bio_key")
            core_values = self.user_profile.get_core_values()
            primary_motivations = self.user_profile.get_primary_motivations()
            # Get personality prompt
            personality_prompt = self.personality_manager.get_personality_prompt()
            working_directory = os.getcwd()
            entity_list = self.entity_list

            # Construct the full message with context
            context = f"User Preferences: {user_preferences}\nTop Topics: {top_topics}\n"
            #context += f"Similar Messages: {similar_messages}\nRelevant Summaries: {relevant_summaries}\n"
            context += f"User First Name: {first_name}\n"
            context += f"User Last Name: {last_name}\n"
            context += f"User Alias: {alias}\n"
            context += f"User Bio: {bio}\n"
            context += f"Core Values: {core_values}\n"
            context += f"Primary Motivations: {primary_motivations}\n"
            context += f"Working Directory: {working_directory}\n"
            context += f"Entity List: {entity_list}\n"

            context += f"Personality: {personality_prompt}\n\n"
            full_message = f"{context}User message: {self.message}"

            response = self.chat.send_message(full_message)
            self.vectordb.add_message(self.message)
            self.vectordb.add_message(response.text)
            self.finished.emit(response.text)
        except Exception as e:
            self.error.emit(str(e))


class SummaryWorker(QThread):
    summary_created = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, vectordb):
        super().__init__()
        self.vectordb = vectordb

    def run(self):
        try:
            summary = self.vectordb.create_conversation_summary()
            if summary:
                self.summary_created.emit(summary)
            else:
                self.summary_created.emit("")
        except Exception as e:
            self.error_occurred.emit(str(e))




class App(QWidget):








    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neo Rebis Interface")
        self.vectordb = EnhancedVectorDatabase('enhanced_chatbot.db')
        self.user_profile = UserProfile("default_user")
        self.personality_manager = PersonalityManager()
        self.history = History


        # Color Customization
        self.bg_color = QColor(15, 16, 18)
        self.text_color = QColor(0, 197, 255)
        self.user_color = QColor(200, 255, 75)

        # Font Customization
        self.font = QFont("JetBrains Mono", 14)

        self.speak_aloud = False

        # Initialize the speech recognition worker
        self.speech_recognition_worker = SpeechRecognitionWorker()
        self.speech_recognition_worker.result_ready.connect(self.on_speech_recognized)
        self.speech_recognition_worker.error_occurred.connect(self.on_speech_error)

        self.log_manager = LogManager()

        self.speech_worker = SpeechWorker(self)
        self.speech_worker.finished.connect(self.on_speech_finished)
        self.speech_worker.error.connect(self.on_speech_error)

        self.multimodal_model = None
        self.chat = None

        self.current_model = DEFAULT_MODEL
        self.system_prompt = DEFAULT_SYSTEM_PROMPT

        self.initUI()

        # Initialize with default model
        self.initialize_model_and_chat(self.current_model, self.system_prompt)

        # Start the speech recognition worker thread
        self.speech_recognition_worker.start()

        # Set up periodic summary creation
        self.summary_timer = QTimer(self)
        self.summary_timer.timeout.connect(self.start_summary_creation)
        self.summary_timer.start(1000000)  # Create summary every 5 minutes

        # Initialize summary worker
        self.summary_worker = None

        self.is_text_changed_connected = True  # Track the connection state



    def initUI(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # --- Chat Display ---
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(self.font)
        main_layout.addWidget(self.chat_display)

        # --- Input Area ---
        input_layout = QHBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter your message here...")
        self.input_text.setReadOnly(False)
        self.input_text.setFont(self.font)
        input_layout.addWidget(self.input_text)

        # Connect textChanged signal to a new slot
        self.input_text.textChanged.connect(self.check_for_trigger)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)

        self.file_picker_button = QPushButton("Pick File")
        self.file_picker_button.clicked.connect(self.pick_file)
        input_layout.addWidget(self.file_picker_button)

        self.clear_file_button = QPushButton("Clear File")
        self.clear_file_button.clicked.connect(self.clear_file)
        input_layout.addWidget(self.clear_file_button)


        button_layout = QHBoxLayout()

        # --- Options Button ---
        options_button = QPushButton("Options")
        options_button.clicked.connect(self.show_options_dialog)
        button_layout.addWidget(options_button)

        # ---- Search Button ----
        self.search_button = QPushButton("Search Logs")
        self.search_button.clicked.connect(self.show_search_dialog)
        button_layout.addWidget(self.search_button)

        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # --- Speech Recognition Toggle Button ---
        self.speech_button = QPushButton("Toggle Speech Recognition")
        self.speech_button.clicked.connect(self.toggle_speech_recognition)
        button_layout.addWidget(self.speech_button)

        main_layout.addLayout(button_layout)



        main_layout.addLayout(button_layout)

        self.update_colors()

    def pick_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select File")
        if file_path:
            self.selected_file_path = file_path
            self.display_message(f"File selected: {os.path.basename(file_path)}", "System")



    def clear_file(self):
        if hasattr(self, 'selected_file_path'):
            del self.selected_file_path
            self.display_message("File cleared", "System")


    def on_speech_recognized(self, text):
        # Update the input box with the recognized text
        current_text = self.input_text.toPlainText()
        self.input_text.setPlainText(current_text + " " + text)

    def on_speech_error(self, error_message):
        print(f"Speech recognition error: {error_message}")

    def toggle_speech_recognition(self):
        if self.speech_recognition_worker.isRunning():
            self.speech_recognition_worker.stop()
            self.speech_button.setText("Start Speech Recognition")
        else:
            self.speech_recognition_worker.running = True
            self.speech_recognition_worker.start()
            self.speech_button.setText("Stop Speech Recognition")




    def show_search_dialog(self):
        try:
            dialog = SearchDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                query = dialog.search_input.text()
                self.perform_search(query)
        except Exception as e:
            self.show_error_message(f"Error opening search dialog: {e}")

    def perform_search(self, query):
        try:
            log_results = self.log_manager.search_logs(query)
            vector_results = self.vectordb.semantic_search(query, k=5)  # Assuming k=5 for top 5 results

            self.display_message(f"Search results for '{query}':", "System")

            if log_results:
                self.display_message("Log Search Results:", "System")
                for result in log_results[:5]:  # Limiting to 5 results
                    self.display_message(result, "Log")

            if vector_results:
                self.display_message("Vector DB Semantic Search Results:", "System")
                for result in vector_results:
                    self.display_message(f"Similarity: {result['similarity']:.2f} - {result['content']}", "VectorDB")

            # Prepare context for the bot
            context = f"Tony searched for '{query}'. Here are the relevant results:\n"
            context += "Log results:\n" + "\n".join(log_results[:5]) + "\n"
            context += "Vector DB results:\n" + "\n".join(
                [f"{r['similarity']:.2f} - {r['content']}" for r in vector_results])
            context += "\nBased on these search results, please provide a summary or answer any questions the user might have."

            # Send context to the bot for processing
            if self.chat:
                self.worker = ChatWorker(self.chat, context, self.vectordb, self.user_profile, self.personality_manager)
                self.worker.finished.connect(self.process_response)
                self.worker.error.connect(self.handle_error)
                self.worker.start()
            else:
                self.show_error_message("Chat model not initialized. Please check your configuration.")
        except Exception as e:
            self.show_error_message(f"Error performing search: {e}")

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)
        print(f"Error: {message}")



    def handle_error(self, error):
        # Log the error
        logger.error(f"An error occurred: {error}")
        # Optional: Display an error dialog or take other error handling actions
        # For example, you could show a QMessageBox with the error message
        # QMessageBox.critical(self, "Error", str(error))




    def check_for_trigger(self):
        try:
            logging.debug("Checking for trigger...")
            # Temporarily disconnect the signal to prevent potential loop
            self.input_text.textChanged.disconnect(self.check_for_trigger)

            text = self.input_text.toPlainText()
            if text.endswith("send") or text.endswith("Send"):
                logging.debug("Trigger detected")
                trigger_message = text[:-4] # Remove the trigger phrase
                self.input_text.clear()
                self.send_message(trigger_message)  # Assuming send_message is your existing message sending function

        except Exception as e:
            logging.error(f"Error in check_for_trigger: {e}")
        finally:
            # Reconnect the signal after processing
            self.input_text.textChanged.connect(self.check_for_trigger)

    def show_options_dialog(self):
        try:
            dialog = OptionsDialog(self)
            dialog.exec()
        except Exception as e:
            print(f"Error opening options dialog: {e}")



    def on_model_changed(self, model_name):
        self.current_model = model_name
        self.initialize_model_and_chat(model_name)
        self.display_message(f"Model changed to {model_name}", "System")


    def apply_system_prompt(self, system_prompt):
        self.system_prompt = system_prompt
        self.initialize_model_and_chat(self.current_model, self.system_prompt)
        self.display_message("System prompt updated!", "System")

    def send_message(self, trigger_message):

        message = self.input_text.toPlainText()
        self.input_text.clear()



        if message and self.chat:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timestamped_message = f"[{current_time}] {message}"
            self.display_message(timestamped_message, "You")
            self.log_manager.log_message("You", timestamped_message)
            # Check if a file is selected
            if hasattr(self, 'selected_file_path'):
                try:
                    # Upload the file
                    uploaded_file = genai.upload_file(path=self.selected_file_path,
                                                      display_name=os.path.basename(self.selected_file_path))



                    self.multimodal_model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
                    self.history.append({"role": "user", "content": message})
                    # Generate content with both text and file
                    response = self.multimodal_model.generate_content([uploaded_file, message])
                    self.history.append({"role": "assistant", "content": response.text})
                    # Process the response
                    self.process_response(response.text)
                except Exception as e:
                    self.show_error_message(f"Error processing file: {str(e)}")
                    del self.selected_file_path
            else:
                # If no file is selected, proceed with text-only message
                self.worker = ChatWorker(self.chat, timestamped_message, self.vectordb, self.user_profile,
                                         self.personality_manager)
                self.worker.finished.connect(self.process_response)
                self.worker.start()

        if trigger_message and self.chat:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timestamped_message = f"[{current_time}] {trigger_message}"
            self.display_message(timestamped_message, "You")
            self.log_manager.log_message("You", timestamped_message)
            if hasattr(self, 'selected_file_path'):
                try:
                    # Upload the file
                    uploaded_file = genai.upload_file(path=self.selected_file_path,
                                                      display_name=os.path.basename(self.selected_file_path))



                    # Construct a GenerativeModel which uses the created cache.
                    self.multimodal_model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

                    # Generate content with both text and file
                    response = self.multimodal_model.generate_content([uploaded_file, message])
                    self.send_from_multimodal(response)
                    # Process the response
                    self.process_response(response.text)
                    self.chat.history.append({"role": "assistant", "content": response.text})
                    # Clear the selected file path
                except Exception as e:
                    self.show_error_message(f"Error processing file: {str(e)}")
                    del self.selected_file_path
            else:
                # If no file is selected, proceed with text-only message
                self.worker = ChatWorker(self.chat, timestamped_message, self.vectordb, self.user_profile,
                                         self.personality_manager)
                self.worker.finished.connect(self.process_response)
                self.worker.start()


    def toggle_speak_aloud(self, state):
        self.speak_aloud = bool(state)

    def process_response(self, response_text):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamped_response = f"[{current_time}] {response_text}"
        self.display_message(timestamped_response, "Gemini")
        self.log_manager.log_message("Gemini", timestamped_response)
        if self.speak_aloud:
            self.speech_worker.add_text(response_text)  # Note: We don't include the timestamp in the spoken text

    def send_from_multimodal(self, response):
        self.worker = ChatWorker(self.chat, response, self.vectordb, self.user_profile,
                                 self.personality_manager)
        self.worker.finished.connect(self.process_response)
        self.worker.start()
        del self.selected_file


    def on_speech_finished(self):
        print("Speech completed")


    def on_speech_error(self, error_message):
        print(f"Speech error: {error_message}")


    def toggle_speak_bot_messages(self, state):
        self.speak_bot_messages = bool(state)


    def display_message(self, message, sender):
        formatted_message = self.format_message(message)
        self.chat_display.append(f"\n{sender}: {formatted_message}")



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
                        '')
                else:
                    formatted_lines.append('')
            else:
                if in_code_block:
                    formatted_lines.append(line.replace(' ', ' '))
                else:
                    formatted_lines.append(line)

        return ''.join(formatted_lines)

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
            # Access and update font in OptionsDialog if needed
            if hasattr(self, 'options_dialog') and hasattr(self.options_dialog, 'model_dropdown'):
                self.options_dialog.model_dropdown.setFont(self.font)
            # Similarly for other widgets in options dialog

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

    def start_summary_creation(self):
        if self.summary_worker is None or not self.summary_worker.isRunning():
            self.summary_worker = SummaryWorker(self.vectordb)
            self.summary_worker.summary_created.connect(self.on_summary_created)
            self.summary_worker.error_occurred.connect(self.on_summary_error)
            self.summary_worker.start()

    def on_summary_created(self, summary):
        if summary:
            self.display_message("Created new conversation summary.", "System")
            logger.info(f"New conversation summary created: {summary[:1000]}...")  # Log first 100 chars
            self.worker = ChatWorker(self.chat, summary, self.vectordb, self.user_profile,
                                     self.personality_manager)
            self.worker.finished.connect(self.process_response)
            self.worker.error.connect(self.handle_error)
            self.worker.start()
        else:
            logger.info("No new messages to summarize.")

    def on_summary_error(self, error):
        logger.error(f"Error creating periodic summary: {error}")
        self.display_message(f"Error creating summary: {error}", "System")

    def initialize_model_and_chat(self, model_name, system_prompt=""):
        if not system_prompt:
            system_prompt = self.DEFAULT_SYSTEM_PROMPT
        try:
            latest_summary = self.vectordb.get_latest_conversation_summary()
            if latest_summary:
                summary_prompt = f"\n\nLatest conversation summary: {latest_summary}"

            self.chat = init_model(model_name, system_prompt)
            if self.chat:
                self.display_message("Model initialized! Let's chat!", "System")
                self.worker = ChatWorker(self.chat, summary_prompt, self.vectordb, self.user_profile,
                                         self.personality_manager)
                self.worker.finished.connect(self.process_response)
                self.worker.error.connect(self.handle_error)
                self.worker.start()
            else:
                self.display_message("Error initializing model. Check console.", "System")
        except Exception as e:
            self.display_message(f"Error initializing model: {str(e)}", "System")

    def closeEvent(self, event):

        # Stop the speech recognition worker
        self.speech_recognition_worker.stop()
        self.speech_recognition_worker.wait()


        if self.summary_worker and self.summary_worker.isRunning():
            self.summary_worker.wait()
        self.vectordb.close()
        self.user_profile.save_profile()
        self.log_manager.log_message("System", "Application closed")
        super().closeEvent(event)


class OptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chat Options")
        self.parent = parent  # Store reference to parent (App)
        layout = QVBoxLayout()

        # --- Model Selection ---
        self.model_dropdown = QComboBox()
        self.model_dropdown.setFont(self.parent.font)  # Access parent's font
        self.update_model_dropdown()
        self.model_dropdown.currentTextChanged.connect(self.parent.on_model_changed)
        layout.addWidget(QLabel("Select Model:"))
        layout.addWidget(self.model_dropdown)

        # --- System Prompt Button ---
        sys_prompt_button = QPushButton("Set System Prompt")
        sys_prompt_button.clicked.connect(self.show_sys_prompt_dialog)
        layout.addWidget(sys_prompt_button)

        # --- Customization Buttons ---
        customize_layout = QHBoxLayout()
        self.bg_button = QPushButton("Background Color")
        self.bg_button.clicked.connect(self.parent.choose_bg_color)
        customize_layout.addWidget(self.bg_button)

        self.text_button = QPushButton("Text Color")
        self.text_button.clicked.connect(self.parent.choose_text_color)
        customize_layout.addWidget(self.text_button)

        self.font_button = QPushButton("Font")
        self.font_button.clicked.connect(self.parent.choose_font)
        customize_layout.addWidget(self.font_button)
        layout.addLayout(customize_layout)

        # --- User Preferences Button ---
        user_prefs_button = QPushButton("User Preferences")
        user_prefs_button.clicked.connect(self.show_user_prefs_dialog)
        layout.addWidget(user_prefs_button)

        # --- Personality System Button ---
        personality_button = QPushButton("AI Personality")
        personality_button.clicked.connect(self.show_personality_dialog)
        layout.addWidget(personality_button)

        # --- Dialog Buttons (OK and Cancel) ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Add Speak Aloud Checkbox
        self.speak_aloud_checkbox = QCheckBox("Read Responses Aloud")
        self.speak_aloud_checkbox.setChecked(parent.speak_aloud)
        self.speak_aloud_checkbox.stateChanged.connect(parent.toggle_speak_aloud)
        layout.addWidget(self.speak_aloud_checkbox)

        self.setLayout(layout)

    def show_sys_prompt_dialog(self):
        dialog = SystemPromptDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            system_prompt_text = dialog.system_prompt_input.toPlainText()
            self.parent.apply_system_prompt(system_prompt_text)

    def show_user_prefs_dialog(self):
        dialog = UserPreferencesDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update user preferences in the main app
            # ... (implementation to fetch and update preferences)
            pass
    def show_personality_dialog(self):
        dialog = PersonalityDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update personality settings in the main app
            # ... (implementation to fetch and update personality traits)
            pass
    def update_model_dropdown(self):
        models = get_available_models()
        self.model_dropdown.clear()
        self.model_dropdown.addItems(models)
        # Set the current index to the default model
        default_index = self.model_dropdown.findText(DEFAULT_MODEL)
        if default_index >= 0:
            self.model_dropdown.setCurrentIndex(default_index)


class SystemPromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set System Prompt")
        layout = QVBoxLayout()

        self.system_prompt_input = QTextEdit()
        self.system_prompt_input.setFont(parent.parent.font)  # Access main app's font
        self.system_prompt_input.setPlaceholderText("Enter System Prompt (optional)")
        layout.addWidget(QLabel("System Prompt:"))
        layout.addWidget(self.system_prompt_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

class UserPreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Preferences")
        layout = QVBoxLayout()
        self.parent = parent
        # Add preference inputs (e.g., communication style, interests)
        self.pref_inputs = {}
        for pref in ["communication_style", "interests","first_name", "last_name", "alias", "bio", "core_values", "primary_motivations"]:
            pref_layout = QHBoxLayout()
            pref_layout.addWidget(QLabel(pref.replace("_", " ").title()))
            pref_input = QLineEdit()
            pref_input.setText(self.parent.parent.user_profile.get_preference(pref, ""))
            pref_input.textChanged.connect(lambda text, p=pref: self.update_preference(p, text))
            self.pref_inputs[pref] = pref_input
            pref_layout.addWidget(pref_input)
            layout.addLayout(pref_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
    def update_preference(self, preference, value):
        self.parent.parent.user_profile.update_preference(preference, value)



class PersonalityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Personality Traits")
        self.parent = parent
        layout = QVBoxLayout()

        # Add sliders for each personality trait
        self.trait_sliders = {}
        for trait in ["formality", "humor", "empathy", "creativity", "assertiveness", "intelligence", "curiosity"]:
            trait_layout = QHBoxLayout()
            trait_layout.addWidget(QLabel(trait.title()))
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(int(self.parent.parent.personality_manager.personality.get_trait(trait) * 100))
            slider.valueChanged.connect(lambda value, t=trait: self.update_personality_trait(t, value / 100))
            self.trait_sliders[trait] = slider
            trait_layout.addWidget(slider)
            layout.addLayout(trait_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
    def update_personality_trait(self, trait, value):
        self.parent.parent.personality_manager.update_personality(trait, value)



class SpeechWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.queue = []
        self.tts_engine = pyttsx3.init()

    def add_text(self, text):
        self.queue.append(text)
        if not self.isRunning():
            self.start()

    def run(self):
        while self.queue:
            text = self.queue.pop(0)
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                self.error.emit(str(e))
        self.finished.emit()