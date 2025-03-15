import os
import random
import time
import uuid

import qrcode
from dotenv import load_dotenv
from square.client import Client
from square.http.auth.o_auth_2 import BearerAuthCredentials

from management.Context import Config
from printer.printer import output_dir

load_dotenv()
access_token=os.environ.get("PAYMENT_TOKEN")
location_id=os.environ.get("SQUARE_ORDER_LOCATION_ID")
print(f"TOKEN:{access_token}")
client = Client(
    bearer_auth_credentials=BearerAuthCredentials(
       access_token=access_token,
    ),
    environment='production')

class PaymentManager:
    """Payment manager that creates checkout link and qr code."""

    def __init__(self, config: Config):
        self.amount = config.PRICE
        self.uuid = str(uuid.uuid4())
        self.idempotency_key = uuid.uuid4()
        self.checkout_link = None
        self.order_id = None
        self.link_id = None
        self.create_checkout_link()
        if self.checkout_link is not None:
            self.create_qr_code()

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
                                        "amount": self.amount*100,
                                        "currency": "USD"
                                    }
                                }
                            ]
                        },
                        "checkout_options": {
                            "allow_tipping": False,
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
                    return

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
            print(result.errors)
        if os.path.exists(f"{output_dir}/qrcode.png"):
            os.remove(f"{output_dir}/qrcode.png")



    def create_qr_code(self) -> None:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.checkout_link)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="maroon", back_color="beige").convert("RGBA")
        qr_data = qr_img.getdata()
        new_data = []
        for item in qr_data:
            if item[:3] == (255, 255, 255):
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)

        qr_img.putdata(new_data)
        qr_img.save(f"{output_dir}/qrcode.png", "PNG")
