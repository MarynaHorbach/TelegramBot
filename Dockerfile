# сообщает нам на каком образе будет построен наш образ
FROM python:3.10.6
# задаем рабочую директорию
WORKDIR /app
# копирует файл зависимостей в наш образ
COPY /requirements.txt /app/requirements.txt
# запускаем команду которая установит все зависимости для нашего проекта
RUN pip install -r /app/requirements.txt
RUN apt-get -y update
RUN apt-get install -y libsndfile1
# копируем все остальные файлы нашего приложения в рабочую директорию
COPY . /app
# заупскаем наше приложение
CMD ["python", "bot.py"]
