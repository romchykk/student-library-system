import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from database.schema import init_db
from services.logger import log
from services.config import LIBRARY_NAME
from gui.login_dialog import LoginDialog
from gui.main_window import _open_window

def main():
    log.info(f"=== Запуск системи '{LIBRARY_NAME}' ===")
    init_db()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setFont(QFont('Segoe UI', 10))

    login = LoginDialog()
    if login.exec_() == LoginDialog.Accepted:
        _open_window(login.role, login.display_name, login  .username, login.staff_id)
    else:
        sys.exit(0)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
