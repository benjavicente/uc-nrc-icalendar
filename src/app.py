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
)
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt


from schedule import Schedule


class MainWindow(QWidget):
    """Main Wondow of the application"""

    def __init__(self):
        super().__init__()
        self.schedule_object = None
        self.init_ui()

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
            code_layout.addWidget(code)

        self.get_button = QPushButton("Obtener horario", self)
        self.get_button.clicked.connect(self.get_schedule)
        main_layout.addWidget(self.get_button)

        # TODO: tabla en vez de texto monoespaciado
        self.schedule_view = QTextEdit(self)
        self.schedule_view.setFont(QFont("consolas", QFont.Monospace))
        self.schedule_view.setReadOnly(True)
        main_layout.addWidget(self.schedule_view)

        self.save_button = QPushButton("Guardar horario", self)
        self.save_button.clicked.connect(self.save_schedule)
        main_layout.addWidget(self.save_button)

    def get_schedule(self):
        """Get the schedule of Buscacursos UC"""
        self.schedule_object = Schedule.get_courses(map(QLineEdit.text, self.code_list))
        self.schedule_view.setText(self.schedule_object.display())

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
