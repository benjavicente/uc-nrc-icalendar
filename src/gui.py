"""Simple GUI application for using Schedule.py"""

# Nota: El módulo debería funcionar también con PyQt


import os
import sys

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from schedule import Schedule, valid_nrc


def get_path(*path):
    """Gets the path of the file, from a executable or python environment"""
    return os.path.join(getattr(sys, "_MEIPASS", os.getcwd()), *path)


with open(get_path("assets", "gui_style.css"), mode="r", encoding="utf-8") as file:
    WINDOW_STYLE = file.read()


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


class MainWindow(QWidget):
    """Main Wondow of the application"""

    # TODO: usar QWindow

    def __init__(self):
        super().__init__()
        self.schedule_object = None
        self.init_ui()
        self.setStyleSheet(WINDOW_STYLE)
        self.setWindowTitle("NRC a iCalendar")
        self.setWindowIcon(QIcon(get_path("assets", "icon.svg")))

        # Dialogo para guradar el archivo
        self.save_dialog = QFileDialog(self)
        self.save_dialog.setFileMode(QFileDialog.AnyFile)
        self.save_dialog.setNameFilter("iCalendar (*.ics)")
        self.save_dialog.setDefaultSuffix("ics")
        self.save_dialog.setAcceptMode(QFileDialog.AcceptSave)

    def init_ui(self):
        """Makes the layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setSizeConstraint(QLayout.SetMinimumSize)

        # Lista de códigos a ingresar
        code_layout = QHBoxLayout()
        main_layout.addLayout(code_layout)
        self.code_list = [QLineEdit(self) for i in range(6)]
        for code in self.code_list:
            code.setObjectName("code_field")
            code.setAlignment(Qt.AlignCenter)
            code.setMaxLength(5)
            # code.setInputMask("99999")
            # Funciona para limitar input numérico, pero es muy molesto, ya que
            # requeña el QLineEdit con espacios y cambia el modo de escritura a
            # instertar cuando está lleno.
            code_layout.addWidget(code)

        self.get_button = QPushButton("Obtener horario", self)
        self.get_button.clicked.connect(self.get_schedule)
        self.get_button.setCursor(Qt.PointingHandCursor)
        main_layout.addWidget(self.get_button)

        self.schedule_view = ScheduleView(8, 6, self)
        main_layout.addWidget(self.schedule_view)

        self.save_button = QPushButton("Guardar horario", self)
        self.save_button.clicked.connect(self.save_schedule)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setDisabled(True)
        main_layout.addWidget(self.save_button)

        self.adjustSize()

    def get_schedule(self):
        """Get the schedule of Buscacursos UC"""
        # TODO: limpiar el método
        # Se debería habilitar el botón para obtener cursos cuando al menos
        # uno de los códigos es valido

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
            return

        # Limpia el horario
        self.schedule_view.clearContents()

        # Si no hay módulos, se deshabilita la opción de guardar y termina
        if not self.schedule_object:
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
