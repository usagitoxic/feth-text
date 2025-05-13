import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QCheckBox, QFileDialog, QLineEdit, QLabel, QDialog, QTextEdit, QFormLayout, QDialogButtonBox, QHeaderView
from PyQt5.QtCore import Qt, QTimer

class EditDialog(QDialog):
    def __init__(self, original_text, translated_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование строки")

        self.resize(600, 600)

        # Создаем форму для ввода
        self.original_text = QTextEdit(self)
        self.original_text.setPlainText(original_text)
        self.original_text.setReadOnly(True)

        self.translated_text = QTextEdit(self)
        self.translated_text.setPlainText(translated_text)

        # Кнопки подтверждения
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        # Кнопка Clone
        self.clone_button = QPushButton("Clone", self)
        self.clone_button.clicked.connect(self.clone_text)

        # Макет формы
        layout = QFormLayout(self)
        layout.addRow("Исходный текст:", self.original_text)
        layout.addRow("Перевод:", self.translated_text)
        layout.addWidget(self.clone_button)
        layout.addWidget(self.buttons)

    def clone_text(self):
        """Копирует текст из оригинала в перевод"""
        self.translated_text.setPlainText(self.original_text.toPlainText())

    def get_translated_text(self):
        """Возвращает текст перевода из поля ввода"""
        return self.translated_text.toPlainText()


class CSVEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bundle Editor")
        self.resize(1280, 600)

        self.stats_label = QLabel("Статистика: 0 строк, 0 непереведённых (0%)")

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Запрещаем редактирование в таблице
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # Выделение всей строки при клике
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.doubleClicked.connect(self.on_double_click)

        # Инициализируем переменную для хранения текущего файла
        self.current_file = None

        # Чекбокс для отображения непереведенных строк
        self.show_untranslated_checkbox = QCheckBox("Показать непереведенные строки")
        self.show_untranslated_checkbox.stateChanged.connect(self.apply_filter)

        # Строка для поиска по destination_language
        self.search_line_edit = QLineEdit(self)
        self.search_line_edit.setPlaceholderText("Поиск")

        # Строка для поиска по file_type
        self.file_type_search_line_edit = QLineEdit(self)
        self.file_type_search_line_edit.setPlaceholderText("file_type")

        # Создаем таймер для задержки при поиске
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)  # Ожидаем завершения ввода
        self.search_timer.timeout.connect(self.apply_filter)  # Выполняем фильтрацию после задержки

        self.search_line_edit.textChanged.connect(self.on_search_text_changed)
        self.file_type_search_line_edit.textChanged.connect(self.on_search_text_changed)

        # Кнопки для открытия и сохранения файлов
        load_btn = QPushButton("Открыть CSV")
        load_btn.clicked.connect(self.load_csv)

        save_btn = QPushButton("Сохранить CSV")
        save_btn.clicked.connect(self.save_csv)

        # Размещение кнопок в горизонтальном layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(save_btn)

        # Основной layout
        layout = QVBoxLayout()
        layout.addWidget(self.show_untranslated_checkbox)
        layout.addWidget(self.search_line_edit)
        layout.addWidget(self.file_type_search_line_edit)
        layout.addLayout(btn_layout)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.table)

        # Создаем контейнер для центра окна
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_csv(self):
        """Загружаем CSV файл в таблицу"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть CSV", "", "CSV файлы (*.csv)")
        if not file_path:
            return

        self.current_file = file_path
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            data = list(reader)

        self.table.clear()
        self.table.setRowCount(len(data) - 1)
        self.table.setColumnCount(len(data[0]))
        self.table.setHorizontalHeaderLabels(data[0])

        # Заполнение таблицы данными из CSV
        for row_idx, row in enumerate(data[1:]):
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))

        # Применяем фильтр после загрузки
        self.apply_filter()

    def apply_filter(self):
        """Применяем поиск и фильтрацию для отображения нужных строк"""
        show_untranslated = self.show_untranslated_checkbox.isChecked()
        search_text = self.search_line_edit.text().lower()
        file_type_search_text = self.file_type_search_line_edit.text().lower()

        total_rows = self.table.rowCount()
        untranslated_count = 0
        visible_rows = 0

        for row in range(total_rows):
            item = self.table.item(row, 3)  # destination_language
            item2 = self.table.item(row, 2)  # source_language
            item3 = self.table.item(row, 1)  # file_type

            if item and item2 and item3:
                destination_language = item.text().lower()
                source_language = item2.text().lower()
                file_type = item3.text().lower()

                is_untranslated = destination_language == ""
                if is_untranslated:
                    untranslated_count += 1

                matches_filter = (
                    (search_text in destination_language or search_text in source_language) and
                    (file_type_search_text in file_type) and
                    (not show_untranslated or is_untranslated)
                )

                self.table.setRowHidden(row, not matches_filter)
                if matches_filter:
                    visible_rows += 1

        # Обновляем метку со статистикой
        translated = total_rows - untranslated_count
        percent = int(translated / total_rows * 100) if total_rows > 0 else 0
        self.stats_label.setText(
            f"Статистика: всего {total_rows} строк, {untranslated_count} не переведено ({percent}% переведено)"
        )


    def save_csv(self):
        """Сохраняем данные из таблицы обратно в CSV файл"""
        if not self.current_file:
            return

        with open(self.current_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            writer.writerow(headers)

            # Сохраняем данные построчно
            for row in range(self.table.rowCount()):
                row_data = [
                    self.table.item(row, col).text() if self.table.item(row, col) else ''
                    for col in range(self.table.columnCount())
                ]
                writer.writerow(row_data)

    def on_double_click(self, index):
        """Открывает модальное окно для редактирования строки"""
        row = index.row()
        original_text = self.table.item(row, 2).text()  # Исходный текст (source_language)
        translated_text = self.table.item(row, 3).text()  # Перевод (destination_language)

        dialog = EditDialog(original_text, translated_text, self)
        if dialog.exec_() == QDialog.Accepted:
            # Получаем новый перевод и обновляем таблицу
            new_translated_text = dialog.get_translated_text()
            self.table.item(row, 3).setText(new_translated_text)

    def on_search_text_changed(self):
        """Метод вызывается при изменении текста в строке поиска"""
        # Запускаем таймер с задержкой 300 мс после последнего ввода
        self.search_timer.start(300)

if __name__ == "__main__":
    app = QApplication([])

    # Создаем окно и запускаем приложение
    editor = CSVEditor()
    editor.show()

    app.exec_()
