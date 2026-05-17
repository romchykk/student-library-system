"""
Матриця прав доступу для кожної ролі.

admin      — повний доступ до всього
librarian  — управління читачами, документами, видачами та поверненнями
             НЕ може: керувати обліковими записами системи
student    — тільки перегляд каталогу + подача запиту на книгу
"""

ROLES = {
    "admin": {
        "display":      "Адміністратор",
        "icon":         "👑",
        # Читачі
        "user_add":     True,
        "user_edit":    True,
        "user_delete":  True,
        "user_view":    True,
        # Документи
        "doc_add":      True,
        "doc_edit":     True,
        "doc_delete":   True,
        "doc_view":     True,
        # Видачі
        "issue":        True,
        "return_doc":   True,
        "undo":         True,
        # Пошук
        "search":       True,
        # Каталог
        "catalog":      True,
    },
    "librarian": {
        "display":      "Бібліотекар",
        "icon":         "📚",
        # Читачі
        "user_add":     True,
        "user_edit":    True,
        "user_delete":  False,   # не може видаляти читачів
        "user_view":    True,
        # Документи
        "doc_add":      True,
        "doc_edit":     True,
        "doc_delete":   False,   # не може видаляти документи
        "doc_view":     True,
        # Видачі
        "issue":        True,    # може видавати
        "return_doc":   True,    # може приймати повернення
        "undo":         False,   # не може скасовувати
        # Пошук
        "search":       True,
        # Каталог
        "catalog":      True,
    },
    "student": {
        "display":      "Студент",
        "icon":         "🎓",
        # Читачі — немає доступу
        "user_add":     False,
        "user_edit":    False,
        "user_delete":  False,
        "user_view":    False,
        # Документи — тільки перегляд
        "doc_add":      False,
        "doc_edit":     False,
        "doc_delete":   False,
        "doc_view":     True,
        # Видачі — немає доступу
        "issue":        False,
        "return_doc":   False,
        "undo":         False,
        # Пошук
        "search":       True,
        # Каталог
        "catalog":      True,
    },
}


def can(role: str, permission: str) -> bool:
    """Перевірити чи має роль певний дозвіл."""
    return ROLES.get(role, {}).get(permission, False)


def get_display(role: str) -> str:
    return ROLES.get(role, {}).get("display", role)


def get_icon(role: str) -> str:
    return ROLES.get(role, {}).get("icon", "")
