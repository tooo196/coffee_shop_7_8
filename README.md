# Coffee Shop

Современное веб-приложение на Django для управления онлайн-витриной кофейни, включая каталог товаров, корзину и управление заказами.

## Возможности

- **Каталог товаров**: Просмотр и управление ассортиментом кофе
- **Корзина покупок**: Добавление/удаление товаров и управление количеством
- **Аутентификация пользователей**: Безопасные учетные записи и профили
- **Адаптивный дизайн**: Корректное отображение на компьютерах и мобильных устройствах
- **Панель администратора**: Управление товарами, заказами и пользователями

## Требования

- Python 3.8 и выше
- PostgreSQL (или SQLite для разработки)
- pip (менеджер пакетов Python)

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/coffee_shop.git
   cd coffee_shop
   ```

2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   # На Windows: .\venv\Scripts\activate
   # На macOS/Linux: source venv/bin/activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

5. Примените миграции:
   ```bash
   python manage.py migrate
   ```

6. Создайте суперпользователя (опционально):
   ```bash
   python manage.py createsuperuser
   ```

7. Запустите сервер разработки:
   ```bash
   python manage.py runserver
   ```

## Запуск с помощью Docker

1. Убедитесь, что у вас установлены Docker и Docker Compose
2. Выполните:
   ```bash
   docker-compose up --build
   ```
3. Приложение будет доступно по адресу `http://localhost:8000`

## Структура проекта

```
coffee_shop/
├── apps/               # Приложения Django
├── coffee_shop/        # Настройки и конфигурации проекта
├── templates/          # HTML-шаблоны
├── static/             # Статические файлы (CSS, JS, изображения)
├── media/              # Загружаемые пользователями файлы
├── .env                # Переменные окружения
├── .gitignore          # Файл для исключения файлов из Git
├── docker-compose.yml  # Конфигурация Docker Compose
├── Dockerfile          # Конфигурация Docker
├── manage.py           # Скрипт управления Django
└── requirements.txt    # Зависимости Python
```

## Внесение изменений

1. Сделайте форк репозитория
2. Создайте ветку для вашей функции (`git checkout -b feature/НоваяФункция`)
3. Зафиксируйте изменения (`git commit -m 'Добавлена новая функция'`)
4. Отправьте изменения в репозиторий (`git push origin feature/НоваяФункция`)
5. Создайте Pull Request

## Лицензия

Этот проект распространяется под лицензией MIT - подробности см. в файле [LICENSE](LICENSE).

## Контакты

Ваше Имя - ваш.email@example.com

Ссылка на проект: [https://github.com/tooo196/coffee_shop](https://github.com/tooo196/coffee_shop)
