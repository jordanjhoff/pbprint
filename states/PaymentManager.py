import os
import random
import time
import uuid

from dotenv import load_dotenv
from square.client import Client
from square.http.auth.o_auth_2 import BearerAuthCredentials

load_dotenv()
access_token=os.environ.get("PAYMENT_TOKEN")
location_id=os.environ.get("SQUARE_ORDER_LOCATION_ID")
print(f"TOKEN:{access_token}")
client = Client(
    bearer_auth_credentials=BearerAuthCredentials(
       access_token=access_token,
    ),
    environment='sandbox')

class PaymentManager:
    def __init__(self, amount: int = 5, currency: str = "USD"):
        self.amount = amount
        self.currency = currency
        self.uuid = str(uuid.uuid4())
        self.idempotency_key = uuid.uuid4()
        self.checkout_link = None
        self.order_id = None
        self.link_id = None
        self.create_checkout_link()

    def create_checkout_link(self) -> None:
        """
        Generate a Square checkout link with retry logic.
        """
        retries_per_method_call = 3
        delay = 2

        for attempt in range(retries_per_method_call):
            try:
                result = client.checkout.create_payment_link(
                    body={
                        "idempotency_key": self.uuid,
                        "description": "2 x Photo Strip",
                        "order": {
                            "location_id": location_id,
                            "line_items": [
                                {
                                    "name": "Photobooth",
                                    "quantity": "1",
                                    "base_price_money": {
                                        "amount": 500,
                                        "currency": "USD"
                                    }
                                }
                            ]
                        },
                        "checkout_options": {
                            "allow_tipping": True,
                            "merchant_support_email": "forty1bear@gmail.com",
                            "ask_for_shipping_address": False,
                            "accepted_payment_methods": {
                                "apple_pay": True,
                                "google_pay": True,
                                "cash_app_pay": True,
                                "afterpay_clearpay": False
                            }
                        }
                    }
                )

                if result.is_success():
                    print(result.body['payment_link']['long_url'])
                    self.checkout_link = result.body['payment_link']['long_url']
                    self.order_id = result.body['payment_link']['order_id']
                    self.link_id = result.body['payment_link']['id']
                    return  # Exit the function since it succeeded

                else:
                    print(f"Failed to create link: {result.body}")

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")

            time.sleep(delay + random.uniform(0, 1))
            delay *= 2
        print("Unable to create checkout link")

    def check_payment_status(self) -> str:
        result = client.orders.retrieve_order(
            order_id=self.order_id
        )

        if result.is_success():
            return result.body['order']['state']
        elif result.is_error():
            print(result.errors)
            raise Exception(result.errors)


    def clean_payment_manager(self) -> None:
        result = client.checkout.delete_payment_link(
            id=self.link_id
        )

        if result.is_success():
            print(result.body)
        elif result.is_error():
            raise Exception(result.errors)


if __name__ == '__main__':
    pm = PaymentManager()
    pm.clean_payment_manager()