import psycopg2

def check_postgres():
	"""
	Проверяет подключение к PostgreSQL и наличие базы данных coffee_shop
	"""
	print("🔍 Проверка подключения к PostgreSQL...")

	# Сначала проверяем подключение как superuser (postgres)
	try:
		conn = psycopg2.connect(
			host="localhost",
			port=5434,
			database="postgres",  # Подключаемся к системной базе
			user="postgres",
			password="postgres"
		)
		print("✅ Подключение к PostgreSQL как 'postgres' успешно")

		cursor = conn.cursor()

		# Проверяем какие базы данных существуют
		cursor.execute("SELECT datname FROM pg_database ORDER BY datname;")
		databases = cursor.fetchall()

		print("\n📁 Список всех баз данных на сервере:")
		coffee_shop_exists = False
		for db in databases:
			db_name = db[0]
			if db_name == "coffee_shop":
				print(f"  ✅ {db_name} (наша база)")
				coffee_shop_exists = True
			else:
				print(f"  • {db_name}")

		if not coffee_shop_exists:
			print("\n❌ База данных 'coffee_shop' не найдена!")
			print("Создайте её командой:")
			print("CREATE DATABASE coffee_shop;")
		else:
			print("\n✅ База данных 'coffee_shop' существует!")

			# Проверяем пользователя coffee_user
			cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'coffee_user';")
			if cursor.fetchone():
				print("✅ Пользователь 'coffee_user' существует")
			else:
				print("❌ Пользователь 'coffee_user' не найден")

		cursor.close()
		conn.close()

	except Exception as e:
		print(f"❌ Ошибка подключения к PostgreSQL: {e}")
		print("\nВозможные причины:")
		print("1. PostgreSQL не запущен")
		print("2. Неправильный порт (попробуйте 5432 или 5434)")
		print("3. Неправильный пароль для пользователя 'postgres'")
		return

	# Теперь проверяем подключение к конкретной базе coffee_shop
	print("\n🔍 Проверка подключения к базе 'coffee_shop'...")
	try:
		conn = psycopg2.connect(
			host="localhost",
			port=5434,
			database="coffee_shop",  # Пытаемся подключиться к нашей базе
			user="coffee_user",
			password="coffee_password"
		)
		print("✅ Успешное подключение к базе 'coffee_shop'!")

		cursor = conn.cursor()
		cursor.execute("SELECT current_database(), current_user;")
		db_name, username = cursor.fetchone()
		print(f"   Текущая база: {db_name}")
		print(f"   Текущий пользователь: {username}")

		cursor.close()
		conn.close()

	except psycopg2.OperationalError as e:
		print(f"❌ Не удалось подключиться к 'coffee_shop': {e}")
		print("\nВозможные решения:")
		print("1. Создайте базу данных: CREATE DATABASE coffee_shop;")
		print("2. Создайте пользователя: CREATE USER coffee_user WITH PASSWORD 'coffee_password';")
		print("3. Дайте права: GRANT ALL PRIVILEGES ON DATABASE coffee_shop TO coffee_user;")

if __name__ == "__main__":
	check_postgres()