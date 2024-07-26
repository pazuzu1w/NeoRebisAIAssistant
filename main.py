import sys
from PyQt6.QtWidgets import QApplication
from dotenv import load_dotenv
from gui import App
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

load_dotenv()




def initialize_app():
    global app_instance
    app_instance = App()




    # ... (rest of the App class remains the same)



# At the bottom of your main script file
if __name__ == '__main__':
    print("Starting application")
    app = QApplication(sys.argv)
    print("QApplication created")
    initialize_app()
    print("App instance created")
    app_instance.show()
    print("show() called on App instance")
    sys.exit(app.exec())