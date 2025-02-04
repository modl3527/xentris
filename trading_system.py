import asyncio
import logging
from market_data import get_market_data
from analysis import analyze_market
from trading_bot import execute_order
from config import SYMBOL

# Configurar logging
logging.basicConfig(
    filename='trading_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def analyze_and_trade():
    """
    Obtiene datos de mercado, analiza y ejecuta órdenes en función de la IA.
    """
    market_data = get_market_data(SYMBOL, "1min")
    if not market_data.empty:
        analysis = analyze_market(market_data, SYMBOL)
        if analysis and analysis.get('confidence', 0) > 0.7:
            execute_order(analysis)

async def run_trading_system():
    """
    Ejecuta de forma asíncrona el sistema de trading.
    """
    while True:
        await analyze_and_trade()
        await asyncio.sleep(60)  # Ejecutar cada minuto

if __name__ == "__main__":
    asyncio.run(run_trading_system())
