import os
import csv

# ТРЕБОВАНИЕ 3 & 6: Наследование + Статический метод
class BaseDataManager:
    # 6. Статический метод (вызывается без создания экземпляра класса)
    @staticmethod
    def count_files(path):
        count = 0
        for item in os.listdir(path):
            if os.path.isfile(os.path.join(path, item)):
                count += 1
        return count

# Основной класс коллекции пациентов
class PatientCollection(BaseDataManager):
    def __init__(self, filename):
        # Инициализация через __setattr__ (автоматически вызовет наш переопределённый метод)
        self._filename = filename
        self._records = []
        self._load_or_create()

    # 4. Запись значений в свойства только через __setattr__
    def __setattr__(self, name, value):
        # Разрешаем менять только внутренние поля (начинающиеся с '_')
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            raise AttributeError(f"Прямое изменение свойства '{name}' запрещено. Используйте методы класса.")

    def _load_or_create(self):
        if os.path.exists(self._filename):
            with open(self._filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['Number'] = int(row['Number'])
                    row['Duration'] = int(row['Duration'])
                    self._records.append(row)
        else:
            # Создаём демо-файл с русскими именами
            with open(self._filename, 'w', encoding='utf-8') as f:
                f.write("Number,Patient Name,Doctor Name,Reason,Duration\n")
                f.write("1,Иванов Иван,Петрова Анна,Грипп,15\n")
                f.write("2,Петрова Мария,Сидоров Владимир,Перелом,30\n")
                f.write("3,Сидоров Алексей,Иванова Елена,Кашель,10\n")
                f.write("4,Козлова Ольга,Петрова Анна,Давление,20\n")
                f.write("5,Михайлов Сергей,Сидоров Владимир,Головная боль,25\n")
                f.write("6,Новикова Татьяна,Иванова Елена,Тонзиллит,40\n")
                f.write("7,Соколов Дмитрий,Петрова Анна,Грипп,15\n")
            self._load_or_create()

    # 5. Доступ к элементам коллекции по индексу
    def __getitem__(self, index):
        return self._records[index]

    # 1. Итератор
    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index < len(self._records):
            record = self._records[self._iter_index]
            self._iter_index += 1
            return record
        raise StopIteration

    # 2. Перегрузка стандартных операций (repr)
    def __repr__(self):
        return f"PatientCollection(file='{self._filename}', records={len(self._records)})"

    # 7. Генератор: фильтрация по длительности
    def filter_by_duration(self, min_val):
        for rec in self._records:
            if rec['Duration'] > min_val:
                yield rec

    # 7. Генератор: сортировка по полю
    def sorted_by_field(self, field_name):
        for rec in sorted(self._records, key=lambda x: x[field_name]):
            yield rec

    # Сохранение данных обратно в файл
    def save_to_csv(self):
        fieldnames = ['Number', 'Patient Name', 'Doctor Name', 'Reason', 'Duration']
        with open(self._filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self._records)
        print(f"✅ Данные сохранены в '{self._filename}'")

    # Вывод таблицы на экран
    def print_table(self, title, records=None):
        print(f"\n{title}")
        print("-" * 70)
        data = records if records else self._records
        for r in data:
            print(f"{r['Number']:<3} {r['Patient Name']:<20} {r['Doctor Name']:<20} {r['Reason']:<15} {r['Duration']}")
        print(f"Всего: {len(data)}")


# 3. Наследование: Расширенная версия коллекции
class ExtendedPatientCollection(PatientCollection):
    def __init__(self, filename):
        super().__init__(filename)

    # 7. Ещё один генератор в дочернем классе
    def find_by_doctor(self, doctor_name):
        for rec in self._records:
            if rec['Doctor Name'] == doctor_name:
                yield rec


# ================= ОСНОВНАЯ ПРОГРАММА =================
if __name__ == "__main__":
    # 1. Считаем файлы в директории (статический метод)
    print("1. Подсчёт файлов в текущей папке")
    file_count = PatientCollection.count_files(".")
    print(f"📁 Файлов найдено: {file_count}")

    print("\n2. Работа с коллекцией пациентов")
    # Создаём объект (дочерний класс наследует все методы родителя)
    db = ExtendedPatientCollection('data.csv')
    print(f"Объект создан: {repr(db)}")  # Проверка __repr__

    # Проверка __getitem__ (доступ по индексу)
    print("\nЗапись по индексу [0]:", db[0]['Patient Name'])

    # Проверка итератора (__iter__, __next__)
    print("\nИтерация по коллекции:")
    for rec in db:
        print(f"  -> {rec['Patient Name']} ({rec['Duration']} мин)")

    # 2.1 Сортировка (через генератор)
    print_table_data = lambda title, gen: (db.print_table(title, list(gen)))
    print_table_data("Сортировка по ФИО пациента:", db.sorted_by_field('Patient Name'))

    # 2.2 Сортировка по числу (через генератор)
    print_table_data("Сортировка по длительности:", db.sorted_by_field('Duration'))

    # 2.3 Фильтрация (через генератор)
    print_table_data("Посещения дольше 20 минут:", db.filter_by_duration(20))

    # Демонстрация генератора из дочернего класса
    print_table_data("Пациенты врача 'Петрова Анна':", db.find_by_doctor('Петрова Анна'))

    # 3. Добавление записи и сохранение
    print("\n3. Добавление новой записи и сохранение")
    new_visit = {
        'Number': 8,
        'Patient Name': 'Кузнецова Анна',
        'Doctor Name': 'Сидоров Владимир',
        'Reason': 'Аллергия',
        'Duration': 18
    }
    db._records.append(new_visit)  # Добавляем во внутренний список
    db.save_to_csv()               # Сохраняем в файл