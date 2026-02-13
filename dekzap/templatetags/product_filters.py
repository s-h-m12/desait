from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='calculate_price')
def calculate_price(product):
    # Проверяем наличие и значение скидки
    if not hasattr(product, 'sale') or not product.sale or product.sale <= 0:
        return mark_safe(f'''
            <div class="product-price">
                <span class="price-normal">{product.price} ₽</span>
            </div>
        ''')

    try:
        price = float(product.price)
        sale_percent = int(product.sale)
        # Рассчитываем цену со скидкой
        new_price = price - (price * sale_percent / 100)
        new_price = round(new_price, 2)

        price_container_class = "product-price"
        price_container_style = ""
        # Особая стилизация для скидок больше 15%
        if sale_percent > 15:
            price_container_class = "product-price discount-high"
            price_container_style = "style='background-color: #2E8B57; padding: 8px; border-radius: 6px;'"

        html = f'''
        <div class="{price_container_class}" {price_container_style}>
            <div class="d-flex align-items-center">
                <span class="price-old">{price} ₽</span>
                <span class="price-new">{new_price} ₽</span>
            </div>
            <div class="sale-badge">-{sale_percent}%</div>
        </div>
        '''

        return mark_safe(html)
    # Обрабатываем ошибки преобразования типов
    except (ValueError, TypeError, AttributeError):
        return mark_safe(f'''
            <div class="product-price">
                <span class="price-normal">{product.price} ₽</span>
            </div>
        ''')