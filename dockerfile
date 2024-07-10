# Використовуємо офіційний образ Python як базовий
FROM python:3.12.1

# Встановлюємо pipenv
RUN pip install pipenv

# Вказуємо робочу директорію
WORKDIR /app

# Копіюємо Pipfile і Pipfile.lock до робочої директорії
COPY Pipfile Pipfile.lock ./

# Встановлюємо залежності
RUN pipenv install --deploy --ignore-pipfile

# Копіюємо всі файли проекту до контейнера
COPY . .

# Вказуємо команду для запуску програми
CMD ["ENTRYPOINT", "CMD"]
