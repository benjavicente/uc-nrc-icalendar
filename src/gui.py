"""Simple GUI application for using Schedule.py"""

# Nota: El módulo debe´ria funcionar también con PyQt


import sys

from PySide2.QtWidgets import (
    QApplication,
    QBoxLayout,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QTableWidget,
    QLabel,
    QFrame,
)
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt


from schedule import Schedule


def import_style():
    with open("gui.css", encoding="utf-8") as file:
        content = file.read()
    return content


class MainWindow(QWidget):
    """Main Wondow of the application"""

    def __init__(self):
        super().__init__()
        self.schedule_object = None
        self.init_ui()
        self.setStyleSheet(import_style())

        # Dialogo para guradar el archivo
        self.save_dialog = QFileDialog(self)
        self.save_dialog.setFileMode(QFileDialog.AnyFile)
        self.save_dialog.setNameFilter("iCalendar (*.ics)")
        self.save_dialog.setDefaultSuffix("ics")
        self.save_dialog.setAcceptMode(QFileDialog.AcceptSave)

    def init_ui(self):
        """Makes the layout"""
        main_layout = QVBoxLayout(self)

        code_layout = QHBoxLayout()
        main_layout.addLayout(code_layout)

        # Lista de códigos a ingresar
        self.code_list = [QLineEdit(self) for i in range(6)]
        for code in self.code_list:
            code.setObjectName("code_field")
            code.setAlignment(Qt.AlignCenter)
            code_layout.addWidget(code)

        self.get_button = QPushButton("Obtener horario", self)
        self.get_button.clicked.connect(self.get_schedule)
        main_layout.addWidget(self.get_button)

        self.schedule_view = QTableWidget(8, 6, self)
        main_layout.addWidget(self.schedule_view)

        table_h_header = self.schedule_view.horizontalHeader()
        table_h_header.setSectionResizeMode(table_h_header.Stretch)
        table_v_header = self.schedule_view.verticalHeader()
        table_v_header.setSectionResizeMode(table_v_header.ResizeToContents)

        self.save_button = QPushButton("Guardar horario", self)
        self.save_button.clicked.connect(self.save_schedule)
        self.save_button.setDisabled(True)
        main_layout.addWidget(self.save_button)

    def get_schedule(self):
        """Get the schedule of Buscacursos UC"""
        self.schedule_object = Schedule.get_courses(map(QLineEdit.text, self.code_list))
        # TODO: ver si existen módulos, para bloquear la opción de crear calendario

        self.schedule_view.clearContents()
        for i_row, row in enumerate(self.schedule_object.get_table()):
            for sub_row in row:
                for i_col, element in enumerate(sub_row):

                    if not element:
                        continue

                    module_label = QLabel(self.schedule_view)
                    module_label.setText(element.code)
                    module_label.setObjectName(element.type_)
                    module_label.setAlignment(Qt.AlignCenter)
                    module_label.setFixedHeight(20)
    
                    cell_frame = self.schedule_view.cellWidget(i_row, i_col)
    
                    # Se crea un frame para los widgets si no existe
                    if not cell_frame:
                        cell_frame = QFrame(self.schedule_view)
                        cell_layout = QVBoxLayout(cell_frame)
                        cell_layout.setSpacing(0)
                        cell_layout.setMargin(0)
                        self.schedule_view.setCellWidget(i_row, i_col, cell_frame)

                    cell_frame.layout().addWidget(module_label)

        # TODO: topes de horario no se mestran correctamente, no se expande automáticamente

        self.save_button.setDisabled(False)

    def save_schedule(self):
        """Saves the schedule"""
        if self.save_dialog.exec_():
            out_dir = self.save_dialog.selectedFiles()[0]
            with open(out_dir, mode="w", encoding="utf-8") as file:
                file.write(self.schedule_object.to_ics())


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
