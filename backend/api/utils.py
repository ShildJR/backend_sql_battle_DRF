import sqlite3
import tempfile
import os
import re
from typing import Tuple, List, Dict, Any


# Запрещённые ключевые слова (только SELECT разрешён)
FORBIDDEN_KEYWORDS = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE', 'CREATE', 'EXEC', 'GRANT', 'REVOKE']


def validate_query(query: str) -> bool:
    """Проверяет, что запрос безопасен (только SELECT)"""
    query_upper = query.upper().strip()

    # Пустой запрос
    if not query_upper:
        return False

    # Проверяем запрещённые ключевые слова
    for keyword in FORBIDDEN_KEYWORDS:
        # Используем word boundary чтобы не ловить подстроки
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, query_upper):
            return False

    return True


def execute_sql_sandbox(
    query: str,
    schema: str,
    tables_data: List[Dict[str, Any]]
) -> Tuple[bool, Any]:
    """
    Выполняет SQL-запрос в изолированной среде (sandbox).

    Args:
        query: SQL-запрос пользователя
        schema: DDL для создания таблиц
        tables_data: Данные таблиц с примерами

    Returns:
        Tuple[bool, Any]: (успех, результат или сообщение об ошибке)
        Если успех=True: результат — список словарей
        Если успех=False: результат — строка с ошибкой
    """
    tmp_file = None
    conn = None

    try:
        # Создаём временную БД
        tmp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        tmp_file.close()

        conn = sqlite3.connect(tmp_file.name)
        conn.row_factory = sqlite3.Row

        # Создаём схему
        try:
            conn.executescript(schema)
        except sqlite3.Error as e:
            return False, f"Ошибка создания схемы: {str(e)}"

        # Загружаем тестовые данные
        for table_info in tables_data:
            table_name = table_info.get('name', '')
            columns = table_info.get('columns', [])
            sample_data = table_info.get('sampleData', [])

            if not table_name or not columns:
                continue

            col_names = [col['name'] for col in columns]

            for row in sample_data:
                values = []
                placeholders = []
                for col_name in col_names:
                    val = row.get(col_name)
                    values.append(val)
                    placeholders.append('?')

                try:
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({', '.join(placeholders)})"
                    conn.execute(insert_sql, values)
                except sqlite3.Error as e:
                    return False, f"Ошибка загрузки данных в {table_name}: {str(e)}"

        conn.commit()

        # Выполняем запрос пользователя с таймаутом
        conn.execute("PRAGMA busy_timeout = 3000")  # 3 секунды

        try:
            cursor = conn.execute(query)
            rows = cursor.fetchall()

            # Преобразуем в список словарей
            if rows:
                col_names = [description[0] for description in cursor.description]
                result = []
                for row in rows:
                    row_dict = {}
                    for i, col_name in enumerate(col_names):
                        row_dict[col_name] = row[i]
                    result.append(row_dict)
            else:
                result = []

            return True, result

        except sqlite3.Error as e:
            return False, f"ERROR: {str(e)}"

    except Exception as e:
        return False, f"Внутренняя ошибка: {str(e)}"

    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        if tmp_file and os.path.exists(tmp_file.name):
            try:
                os.unlink(tmp_file.name)
            except Exception:
                pass


def compare_results(user_result: List[Dict], expected_result: List[Dict]) -> bool:
    """
    Сравнивает результат пользователя с эталонным.
    Устойчива к типам данных (float vs int), порядку строк и JSON-строкам.
    """
    import json
    
    # Страховка: если данные пришли как JSON-строка, парсим их
    if isinstance(user_result, str):
        try:
            user_result = json.loads(user_result)
        except json.JSONDecodeError:
            return False
    if isinstance(expected_result, str):
        try:
            expected_result = json.loads(expected_result)
        except json.JSONDecodeError:
            return False

    # Базовые проверки
    if not isinstance(user_result, list) or not isinstance(expected_result, list):
        return False
    if len(user_result) != len(expected_result):
        return False
    if len(user_result) == 0:
        return True

    # Нормализация одной строки (словаря)
    def normalize_row(row):
        normalized = {}
        for k, v in row.items():
            if v is None:
                normalized[k] = None
            elif isinstance(v, float):
                normalized[k] = round(v, 4)  # Округляем float
            elif isinstance(v, str):
                normalized[k] = v.strip().lower()  # Нормализуем строки
            else:
                normalized[k] = v
        return tuple(sorted(normalized.items()))

    # Сортируем строки и сравниваем
    user_sorted = sorted([normalize_row(row) for row in user_result])
    expected_sorted = sorted([normalize_row(row) for row in expected_result])

    return user_sorted == expected_sorted
