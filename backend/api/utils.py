import sqlite3
import tempfile
import time
import json
import os
from typing import Tuple, Optional, Any


FORBIDDEN_KEYWORDS = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE', 'CREATE', 'GRANT', 'REVOKE']


def validate_query(query: str) -> Tuple[bool, Optional[str]]:
    """Проверяет SQL-запрос на запрещённые операции"""
    query_upper = query.upper().strip()

    # Проверяем запрещённые ключевые слова
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in query_upper:
            return False, f"Запрещённая операция: {keyword}. Разрешены только SELECT-запросы."

    # Проверяем что запрос начинается с SELECT или WITH (для CTE)
    first_word = query_upper.split()[0] if query_upper.split() else ''
    if first_word not in ('SELECT', 'WITH', 'PRAGMA'):
        return False, "Разрешены только SELECT-запросы"

    return True, None


def execute_sql_in_sandbox(
    query: str,
    schema: str,
    tables_data: list,
    timeout_seconds: int = 3
) -> dict:
    """
    Выполняет SQL-запрос в изолированной среде (sandbox).
    
    Args:
        query: SQL-запрос пользователя
        schema: DDL для создания таблиц
        tables_data: Данные таблиц в формате [{"name": "...", "columns": [...], "sampleData": [...]}]
        timeout_seconds: Таймаут выполнения в секундах
    
    Returns:
        dict с результатом выполнения
    """
    # Валидация запроса
    is_valid, error_msg = validate_query(query)
    if not is_valid:
        return {
            'status': 'error',
            'message': error_msg
        }

    # Создаём временную БД
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.db')
    os.close(tmp_fd)

    try:
        conn = sqlite3.connect(tmp_path)
        conn.execute(f"PRAGMA busy_timeout = {timeout_seconds * 1000}")

        # Создаём схему
        try:
            conn.executescript(schema)
        except sqlite3.Error as e:
            conn.close()
            return {
                'status': 'error',
                'message': f"Ошибка создания схемы: {str(e)}"
            }

        # Загружаем тестовые данные
        try:
            for table_data in tables_data:
                table_name = table_data['name']
                columns = table_data.get('columns', [])
                sample_data = table_data.get('sampleData', [])

                if sample_data and columns:
                    col_names = [col['name'] for col in columns]
                    placeholders = ', '.join(['?' for _ in col_names])
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({placeholders})"

                    for row in sample_data:
                        values = [row.get(col['name']) for col in columns]
                        conn.execute(insert_sql, values)

            conn.commit()
        except (sqlite3.Error, KeyError) as e:
            conn.close()
            return {
                'status': 'error',
                'message': f"Ошибка загрузки данных: {str(e)}"
            }

        # Выполняем запрос с замером времени
        start_time = time.time()
        try:
            cursor = conn.execute(query)
            columns = [description[0] for description in cursor.description] if cursor.description else []
            rows = cursor.fetchmany(1000)  # Ограничение на количество строк
            execution_time = time.time() - start_time

            # Формируем результат
            result_data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                result_data.append(row_dict)

            conn.close()
            return {
                'status': 'success',
                'data': result_data,
                'execution_time': round(execution_time, 3)
            }

        except sqlite3.Error as e:
            execution_time = time.time() - start_time
            conn.close()
            return {
                'status': 'error',
                'message': str(e),
                'execution_time': round(execution_time, 3)
            }

    except Exception as e:
        return {
            'status': 'error',
            'message': f"Внутренняя ошибка: {str(e)}"
        }
    finally:
        # Удаляем временный файл
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def compare_results(user_result: list, expected_result: list) -> bool:
    """
    Сравнивает результат пользователя с эталонным.
    
    Правила сравнения:
    - Количество строк должно совпадать
    - Порядок строк не важен
    - Значения должны совпадать с точностью до типов данных
    """
    if len(user_result) != len(expected_result):
        return False

    if len(user_result) == 0 and len(expected_result) == 0:
        return True

    # Нормализуем значения для сравнения
    def normalize_value(val):
        if val is None:
            return None
        if isinstance(val, float):
            return round(val, 6)
        if isinstance(val, int):
            return val
        return str(val).strip().lower()

    def normalize_row(row):
        return tuple(sorted(normalize_value(v) for v in row.values()))

    # Сортируем оба набора для сравнения
    user_normalized = sorted(normalize_row(row) for row in user_result)
    expected_normalized = sorted(normalize_row(row) for row in expected_result)

    return user_normalized == expected_normalized
