# 📊 SMT

### StockMarketToropov - это реализация торговой платформы с поддержкой лимитных/рыночных ордеров, портфелем пользователя и историей сделок.

---

## 🚀 Quick Start

1. В корне проекта создаем .env файл и заполняем его далее по списку:

* `POSTGRESQL_HOST` - Хост бд
* `POSTGRESQL_PORT` - Порт бд
* `POSTGRESQL_USER` - Имя пользователя в бд
* `POSTGRESQL_PASS` - Пароль от пользователя
* `POSTGRESQL_NAME` - Название бд
* `POSTGRESQL_ECHO` - Режим отладки бд True/False. По умолчанию False
* `SECRET_KEY` - Секретный ключ, используемый для подписи JWT

2. Устанавливаем python 3.13, docker, docker-compose
3. Собираем образ (через терминал):
`docker-compose build`
4. Запускаем в фоновом режиме:
`docker-compose up -d`
