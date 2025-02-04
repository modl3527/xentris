import os
import requests
import MetaTrader5 as mt5
import pandas as pd
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
MT5_LOGIN = int(os.getenv("MT5_LOGIN"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD")
MT5_SERVER = os.getenv("MT5_SERVER")

# Configurar logging
logging.basicConfig(
    filename='market_data.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MarketDataManager:
    def __init__(self, symbol: str, timeframe: str):
        self.symbol = symbol
        self.timeframe = timeframe

    def get_twelve_data(self) -> pd.DataFrame:
        """
        Obtiene datos de mercado en tiempo real desde la API de TwelveData.
        """
        url = "https://api.twelvedata.com/time_series"
        params = {
            "symbol": self.symbol,
            "interval": self.timeframe,
            "apikey": TWELVE_DATA_API_KEY,
            "outputsize": 100
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                logging.error(f"Error API TwelveData: {response.text}")
                return pd.DataFrame()

            data = response.json()
            if 'values' not in data:
                logging.error(f"Datos inválidos de TwelveData: {data}")
                return pd.DataFrame()

            df = pd.DataFrame(data['values'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            df.set_index('datetime', inplace=True)
            
            return df

        except Exception as e:
            logging.error(f"Error obteniendo datos de TwelveData: {e}")
            return pd.DataFrame()

    def initialize_mt5(self) -> bool:
        """
        Inicializa MetaTrader 5 y realiza el login.
        """
        if not mt5.initialize():
            logging.error("MT5 initialization failed")
            return False

        authorized = mt5.login(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
        if not authorized:
            logging.error(f"MT5 login failed: {mt5.last_error()}")
            return False

        logging.info("MT5 initialized successfully")
        return True

    def get_mt5_data(self, count: int = 100) -> pd.DataFrame:
        """
        Obtiene datos históricos desde MetaTrader 5.
        """
        if not self.initialize_mt5():
            return pd.DataFrame()

        timeframe_map = {
            "1min": mt5.TIMEFRAME_M1,
            "5min": mt5.TIMEFRAME_M5,
            "15min": mt5.TIMEFRAME_M15,
            "30min": mt5.TIMEFRAME_M30,
            "1h": mt5.TIMEFRAME_H1,
            "4h": mt5.TIMEFRAME_H4,
            "1d": mt5.TIMEFRAME_D1
        }

        if self.timeframe not in timeframe_map:
            logging.error(f"Timeframe no válido: {self.timeframe}")
            return pd.DataFrame()

        rates = mt5.copy_rates_from_pos(self.symbol, timeframe_map[self.timeframe], 0, count)

        if rates is None or len(rates) == 0:
            logging.error("No se obtuvieron datos de MT5")
            return pd.DataFrame()

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        return df

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara y enriquece los datos con indicadores técnicos básicos.
        """
        if df.empty:
            logging.error("DataFrame vacío o None")
            return df

        try:
            df['SMA_20'] = df['close'].rolling(window=20).mean()
            df['SMA_50'] = df['close'].rolling(window=50).mean()
            df['RSI'] = self.calculate_rsi(df['close'])
            df['MACD'], df['Signal'] = self.calculate_macd(df['close'])

            df.dropna(inplace=True)
            return df
        except Exception as e:
            logging.error(f"Error en prepare_data: {e}")
            return df

    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calcula el Índice de Fuerza Relativa (RSI).
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """
        Calcula la línea MACD y la línea de señal.
        """
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line
