import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_product(name, description=None):
    """Создаёт продукт в Stripe и возвращает его id"""
    product = stripe.Product.create(
        name=name,
        description=description,
    )
    return product.id

def create_stripe_price(product_id, amount, currency='rub'):
    """
    Создаёт цену в Stripe.
    amount — сумма в копейках (целое число).
    """
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount,
        currency=currency,
    )
    return price.id

def create_stripe_checkout_session(price_id, success_url, cancel_url):
    """Создаёт сессию оплаты и возвращает session.id и session.url"""
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.id, session.url

def retrieve_stripe_session(session_id):
    """Получает статус сессии по её id"""
    session = stripe.checkout.Session.retrieve(session_id)
    return {
        'id': session.id,
        'payment_status': session.payment_status,
        'url': session.url,
        'amount_total': session.amount_total,
    }
