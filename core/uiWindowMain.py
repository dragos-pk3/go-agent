from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QDateEdit, QComboBox, QTextEdit, QPushButton
from PyQt5.QtCore import QDate
import sqlite3
import sys
import os

# # Add the project root directory to Python path
# project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(project_root)
import jsonSRW
from processDataClass import ProcessData
from htmlReplace import HTMLReplacer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.html_replacer = HTMLReplacer()

        self.setWindowTitle("Autovan Picker")

        # Create main layout
        layout = QVBoxLayout()

        # Start date picker
        self.start_date_picker = QDateEdit(self)
        self.start_date_picker.setCalendarPopup(True)
        self.start_date_picker.setDate(QDate.currentDate())
        self.start_date_picker.setDisplayFormat("dd.MM")
        layout.addWidget(self.start_date_picker)

        # End date picker
        self.end_date_picker = QDateEdit(self)
        self.end_date_picker.setCalendarPopup(True)
        self.end_date_picker.setDate(QDate.currentDate())
        self.end_date_picker.setDisplayFormat("dd.MM")
        layout.addWidget(self.end_date_picker)

        # ComboBox for Autorulota picker
        self.autovan_combo_box = QComboBox(self)
        layout.addWidget(self.autovan_combo_box)
        self.populate_autovan_combo_box()

        # Rich TextEdit for the generated output
        self.output_text_edit = QTextEdit(self)
        self.output_text_edit.setAcceptRichText(True)
        layout.addWidget(self.output_text_edit)

        # Button for generating output
        self.generate_button = QPushButton("Generate Output", self)
        self.generate_button.clicked.connect(self.generate_output)
        layout.addWidget(self.generate_button)

        # Set main layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def populate_autovan_combo_box(self):
        data = jsonSRW.read_json("__userfiles__\\user_config.json")
        conn = sqlite3.connect(data["DB_PATH"])
        cursor = conn.cursor()
        cursor.execute("SELECT vehicle_id, autovan_type, location_city FROM VehiclesSummary")
        rows = cursor.fetchall()
        for row in rows:
            self.autovan_combo_box.addItem(f"{row[1]} - {row[2]}", row[0])
        conn.close()

    def generate_output(self):
        start_date = self.start_date_picker.date().toString("dd.MM")
        end_date = self.end_date_picker.date().toString("dd.MM")
        selected_autovan = self.autovan_combo_box.currentText().split(" - ")[0]
        vehicle_id = self.autovan_combo_box.currentData()
        print(f"Selected Autovan: {selected_autovan}, Vehicle ID: {vehicle_id}, Start Date: {start_date}, End Date: {end_date}")
        # Process the data with the GUI values instead of using input()
        processed_data = ProcessData()
        processed_data.process(vehicle_id, start_date, end_date)

        if not processed_data:
            self.output_text_edit.setText("No data processed. Please check your inputs.")
            return

        # Use HTMLReplacer to process the template
        html_output = self.html_replacer.process_template(processed_data.output)
        self.output_text_edit.setHtml(html_output)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
