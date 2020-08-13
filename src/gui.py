"""Simple GUI application for using Schedule.py"""

# Nota: El módulo debería funcionar también con PyQt


import os
import sys
import webbrowser
import json
import types

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QIntValidator, QClipboard
from PySide2.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from schedule import Schedule, valid_nrc


class JsonObj(types.SimpleNamespace):
    """Class of json objects"""
    def __init__(self, json_dict):
        super().__init__(**json_dict)


def get_path(*path):
    """Gets the path of the file, from a executable or python environment"""
    return os.path.join(getattr(sys, "_MEIPASS", os.getcwd()), *path)


with open(get_path("assets", "gui_style.css"), mode="r", encoding="utf-8") as file:
    WINDOW_STYLE = file.read()

with open(get_path("assets", "calendars.json"), mode="r", encoding="utf-8") as file:
    OTHER_CALENDARS = json.load(file, object_hook=JsonObj)

with open(get_path("assets", "links.json"), mode="r", encoding="utf-8") as file:
    LINKS = json.load(file, object_hook=JsonObj)


class ScheduleView(QTableWidget):
    """Table view of the schedule"""

    def __init__(self, rows: int, columns: int, parent: QWidget):
        super().__init__(rows, columns, parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionMode(QTableWidget.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)

        horizontal_header = self.horizontalHeader()
        vertical_header = self.verticalHeader()

        horizontal_header.setSectionResizeMode(QHeaderView.Stretch)
        vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)

        self.setHorizontalHeaderLabels("LMWJVS")
        self.setVerticalHeaderLabels(
            ["08:30", "10:00", "11:30", "14:00", "15:30", "17:00", "18:30", "20:00"]
        )

    def update_size(self):
        """Updates the size of the widget"""
        # Ajusta verticalmente el widget a los contenidos
        self.setFixedHeight(
            self.horizontalHeader().height()
            + self.verticalHeader().length()
            + self.frameWidth() * 2
        )


class MainWindow(QMainWindow):
    """Main Window of the application"""

    def __init__(self):
        super().__init__()
        self.schedule_object = None
        self.init_ui()
        self.setStyleSheet(WINDOW_STYLE)
        self.setWindowTitle("NRC a iCalendar")
        self.setWindowIcon(QIcon(get_path("assets", "icon.svg")))
        self.clikboard = QClipboard()

        # Dialogo para guardar el archivo
        self.save_dialog = QFileDialog(self)
        self.save_dialog.setFileMode(QFileDialog.AnyFile)
        self.save_dialog.setNameFilter("iCalendar (*.ics)")
        self.save_dialog.setDefaultSuffix("ics")
        self.save_dialog.setAcceptMode(QFileDialog.AcceptSave)

    def init_ui(self):
        """Makes the layout"""

        # Barra de opciones y links de interés
        menu_bar = self.menuBar()

        options_menu = menu_bar.addMenu("&Opciones")
        act_allways_visible = options_menu.addAction("Siempre visible")
        act_allways_visible.setCheckable(True)
        act_allways_visible.toggled.connect(self.__allways_visible)

        calendars_menu = menu_bar.addMenu("&Calendarios")
        for calendar_group in OTHER_CALENDARS:
            section = calendars_menu.addMenu(calendar_group.name)
            for calendar in calendar_group.calendars:
                option = section.addAction(calendar.name)
                option.triggered.connect(lambda s=None, l=calendar.url: self.__to_clipboard(l))

        go_to_menu = menu_bar.addMenu("&Ir a")
        for i, link_group in enumerate(LINKS):
            for link in link_group.links:
                new_option = go_to_menu.addAction(link.description)
                new_option.triggered.connect(lambda s=None, l=link.url: webbrowser.open(l))
            if i - 1 != len(LINKS):
                go_to_menu.addSeparator()

        # Main widget

        main_widget = QFrame()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)
        main_widget.setLayout(main_layout)

        main_layout.setSizeConstraint(QLayout.SetMinimumSize)

        # Lista de códigos a ingresar
        code_layout = QHBoxLayout()
        main_layout.addLayout(code_layout)
        self.code_list = [QLineEdit(main_widget) for i in range(6)]
        code_validator = QIntValidator(main_layout, 10 ** 4, 10 ** 5)
        for code in self.code_list:
            code.setObjectName("code_field")
            code.setAlignment(Qt.AlignCenter)
            code.setMaxLength(5)
            code.setValidator(code_validator)
            code.textEdited.connect(self.check_codes)
            code_layout.addWidget(code)

        self.get_button = QPushButton("Obtener horario", main_widget)
        self.get_button.clicked.connect(self.get_schedule)
        self.get_button.setCursor(Qt.PointingHandCursor)
        self.get_button.setDisabled(True)
        main_layout.addWidget(self.get_button)

        self.schedule_view = ScheduleView(8, 6, main_widget)
        main_layout.addWidget(self.schedule_view)

        self.save_button = QPushButton("Guardar horario", main_widget)
        self.save_button.clicked.connect(self.save_schedule)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setDisabled(True)
        main_layout.addWidget(self.save_button)

        self.status_bar = QStatusBar(self)
        self.status_bar.showMessage("Ingrese los códigos NRC")
        self.setStatusBar(self.status_bar)

        self.adjustSize()

    def __allways_visible(self, option):
        flags = self.windowFlags()
        if option:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags ^ Qt.WindowStaysOnTopHint)
        self.show()

    def __to_clipboard(self, link):
        self.clikboard.setText(link)
        self.status_bar.showMessage("URL del calendario copiado a portapapeles")

    def check_codes(self):
        """Check if the codes are valid"""
        at_least_one_valid = False
        for code in self.code_list:
            if valid_nrc(code.text()):
                at_least_one_valid = True
            elif code.text():
                # TODO: cambiar el estilo al ser invalido y tener texto
                pass
            else:
                pass

        self.get_button.setDisabled(not at_least_one_valid)

        if at_least_one_valid:
            self.status_bar.clearMessage()
        else:
            self.status_bar.showMessage("Ingrese los códigos NRC")

    def get_schedule(self):
        """Get the schedule of BuscaCursos UC"""
        valid_codes = list(filter(valid_nrc, map(QLineEdit.text, self.code_list)))

        if not valid_codes:
            return

        try:
            self.schedule_object = Schedule.get(valid_codes)
        except OSError:
            error_box = QMessageBox(
                QMessageBox.Critical, "Error", "No se ha podido importar el horario"
            )
            error_box.exec_()
        else:
            self.show_schedule()

    def show_schedule(self):
        """Show the schedule in the table"""
        # Limpia el horario
        self.schedule_view.clearContents()

        # Si no hay módulos, se deshabilita la opción de guardar y termina
        if not self.schedule_object.courses:
            self.schedule_view.update_size()
            self.save_button.setDisabled(True)
            return

        # Si existen módulos, se muestran en el horario
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

        self.schedule_view.update_size()
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
    window.schedule_view.update_size()  # Esto no debería estar aquí, pero es donde funciona (creo)
    sys.exit(app.exec_())
