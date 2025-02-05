import asyncio
import logging
from market_data import get_market_data
from analysis import analyze_market
from trading_ai_system.trading_system import TradingSystem

# Configurar logging
logging.basicConfig(
    filename='assistant.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def analyze_and_trade(symbol: str):
    """
    Obtiene datos, analiza el mercado y ejecuta órdenes según la señal.
    """
    market_data = get_market_data(symbol, "1min")
    if not market_data.empty:
        analysis = analyze_market(market_data, symbol)
        if analysis and analysis.get('confidence', 0) > 0.7:
            execute_order(analysis)

async def run_assistant():
    """
    Ejecuta de forma asíncrona el análisis y la ejecución de órdenes en intervalos regulares.
    """
    symbol = "BTC/USD"
    while True:
        await analyze_and_trade(symbol)
        await asyncio.sleep(60)  # Ejecutar cada minuto

if __name__ == "__main__":
    asyncio.run(run_assistant())
