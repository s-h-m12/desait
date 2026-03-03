# Импортируем необходимый модульс функцией calculate_price.
from django.test import TestCase  # Используем TestCase от Django для работы с контекстом
from .templatetags.product_filters import calculate_price

# Создаем фиктивный класс товара для изоляции тестирования функции.
# Этот класс имитирует реальный объект product, который функция получает на вход.
class MockProduct:
    def __init__(self, price, sale):
        self.price = price  # Устанавливаем цену товара
        self.sale = sale  # Устанавливаем значение скидки в процентах

# Создаем тестовый класс, наследующийся от TestCase Django,
# что позволяет нам использовать возможности фреймворка при тестировании.
class CalculatePriceFilterTests(TestCase):

    # Тест №1: Проверка расчета цены со стандартной скидкой.
    # Техническая цель: убедиться, что при скидке 10% от цены 2000,
    # функция возвращает HTML-блок с перечеркнутой старой ценой
    # и новой ценой 1800, а также бейджем скидки.
    def test_calculate_price_with_discount(self):
        # Arrange (Подготовка): создаем товар с ценой 2000 и скидкой 10%
        product = MockProduct(price=2000, sale=10)

        # Act (Действие): вызываем тестируемую функцию
        result = calculate_price(product)

        # Assert (Проверка): проверяем, что результат содержит ожидаемые элементы
        self.assertIn('price-old">2000', result)  # Старая цена должна быть перечеркнута
        self.assertIn('price-new">1800.0', result)  # Новая цена 1800.0 после скидки
        self.assertIn('sale-badge">-10%', result)  # Бейдж скидки присутствует

    # Тест №2: Проверка обработки товара без скидки.
    # Техническая цель: убедиться, что при отсутствии скидки (sale = 0 или None)
    # функция возвращает HTML-блок с обычной ценой, без элементов скидки.
    def test_calculate_price_without_discount(self):
        # Arrange (Подготовка): создаем товар без скидки (None)
        product = MockProduct(price=1500, sale=None)

        # Act (Действие): вызываем тестируемую функцию
        result = calculate_price(product)

        # Assert (Проверка): проверяем, что цена отображается как обычная
        self.assertIn('price-normal">1500', result)  # Должен быть класс обычной цены
        self.assertNotIn('price-old', result)  # Старая цена отсутствует
        self.assertNotIn('sale-badge', result)  # Бейдж скидки отсутствует

    # Тест №3: Проверка применения специального стиля для высокой скидки.
    # Техническая цель: при скидке более 15% (например, 20%) функция должна
    # добавить специальный CSS-класс и зеленый фон с отступами к контейнеру цены.
    def test_calculate_price_high_discount_style(self):
        # Arrange (Подготовка): создаем товар с высокой скидкой 20%
        product = MockProduct(price=3000, sale=20)

        # Act (Действие): вызываем тестируемую функцию
        result = calculate_price(product)

        # Assert (Проверка): проверяем наличие специального оформления
        self.assertIn('discount-high', result)  # Специальный класс для высокой скидки

        # ИСПРАВЛЕНО: ищем только цвет, без кавычек (более надежно)
        self.assertIn('background-color: #2E8B57', result)  # Зеленый фон

        self.assertIn('padding: 8px', result)  # Увеличенные отступы

    # Тест №4: Проверка обработки отрицательной скидки.
    # Техническая цель: при скидке более 15% (например, 20%) функция должна
    # добавить специальный CSS-класс и зеленый фон с отступами к контейнеру цены.
    def test_calculate_price_with_negative_discount(self):
        # Arrange (Подготовка): создаем товар с отрицательной скидкой -5%
        product = MockProduct(price=2500, sale=-5)

        # Act (Действие): вызываем тестируемую функцию
        result = calculate_price(product)

        # Assert (Проверка): убеждаемся, что скидка не применилась
        self.assertIn('price-normal">2500', result)  # Должна быть обычная цена
        self.assertNotIn('price-old', result)  # Нет перечеркнутой цены
        self.assertNotIn('sale-badge', result)  # Нет бейджа скидки
        self.assertNotIn('price-new', result)  # Нет новой цены

        # Эта проверка специально добавлена для демонстрации ошибки
        # Ожидается, что бейдж скидки отсутствует, но мы намеренно проверяем его наличие
        self.assertIn('sale-badge">-5%', result)  # Будет ошибка! Бейдж не должен присутствовать