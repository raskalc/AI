import sys
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import QUrl

# 1. Create the application instance
app = QGuiApplication(sys.argv)

# 2. Create the QML engine
engine = QQmlApplicationEngine()

# 3. Load the QML file
# We use QUrl.fromLocalFile() to convert the local file path to a URL
qml_file_path = "design/Group_5.qml"
engine.load(QUrl.fromLocalFile(qml_file_path))

# Check if the QML loaded successfully
if not engine.rootObjects():
    sys.exit(-1)

# Connect the engine's quit signal to the application's quit slot
engine.quit.connect(app.quit)

# 4. Start the application event loop
sys.exit(app.exec_())