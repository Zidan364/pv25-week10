from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QTabWidget, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt
import sys, sqlite3, csv

class BookManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Buku")
        self.setGeometry(300, 100, 700, 500)

        self.conn = sqlite3.connect("books.db")
        self.c = self.conn.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS books (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          title TEXT,
                          author TEXT,
                          year INTEGER)""")
        self.conn.commit()

        self.create_menu_bar()

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        # Perbaikan di sini:
        central_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.tab = QTabWidget()
        self.tab.setFixedWidth(600)
        self.setup_tabs()
        central_layout.addWidget(self.tab)

        self.setCentralWidget(central_widget)
        self.loadData()

    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        simpan_action = file_menu.addAction("Simpan")
        simpan_action.triggered.connect(self.addData)

        ekspor_action = file_menu.addAction("Ekspor ke CSV")
        ekspor_action.triggered.connect(self.exportCSV)

        keluar_action = file_menu.addAction("Keluar")
        keluar_action.triggered.connect(QApplication.quit)

        edit_menu = menubar.addMenu("Edit")
        cari_action = edit_menu.addAction("Cari Judul")
        cari_action.triggered.connect(self.focus_search)

        hapus_action = edit_menu.addAction("Hapus Data")
        hapus_action.triggered.connect(self.deleteData)

        edit_menu.addSeparator()
        edit_menu.addAction("AutoFill")
        edit_menu.addAction("Start Dictation…")
        edit_menu.addAction("Emoji & Symbols")

    def focus_search(self):
        self.tab.setCurrentIndex(0)
        self.search_input.setFocus()

    def setup_tabs(self):
        self.data_tab = QWidget()
        self.tab.addTab(self.data_tab, "Data Buku")

        outer_layout = QVBoxLayout(self.data_tab)
        # Perbaikan di sini:
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QVBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Judul")
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Pengarang")
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Tahun")

        form_layout.addWidget(QLabel("Judul:"))
        form_layout.addWidget(self.title_input)
        form_layout.addWidget(QLabel("Pengarang:"))
        form_layout.addWidget(self.author_input)
        form_layout.addWidget(QLabel("Tahun:"))
        form_layout.addWidget(self.year_input)

        self.save_btn = QPushButton("Simpan")
        self.save_btn.clicked.connect(self.addData)
        form_layout.addWidget(self.save_btn)

        outer_layout.addLayout(form_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari judul…")
        self.search_input.textChanged.connect(self.searchData)
        outer_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.cellDoubleClicked.connect(self.editCell)
        outer_layout.addWidget(self.table)

        self.delete_btn = QPushButton("Hapus Data")
        self.delete_btn.setStyleSheet("background-color: orange;")
        self.delete_btn.clicked.connect(self.deleteData)
        outer_layout.addWidget(self.delete_btn)

        identitas = QLabel("Nama: Zidan Shoni Ikram    NIM: F1D022165")
        identitas.setAlignment(Qt.AlignmentFlag.AlignRight)
        outer_layout.addWidget(identitas)

        self.export_tab = QWidget()
        self.tab.addTab(self.export_tab, "Ekspor")

        export_layout = QVBoxLayout(self.export_tab)
        export_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.export_btn = QPushButton("Ekspor ke CSV")
        self.export_btn.clicked.connect(self.exportCSV)
        export_layout.addWidget(self.export_btn)

    def loadData(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.c.execute("SELECT * FROM books")
        for row_data in self.c.fetchall():
            row_num = self.table.rowCount()
            self.table.insertRow(row_num)
            for col, data in enumerate(row_data):
                self.table.setItem(row_num, col, QTableWidgetItem(str(data)))
        self.table.blockSignals(False)

    def addData(self):
        title = self.title_input.text()
        author = self.author_input.text()
        year = self.year_input.text()

        if title and author and year:
            self.c.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
                           (title, author, year))
            self.conn.commit()
            self.title_input.clear()
            self.author_input.clear()
            self.year_input.clear()
            self.loadData()
        else:
            QMessageBox.warning(self, "Input Error", "Semua field harus diisi!")

    def editCell(self, row, column):
        id_value = int(self.table.item(row, 0).text())
        current_title = self.table.item(row, 1).text()
        current_author = self.table.item(row, 2).text()
        current_year = self.table.item(row, 3).text()

        new_title, ok1 = QInputDialog.getText(self, "Edit Judul", "Judul:", text=current_title)
        if not ok1:
            return

        new_author, ok2 = QInputDialog.getText(self, "Edit Pengarang", "Pengarang:", text=current_author)
        if not ok2:
            return

        new_year, ok3 = QInputDialog.getText(self, "Edit Tahun", "Tahun:", text=current_year)
        if not ok3:
            return

        try:
            self.c.execute("UPDATE books SET title = ?, author = ?, year = ? WHERE id = ?",
                           (new_title, new_author, new_year, id_value))
            self.conn.commit()
            self.loadData()
            QMessageBox.information(self, "Sukses", "Data berhasil diperbarui.")
        except Exception as e:
            QMessageBox.warning(self, "Update Error", str(e))

    def deleteData(self):
        selected = self.table.currentRow()
        if selected >= 0:
            id_value = int(self.table.item(selected, 0).text())
            self.c.execute("DELETE FROM books WHERE id = ?", (id_value,))
            self.conn.commit()
            self.loadData()
        else:
            QMessageBox.information(self, "Info", "Pilih data yang ingin dihapus.")

    def searchData(self, text):
        self.table.setRowCount(0)
        self.c.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + text + '%',))
        for row_data in self.c.fetchall():
            row_num = self.table.rowCount()
            self.table.insertRow(row_num)
            for col, data in enumerate(row_data):
                self.table.setItem(row_num, col, QTableWidgetItem(str(data)))

    def exportCSV(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", "", "CSV Files (*.csv)")
        if path:
            self.c.execute("SELECT * FROM books")
            rows = self.c.fetchall()
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                writer.writerows(rows)
            QMessageBox.information(self, "Berhasil", "Data berhasil diekspor ke CSV!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = BookManager()
    win.show()
    # Perbaikan di sini:
    sys.exit(app.exec())
