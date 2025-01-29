from PyQt5.QtWidgets import (
   QApplication,
   QMainWindow,
   QVBoxLayout,
   QWidget,
   QDateEdit,
   QComboBox,
   QTextEdit,
   QPushButton,
   QHBoxLayout,
   QLabel,
   QSpacerItem,
   QSizePolicy,
   QAction,
   QTabWidget,
   QTableWidget,
   QTableWidgetItem,
   QFormLayout,
   QLineEdit,
   QMessageBox,
   QCheckBox,
   QFileDialog,
   QRadioButton,
   QButtonGroup
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDate
import sqlite3
import sys
import os
from functools import partial
import jsonSRW
from datetime import datetime
from processDataClass import ProcessData
from docxReplace import DocxReplace
from htmlReplace import HTMLReplacer
icon_path = "__userfiles__/rv.ico"
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.html_replacer = HTMLReplacer()
        self.docx_replacer = DocxReplace()
        self.setWindowTitle("GoCamper Suite")
        self.setWindowIcon(QIcon(icon_path))
        self.init_menu()
        self.init_tabs()
        self.user_preferences = jsonSRW.read_json("__userfiles__/user_preferences.json")
        self.reload_factura_content()
        
        # Move the window to the top-left corner of the screen
        self.move(0, 0)

    def init_menu(self):
        menu_bar = self.menuBar()

        settings_menu = menu_bar.addMenu("Settings")

        files_action = QAction("Files", self)
        configuration_action = QAction("Preferences", self)
        
        files_action.triggered.connect(self.open_files_window)
        configuration_action.triggered.connect(self.open_configuration_window)
       
        settings_menu.addAction(files_action)
        settings_menu.addAction(configuration_action)
    
    def init_tabs(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.create_offers_tab()
        self.create_contracts_tab()
        #self.create_procura_tab()
        self.create_db_tab()
        #TODO: Reservation Confirmation Tab

    #region Menu Actions
    def open_files_window(self):
        self.files_window = QWidget()
        self.files_window.setWindowTitle("Files")
        self.files_layout = QVBoxLayout()

        user_config = jsonSRW.read_json("__userfiles__/user_config.json")

        for key, value in user_config.items():
            row_layout = QHBoxLayout()

            label = QLabel(f"{key}:")
            text_field = QLineEdit(str(value))
            text_field.setObjectName(key)

            browse_button = QPushButton("Browse")
            browse_button.setObjectName(f"browse_{key}")
            # Connect the button to a function that opens a file dialog
            browse_button.clicked.connect(partial(self.browse_file, text_field)) if "OUTPUT_PATH" not in key else browse_button.clicked.connect(partial(self.browse_folder, text_field))

            row_layout.addWidget(label)
            row_layout.addWidget(text_field)
            row_layout.addWidget(browse_button)

            self.files_layout.addLayout(row_layout)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_files)
        self.files_layout.addWidget(save_button)

        self.files_window.setLayout(self.files_layout)
        self.files_window.show()

    def browse_file(self, text_field):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self.files_window,
            "Select File",
            "",
            "All Files (*);;Text Files (*.txt)",
            options=options
        )
        if file_name:
            text_field.setText(file_name)

    def browse_folder(self, text_field):
        folder_name = QFileDialog.getExistingDirectory(self.files_window, "Select Folder")
        if folder_name:
            text_field.setText(folder_name)

    def save_files(self):
        user_config = {}
        for widget in self.files_window.findChildren(QLineEdit):
            user_config[widget.objectName()] = widget.text()

        try:
            jsonSRW.write_json("__userfiles__/user_config.json", user_config)
            QMessageBox.information(self, "Success", "Preferences saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save preferences: {e}")
        finally:
            self.files_window.close()
    # Configuration Window        
    def open_configuration_window(self):
        self.preferences_window = QWidget()
        self.preferences_window.setWindowTitle("Preferences")
        self.preferences_layout = QVBoxLayout()

        self.user_preferences = jsonSRW.read_json("__userfiles__/user_preferences.json")

        for key, value in self.user_preferences.items():
            label = QLabel(f"{key}:")
            text_field = QLineEdit(str(value))
            text_field.setObjectName(key)
            self.preferences_layout.addWidget(label)
            self.preferences_layout.addWidget(text_field)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_preferences)
        self.preferences_layout.addWidget(save_button)

        self.preferences_window.setLayout(self.preferences_layout)
        self.preferences_window.show()

    def save_preferences(self):
        user_config = {}
        for widget in self.preferences_window.findChildren(QLineEdit):
            user_config[widget.objectName()] = widget.text()

        try:
            jsonSRW.write_json("__userfiles__/user_preferences.json", user_config)
            QMessageBox.information(self, "Success", "Preferences saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save preferences: {e}")
        finally:
            self.preferences_window.close()
    #endregion

    #region Tabs Implementations
    def create_offers_tab(self):
        offers_tab = QWidget()
        layout = QVBoxLayout()
        horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        start_date_widget = QWidget()
        startDateLayout = QHBoxLayout(start_date_widget)
        self.start_date_label = QLabel(self)
        self.start_date_label.setText("Start Date: ")
        # Start date picker
        self.start_date_picker = QDateEdit(self)
        self.start_date_picker.setCalendarPopup(True)
        self.start_date_picker.setDate(QDate.currentDate())
        self.start_date_picker.setDisplayFormat("dd.MM")
        self.start_date_picker.setFixedSize(120, 30)
        startDateLayout.addWidget(self.start_date_label)
        startDateLayout.addWidget(self.start_date_picker)
        startDateLayout.addItem(horizontal_spacer)
        layout.addWidget(start_date_widget)
        #TODO: CHECKBOX To automatically set end date to 3 days from start date after start date is set, if checked
        end_date_widget = QWidget() 
        endDateLayout = QHBoxLayout(end_date_widget)
        self.end_date_label = QLabel(self)
        self.end_date_label.setText("End Date: ")
        # End date picker
        self.end_date_picker = QDateEdit(self)
        self.end_date_picker.setCalendarPopup(True)
        self.end_date_picker.setDate(QDate.currentDate().addDays(3))
        self.end_date_picker.setDisplayFormat("dd.MM")
        self.end_date_picker.setFixedSize(120, 30)
        endDateLayout.addWidget(self.end_date_label)
        endDateLayout.addWidget(self.end_date_picker)
        endDateLayout.addItem(horizontal_spacer)
        layout.addWidget(end_date_widget)
        days_widget = QWidget()
        daysLayout = QHBoxLayout(days_widget)
        
        # High Days
        self.high_days_label = QLabel(self)
        self.high_days_label.setText("High Nights: ")
        self.high_days_value = QLabel(self)
        self.high_days_value.setText("0")
        daysLayout.addWidget(self.high_days_label)
        daysLayout.addWidget(self.high_days_value)
        
        # Low Days
        self.low_days_label = QLabel(self)
        self.low_days_label.setText("Low Nights: ")
        self.low_days_value = QLabel(self)
        self.low_days_value.setText("0")
        daysLayout.addWidget(self.low_days_label)
        daysLayout.addWidget(self.low_days_value)
        
        # Standard Days
        self.standard_days_label = QLabel(self)
        self.standard_days_label.setText("Standard Nights: ")
        self.standard_days_value = QLabel(self)
        self.standard_days_value.setText("0")
        daysLayout.addWidget(self.standard_days_label)
        daysLayout.addWidget(self.standard_days_value)
        daysLayout.addItem(horizontal_spacer)
        layout.addWidget(days_widget)
        self.autovan_combo_box = QComboBox(self)
        layout.addWidget(self.autovan_combo_box)
        self.populate_autovan_combo_box(self.autovan_combo_box)

        self.output_text_edit = QTextEdit(self)
        self.output_text_edit.setAcceptRichText(True)
        layout.addWidget(self.output_text_edit)

        self.generate_button = QPushButton("Generate Output", self)
        self.generate_button.clicked.connect(self.generate_output)
        layout.addWidget(self.generate_button)

        offers_tab.setLayout(layout)
        self.tabs.addTab(offers_tab, "Offers")

    def create_contracts_tab(self):
        contracts_tab = QWidget()
        layout = QFormLayout()
        self.companyCheckbox = QCheckBox("Include Company Details")
        self.companyCheckbox.toggled.connect(self.toggleCompanyFields)
        layout.addWidget(self.companyCheckbox)

        # Company fields
        self.numeFirma = QLineEdit()
        self.adresaFirma = QLineEdit()
        self.firmaReg = QLineEdit()
        self.firmaCUI = QLineEdit()
        # Client fields
        self.numeClient = QLineEdit()
        self.prenumClient = QLineEdit()
        self.adresaClient = QLineEdit()
        self.serieCIClient = QLineEdit()
        self.nrCIClient = QLineEdit()
        self.cnpClient = QLineEdit()
        self.dataEmitereCI = QLineEdit()
        self.emisCIDe = QLineEdit()
        self.seriaPermisClient = QLineEdit()
        self.dataEmiterePermis = QLineEdit()
        self.emisPermisDe = QLineEdit()
        self.telefonClient = QLineEdit()
        self.autovanAles = QComboBox()
        self.populate_autovan_combo_box(self.autovanAles)
        self.nrNopti = QLineEdit()
        self.tarifPerNoapte = QLineEdit()
        self.startDate = QDateEdit()
        self.startDate.setCalendarPopup(True)
        self.startDate.setDate(QDate.currentDate())
        self.endDate = QDateEdit()
        self.endDate.setCalendarPopup(True)
        self.endDate.setDate(QDate.currentDate().addDays(3))

        # Radio buttons for "Dl." and "Dna."
        self.mrRadioButton = QRadioButton("Dl.")
        self.mrsRadioButton = QRadioButton("Dna.")
        self.mrRadioButton.setChecked(True)
        self.genderGroup = QButtonGroup()
        self.genderGroup.addButton(self.mrRadioButton)
        self.genderGroup.addButton(self.mrsRadioButton)

        # FGO Title
        self.facturaTitle = QTextEdit()
        self.reload_factura_content()
        self.facturaTitle.setText(self.factura_content)
        # Company fields to layout
        layout.addRow(QLabel("Nume Firmă:"), self.numeFirma)
        layout.addRow(QLabel("Adresă Firmă:"), self.adresaFirma)
        layout.addRow(QLabel("Firmă Reg.:"), self.firmaReg)
        layout.addRow(QLabel("Firmă CUI:"), self.firmaCUI)
        self.toggleCompanyFields(False)
        # Gender layout
        genderLayout = QVBoxLayout()
        genderLayout.addWidget(self.mrRadioButton)
        genderLayout.addWidget(self.mrsRadioButton)
        layout.addRow(QLabel("Title:"), genderLayout)
        # Client fields to layout
        layout.addRow(QLabel("Nume Client:"), self.numeClient)
        layout.addRow(QLabel("Prenume Client:"), self.prenumClient)
        layout.addRow(QLabel("Adresa Client:"), self.adresaClient)
        layout.addRow(QLabel("Serie CI Client:"), self.serieCIClient)
        layout.addRow(QLabel("Număr CI Client:"), self.nrCIClient)
        layout.addRow(QLabel("CNP Client:"), self.cnpClient)
        layout.addRow(QLabel("Data Emitere CI:"), self.dataEmitereCI)
        layout.addRow(QLabel("Emis CI De:"), self.emisCIDe)
        layout.addRow(QLabel("Seria Permis Client:"), self.seriaPermisClient)
        layout.addRow(QLabel("Data Emitere Permis:"), self.dataEmiterePermis)
        layout.addRow(QLabel("Emis Permis De:"), self.emisPermisDe)
        layout.addRow(QLabel("Telefon Client:"), self.telefonClient)
        layout.addRow(QLabel("Autovan Ales:"), self.autovanAles)
        layout.addRow(QLabel("Nr. Nopți:"), self.nrNopti)
        layout.addRow(QLabel("Tarif per Noapte:"), self.tarifPerNoapte)
        layout.addRow(QLabel("Start Date:"), self.startDate)
        layout.addRow(QLabel("End Date:"), self.endDate)

        self.generateContract = QPushButton("Generate Contract")
        self.generateContract.clicked.connect(self.generate_contract)
        self.refreshContent = QPushButton("Refresh")
        self.refreshContent.clicked.connect(self.refresh_contract)

        layout.addRow(self.generateContract, self.refreshContent)

        layout.addRow(self.facturaTitle)
        contracts_tab.setLayout(layout)
        self.tabs.addTab(contracts_tab, "Contracts")
    def toggleCompanyFields(self, checked):
        """Enable or disable company fields based on the checkbox state."""
        self.numeFirma.setEnabled(checked)
        self.adresaFirma.setEnabled(checked)
        self.firmaReg.setEnabled(checked)
        self.firmaCUI.setEnabled(checked)
    # def create_procura_tab(self):
    #     procura_tab = QWidget()
    #     self.tabs.addTab(procura_tab, "Procura")
    def create_db_tab(self):
        db_tab = QWidget()
        db_path = "__userfiles__/SQLGoCamper.db"  
        self.connection = sqlite3.connect(db_path)
        
        layout = QVBoxLayout()
        db_tab.setLayout(layout)
        
        self.table_selector = QComboBox()
        self.table_selector.currentIndexChanged.connect(self.display_table)
        layout.addWidget(self.table_selector)
        
        self.table_widget = QTableWidget()
        # Enable editing
        self.table_widget.setEditTriggers(QTableWidget.AllEditTriggers)
        layout.addWidget(self.table_widget)
        
        # Add a button to insert a new row
        self.add_row_button = QPushButton("Add New Row")
        self.add_row_button.clicked.connect(self.add_new_row)
        layout.addWidget(self.add_row_button)
        
        # Add a button to delete the selected row
        self.delete_row_button = QPushButton("Delete Selected Row")
        self.delete_row_button.clicked.connect(self.delete_selected_row)
        layout.addWidget(self.delete_row_button)
        
        # Add a button to save changes to the database
        self.save_changes_button = QPushButton("Save Changes")
        self.save_changes_button.clicked.connect(self.save_changes_to_database)
        layout.addWidget(self.save_changes_button)
        
        self.populate_tables()
        self.tabs.addTab(db_tab, "DB")
    
    def populate_tables(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            self.table_selector.addItems([table[0] for table in tables])
        except sqlite3.Error as e:
            print(f"Error retrieving tables: {e}")
    
    def display_table(self):
        table_name = self.table_selector.currentText()
        if table_name:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"SELECT * FROM [{table_name}]")
                rows = cursor.fetchall()
                
                if not cursor.description:
                    print("No data returned")
                    return
                
                column_names = [description[0] for description in cursor.description]
                
                self.table_widget.setRowCount(len(rows))
                self.table_widget.setColumnCount(len(column_names))
                self.table_widget.setHorizontalHeaderLabels(column_names)
                
                for row_idx, row in enumerate(rows):
                    for col_idx, cell in enumerate(row):
                        item = QTableWidgetItem(str(cell) if cell is not None else "")
                        self.table_widget.setItem(row_idx, col_idx, item)
            except sqlite3.Error as e:
                print(f"Error displaying table {table_name}: {e}")

    def save_changes_to_database(self):
        """Save all changes made in the table widget to the database."""
        table_name = self.table_selector.currentText()
        if table_name:
            try:
                cursor = self.connection.cursor()
                for row in range(self.table_widget.rowCount()):
                    primary_key_value = self.table_widget.item(row, 0).text()
                    values = [self.table_widget.item(row, col).text() for col in range(self.table_widget.columnCount())]
                    
                    # Check if the row is new (i.e., primary key is empty)
                    if not primary_key_value:
                        placeholders = ', '.join(['?'] * len(values))
                        cursor.execute(f"INSERT INTO [{table_name}] VALUES ({placeholders})", values)
                    else:
                        set_clause = ', '.join([f"{self.table_widget.horizontalHeaderItem(col).text()} = ?" for col in range(1, self.table_widget.columnCount())])
                        cursor.execute(f"UPDATE [{table_name}] SET {set_clause} WHERE {self.table_widget.horizontalHeaderItem(0).text()} = ?", values[1:] + [primary_key_value])
                
                self.connection.commit()
                QMessageBox.information(self, "Success", "Changes saved successfully.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"Failed to save changes: {e}")

    def closeEvent(self, event):
        self.connection.close()
        super().closeEvent(event)

    #endregion

    #region Implementations
    def populate_autovan_combo_box(self,comboBox):
        data = jsonSRW.read_json("__userfiles__/user_config.json")
        conn = sqlite3.connect(data["DATABASE_PATH"])
        cursor = conn.cursor()
        
        # Modified query to get distinct combinations of type and city
        cursor.execute("""
            SELECT MIN(vehicle_id) as vehicle_id, autovan_type, location_city 
            FROM VehiclesSummary 
            GROUP BY autovan_type, location_city
        """)
        
        rows = cursor.fetchall()
        for row in rows:
            comboBox.addItem(f"{row[1]} - {row[2]}", row[0])
        conn.close()

    def generate_output(self):
        start_date = self.start_date_picker.date().toString("dd.MM")
        end_date = self.end_date_picker.date().toString("dd.MM")
        selected_autovan = self.autovan_combo_box.currentText().split(" - ")[0]
        vehicle_id = self.autovan_combo_box.currentData()
        # Process the data with the GUI values instead of using input()
        processed_data = ProcessData()
        processed_data.process(vehicle_id, start_date, end_date)

        if not processed_data:
            self.output_text_edit.setText("No data processed. Please check your inputs.")
            return

        self.low_days_value.setText(str(processed_data.output["Low Days"]))
        self.standard_days_value.setText(str(processed_data.output["Standard Days"]))
        self.high_days_value.setText(str(processed_data.output["High Days"]))
        # Use HTMLReplacer to process the template
        html_output = self.html_replacer.process_template(processed_data.output)
        self.output_text_edit.setHtml(html_output)
    def generate_contract(self):
        # Check if any required fields are empty
        required_fields = [

            self.numeClient, self.prenumClient, self.adresaClient, self.serieCIClient,
            self.nrCIClient, self.cnpClient, self.dataEmitereCI, self.emisCIDe,
            self.seriaPermisClient, self.dataEmiterePermis, self.emisPermisDe,
            self.telefonClient, self.nrNopti, self.tarifPerNoapte
        ]
        if self.companyCheckbox.isChecked():
            required_fields.extend([self.numeFirma, self.adresaFirma, self.firmaReg, self.firmaCUI])

        for field in required_fields:
            if not field.text():
                QMessageBox.warning(self, "Incomplete Fields", "Please fill in all required fields.")
                return
        self.user_preferences = jsonSRW.read_json("__userfiles__/user_preferences.json")
        todayDate = datetime.now().strftime("%d.%m.%Y")
        nrDoc = int(self.user_preferences["CONTRACT_NUMBER"]) + 1
        self.user_preferences["CONTRACT_NUMBER"] = str(nrDoc)
        jsonSRW.write_json("__userfiles__/user_preferences.json", self.user_preferences)
        docData = {
            "NrDoc": str(nrDoc),
            "todayDate": todayDate,
            "numeFirma": self.numeFirma.text(),
            "adresaFirma": self.adresaFirma.text(),
            "firmaReg": self.firmaReg.text(),
            "firmaCUI": self.firmaCUI.text(),
            "pronounClient": self.mrRadioButton.isChecked() and "Dl." or "Dna.",
            "numeClient": self.numeClient.text(),
            "prenumClient": self.prenumClient.text(),
            "adresaClient": self.adresaClient.text(),
            "serieCIClient": self.serieCIClient.text(),
            "nrCIClient": self.nrCIClient.text(),
            "cnpClient": self.cnpClient.text(),
            "dataEmitereCI": self.dataEmitereCI.text(),
            "emisCIDe": self.emisCIDe.text(),
            "seriaPermisClient": self.seriaPermisClient.text(),
            "dataEmiterePermis": self.dataEmiterePermis.text(),
            "emisPermisDe": self.emisPermisDe.text(),
            "telefonClient": self.telefonClient.text(),
            "autovanAles": self.autovanAles.currentText().split(" - ")[0],
            "autovanLocation":self.autovanAles.currentText().split(" - ")[1],
            "nrNopti": self.nrNopti.text(),
            "tarifPerNoapte": self.tarifPerNoapte.text(),
            "startDate": self.startDate.date().toString("dd.MM.yyyy"),
            "endDate": self.endDate.date().toString("dd.MM.yyyy")
        }
        self.docx_replacer.process_template(docData, self.companyCheckbox.isChecked())
        QMessageBox.information(self, "Contract Generated", "Contract generated successfully.")
        
        # Read from "__userfiles__/factura.txt" and set the content to facturaTitle QTextEdit
        self.reload_factura_content()
        self.facturaTitle.setText(self.factura_content)
    def reload_factura_content(self):
        with open("__userfiles__/factura.txt", "r", encoding="utf-8") as file:
            self.factura_content = file.read()
    def refresh_contract(self):
        # Assuming contract_tab has text fields that need to be reset
        reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to refresh the contract?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        contracts_tab = self.tabs.widget(1)  # Assuming the "Contracts" tab is the second tab
        for widget in contracts_tab.findChildren(QLineEdit):
            widget.clear()
        for widget in contracts_tab.findChildren(QComboBox):
            widget.setCurrentIndex(0)
        for widget in contracts_tab.findChildren(QTextEdit):
            widget.clear()
        for widget in contracts_tab.findChildren(QDateEdit):
            widget.setDate(QDate.currentDate())
        self.reload_factura_content()
        self.facturaTitle.setText(self.factura_content)
        self.endDate.setDate(QDate.currentDate().addDays(3))
    #endregion

    def add_new_row(self):
        """Add a new row to the table widget."""

        # Insert the new row
        current_row_count = self.table_widget.rowCount()
        self.table_widget.insertRow(current_row_count)

        # Optionally, set default values for the new row
        for col in range(self.table_widget.columnCount()):
            self.table_widget.setItem(current_row_count, col, QTableWidgetItem(""))


    def delete_selected_row(self):
        """Delete the selected row from the table and database."""
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a row to delete.")
            return

        reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to delete the selected row?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            table_name = self.table_selector.currentText()
            primary_key_value = self.table_widget.item(current_row, 0).text()

            if table_name and primary_key_value:
                try:
                    cursor = self.connection.cursor()
                    # Assuming the first column is the primary key
                    primary_key_column = self.table_widget.horizontalHeaderItem(0).text()
                    cursor.execute(f"DELETE FROM [{table_name}] WHERE {primary_key_column} = ?", (primary_key_value,))
                    self.connection.commit()
                    self.table_widget.removeRow(current_row)
                except sqlite3.Error as e:
                    print(f"Error deleting row from database: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    app.exec_()
