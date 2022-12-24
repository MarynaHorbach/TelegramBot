# сообщает нам на каком образе будет построен наш образ
FROM python:3
# задаем рабочую директорию
WORKDIR /app
# копирует файл зависимостей в наш образ
COPY /requirements.txt /app/requirements.txt
# запускаем команду которая установит все зависимости для нашего проекта
RUN apt update
RUN apt-get install -y libsndfile1
RUN apt install -y ffmpeg
RUN pip install -r requirements.txt

# копируем все остальные файлы нашего приложения в рабочую директорию
COPY . /app
# заупскаем наше приложение
CMD ["python", "bot.py"]
