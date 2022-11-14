import alpaca_trade_api as tradeapi

APCA_API_BASE_URL= "https://paper-api.alpaca.markets"
APCA_API_KEY_ID= "XXXXXXXXXXXXXXXXXXXX"
APCA_API_SECRET_KEY= "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit

api = tradeapi.REST(
    base_url=APCA_API_BASE_URL,
    key_id=APCA_API_KEY_ID,
    secret_key=APCA_API_SECRET_KEY
)
