import sys
from PyQt6.QtWidgets import QApplication
from dotenv import load_dotenv
from Gui import App
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

load_dotenv()



if __name__ == '__main__':
    print("Starting application")
    app = QApplication(sys.argv)
    print("QApplication created")
    ex = App()
    print("App instance created")
    ex.show()
    print("show() called on App instance")
    sys.exit(app.exec())