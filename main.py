import sys
from PyQt6.QtWidgets import QApplication
from dotenv import load_dotenv
from gui import App
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

load_dotenv()











if __name__ == '__main__':
    print("Starting application")
    app = QApplication(sys.argv)
    print("QApplication created")
    window = App()
    print("App created")
    window.show()
    print("App shown")
    
    sys.exit(app.exec())