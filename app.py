import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QColorDialog,
    QMenu, QStatusBar, QVBoxLayout, QWidget, QTabWidget, QInputDialog,
    QHBoxLayout, QPushButton, QTabBar
)
from PyQt5.QtGui import QColor, QKeySequence, QTextCharFormat
from PyQt5.QtCore import Qt, QDateTime, QSize

THEME_FILE = 'theme.json'

class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.new_files = set()  # Track new files
        self.initUI()
        self.loadTheme()  # Carrega o tema após a inicialização completa

    def initUI(self):
        self.setWindowTitle("Bloco de Notas")
        self.setGeometry(100, 100, 800, 600)

        # Central Widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Main Layout
        self.layout = QVBoxLayout(self.central_widget)

        # Tab Widget for multiple documents
        self.tab_widget = QTabWidget(self)
        self.layout.addWidget(self.tab_widget)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.closeTab)

        # Add initial tab
        self.addNewTab()

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Menu Bar
        menubar = self.menuBar()

        # File Menu
        fileMenu = menubar.addMenu('Arquivo')
        self.createMenuAction(fileMenu, 'Novo', self.addNewTab)
        self.createMenuAction(fileMenu, 'Abrir...', self.openFile)
        self.createMenuAction(fileMenu, 'Salvar', self.saveFile, QKeySequence("Ctrl+S"))
        self.createMenuAction(fileMenu, 'Salvar Como...', self.saveFileAs, QKeySequence("Ctrl+Shift+S"))
        self.createMenuAction(fileMenu, 'Renomear', self.renameFile)
        self.createMenuAction(fileMenu, 'Sair', self.close)

        # Edit Menu
        editMenu = menubar.addMenu('Editar')
        self.createMenuAction(editMenu, 'Recortar', self.cutText)
        self.createMenuAction(editMenu, 'Copiar', self.copyText)
        self.createMenuAction(editMenu, 'Colar', self.pasteText)
        self.createMenuAction(editMenu, 'Desfazer', self.undoText)
        self.createMenuAction(editMenu, 'Refazer', self.redoText)

        # Format Menu
        formatMenu = menubar.addMenu('Formatar')
        self.createMenuAction(formatMenu, 'Aumentar Tamanho da Fonte', lambda: self.changeFontSize(14))
        self.createMenuAction(formatMenu, 'Diminuir Tamanho da Fonte', lambda: self.changeFontSize(10))
        self.createMenuAction(formatMenu, 'Substituir...', self.replaceWord)
        self.createMenuAction(formatMenu, 'Procurar...', self.findWord)

        # View Menu
        viewMenu = menubar.addMenu('Exibir')
        self.createMenuAction(viewMenu, 'Alternar Barra de Status', self.toggleStatusBar)

        # Options Menu
        optionsMenu = menubar.addMenu('Opções')
        themeMenu = QMenu('Tema', self)
        self.createMenuAction(themeMenu, 'Tema Branco', lambda: self.updateTheme('white'))
        self.createMenuAction(themeMenu, 'Tema Escuro', lambda: self.updateTheme('dark'))
        self.createMenuAction(themeMenu, 'Tema Azul', lambda: self.updateTheme('blue'))
        self.createMenuAction(themeMenu, 'Tema Verde', lambda: self.updateTheme('green'))
        self.createMenuAction(themeMenu, 'Carregar Tema', self.loadTheme)
        optionsMenu.addMenu(themeMenu)
        self.createMenuAction(optionsMenu, 'Alterar Cor da Borda', self.changeBorderColor)
        self.createMenuAction(optionsMenu, 'Alterar Cor de Fundo', self.changeBgColor)
        self.createMenuAction(optionsMenu, 'Alterar Cor do Texto', self.changeTextColor)

        # Set default theme
        self.loadTheme()  # Carrega o tema inicial

        # Set effects for tabs
        self.setTabEffects()

        # Connect F5 to insert date and time
        self.createMenuAction(optionsMenu, 'Inserir Data e Hora', self.insertDateTime, QKeySequence("F5"))

        self.show()

    def createMenuAction(self, menu, text, callback, shortcut=None):
        action = QAction(text, self)
        action.triggered.connect(callback)
        if shortcut:
            action.setShortcut(shortcut)
        menu.addAction(action)

    def addNewTab(self):
        tab = QTextEdit()
        index = self.tab_widget.addTab(tab, "Nova Guia")
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentWidget().filename = None
        self.new_files.add(tab)
        self.setTabCloseButton(index)

    def setTabCloseButton(self, index):
        tab_bar = self.tab_widget.tabBar()
        close_button = QPushButton('x', self)
        close_button.setFixedSize(QSize(16, 16))
        close_button.clicked.connect(lambda: self.tab_widget.tabCloseRequested.emit(index))
        tab_bar.setTabButton(index, QTabBar.RightSide, close_button)

    def closeTab(self, index):
        widget = self.tab_widget.widget(index)
        if widget in self.new_files:
            self.new_files.remove(widget)
        self.tab_widget.removeTab(index)

    def currentTab(self):
        return self.tab_widget.currentWidget()

    def openFile(self):
        file_path = QFileDialog.getOpenFileName(self, "Abrir Arquivo", "", "Text Files (*.txt);;All Files (*)")[0]
        if file_path:
            with open(file_path, 'r') as file:
                self.currentTab().setText(file.read())
            self.currentTab().filename = file_path
            self.new_files.discard(self.currentTab())
            self.setTabCloseButton(self.tab_widget.currentIndex())
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_path.split('/')[-1])

    def saveFile(self):
        tab = self.currentTab()
        if hasattr(tab, 'filename') and tab.filename:
            with open(tab.filename, 'w') as file:
                file.write(tab.toPlainText())
        else:
            self.saveFileAs()

    def saveFileAs(self):
        file_path = QFileDialog.getSaveFileName(self, "Salvar Arquivo Como", "", "Text Files (*.txt);;All Files (*)")[0]
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.currentTab().toPlainText())
            self.currentTab().filename = file_path
            self.new_files.discard(self.currentTab())
            self.setTabCloseButton(self.tab_widget.currentIndex())
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_path.split('/')[-1])

    def renameFile(self):
        file_path = QFileDialog.getSaveFileName(self, "Renomear Arquivo", "", "Text Files (*.txt);;All Files (*)")[0]
        if file_path:
            current_content = self.currentTab().toPlainText()
            with open(file_path, 'w') as file:
                file.write(current_content)
            self.currentTab().filename = file_path
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_path.split('/')[-1])

    def changeFontSize(self, size):
        font = self.currentTab().font()
        font.setPointSize(size)
        self.currentTab().setFont(font)

    def toggleStatusBar(self):
        if self.status_bar.isVisible():
            self.status_bar.hide()
        else:
            self.status_bar.show()

    def changeTextColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            text_color = color.name()
            self.updateThemeColors(text_color=text_color)

    def changeBgColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            bg_color = color.name()
            self.updateThemeColors(background_color=bg_color)

    def changeBorderColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            border_color = color.name()
            self.updateThemeColors(border_color=border_color)

    def updateThemeColors(self, background_color=None, text_color=None, border_color=None):
        try:
            # Carregar o tema atual
            theme = self.loadThemeFromFile()

            # Atualizar com as novas cores
            if background_color:
                theme['background_color'] = background_color
            if text_color:
                theme['text_color'] = text_color
            if border_color:
                theme['border_color'] = border_color

            # Salvar as alterações no arquivo
            with open(THEME_FILE, 'w') as f:
                json.dump(theme, f, indent=4)

            # Aplicar o tema atualizado
            self.applyTheme(theme)
        except Exception as e:
            print(f"Erro ao atualizar cores do tema: {e}")

    def applyTheme(self, theme):
        background_color = theme.get('background_color', 'black')
        text_color = theme.get('text_color', 'white')
        border_color = theme.get('border_color', 'white')
        tab_bg_color = theme.get('tab_bg_color', '#333')

        self.central_widget.setStyleSheet(f"""
            background-color: {background_color};
            color: {text_color};
        """)

        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {border_color};  /* Adiciona a borda */
            }}
            QTabBar::tab {{
                background: {tab_bg_color};
                color: {text_color};
                padding: 10px;
                border: 1px solid {border_color};  /* Adiciona a borda às abas */
            }}
            QTabBar::tab:selected {{
                background: {background_color};
                color: {text_color};
            }}
        """)

        self.status_bar.setStyleSheet(f"""
            background-color: {background_color};
            color: {text_color};
        """)

    def loadTheme(self):
        theme = self.loadThemeFromFile()
        self.applyTheme(theme)

    def loadThemeFromFile(self):
        try:
            with open(THEME_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar o arquivo de tema: {e}")
            return {}

    def updateTheme(self, theme_name):
        themes = {
            'white': {'background_color': 'white', 'text_color': 'black', 'border_color': 'gray', 'tab_bg_color': 'lightgray'},
            'dark': {'background_color': 'black', 'text_color': 'white', 'border_color': 'white', 'tab_bg_color': '#333'},
            'blue': {'background_color': '#001f3f', 'text_color': 'white', 'border_color': 'white', 'tab_bg_color': '#0074D9'},
            'green': {'background_color': '#2E8B57', 'text_color': 'white', 'border_color': 'white', 'tab_bg_color': '#3CB371'}
        }
        if theme_name in themes:
            theme = themes[theme_name]
            with open(THEME_FILE, 'w') as f:
                json.dump(theme, f, indent=4)
            self.applyTheme(theme)
        else:
            print("Tema não encontrado.")

    def setTabEffects(self):
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                background: #2e2e2e;
                color: white;
                padding: 10px;
            }
            QTabBar::tab:selected {
                background: #1e1e1e;
                color: white;
            }
        """)

    def replaceWord(self):
        old_word, ok = QInputDialog.getText(self, 'Substituir Palavra', 'Palavra a ser substituída:')
        if ok and old_word:
            new_word, ok = QInputDialog.getText(self, 'Nova Palavra', 'Nova palavra:')
            if ok and new_word:
                text = self.currentTab().toPlainText()
                new_text = text.replace(old_word, new_word)
                self.currentTab().setText(new_text)

    def findWord(self):
        word, ok = QInputDialog.getText(self, 'Procurar Palavra', 'Palavra a ser procurada:')
        if ok and word:
            text = self.currentTab().toPlainText()
            cursor = self.currentTab().textCursor()
            cursor.setPosition(0)
            self.currentTab().setTextCursor(cursor)
            if text.find(word) == -1:
                print("Palavra não encontrada.")
            else:
                while text.find(word, cursor.position()) != -1:
                    cursor = self.currentTab().textCursor()
                    cursor.beginEditBlock()
                    cursor.movePosition(cursor.Start)
                    cursor = self.currentTab().document().find(word, cursor)
                    if cursor.isNull():
                        break
                    cursor.movePosition(cursor.EndOfWord, cursor.KeepAnchor)
                    cursor.mergeCharFormat(QTextCharFormat())
                    cursor.endEditBlock()
                    self.currentTab().setTextCursor(cursor)

    def cutText(self):
        self.currentTab().cut()

    def copyText(self):
        self.currentTab().copy()

    def pasteText(self):
        self.currentTab().paste()

    def undoText(self):
        self.currentTab().undo()

    def redoText(self):
        self.currentTab().redo()

    def insertDateTime(self):
        current_datetime = QDateTime.currentDateTime().toString()
        self.currentTab().insertPlainText(current_datetime)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    notepad = Notepad()
    sys.exit(app.exec_())
