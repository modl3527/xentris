import MetaTrader5 as mt5
import logging
from config import SYMBOL, BASE_VOLUME

# Configurar logging
logging.basicConfig(
    filename='trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def initialize_mt5():
    """
    Inicializa la conexión con MetaTrader 5.
    """
    if not mt5.initialize():
        logging.error("MT5 initialization failed")
        return False

    authorized = mt5.login(
        login=int(os.getenv("MT5_LOGIN")),
        password=os.getenv("MT5_PASSWORD"),
        server=os.getenv("MT5_SERVER")
    )

    if not authorized:
        logging.error(f"MT5 login failed: {mt5.last_error()}")
        return False

    logging.info("MT5 initialized and logged in successfully")
    return True

def execute_order(analysis):
    """
    Ejecuta una orden en MT5 según la recomendación de la IA.
    """
    if not initialize_mt5():
        return

    order_type = mt5.ORDER_TYPE_BUY if analysis["recommendation"] == "COMPRAR" else mt5.ORDER_TYPE_SELL

    tick = mt5.symbol_info_tick(SYMBOL)
    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": BASE_VOLUME,
        "type": order_type,
        "price": price,
        "sl": analysis["suggested_sl"],
        "tp": analysis["suggested_tp"],
        "deviation": 20,
        "magic": 234000,
        "comment": "Orden generada por IA local",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logging.error(f"Error al enviar la orden: {result.comment}")
    else:
        logging.info(f"Orden ejecutada correctamente, ticket: {result.order}")

