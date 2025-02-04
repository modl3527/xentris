import pytest
import pandas as pd
from utils.market_data import MarketDataManager

@pytest.fixture
def market():
    """Inicializa el manejador de datos de mercado con BTC/USD y timeframe de 1min"""
    return MarketDataManager("BTC/USD", "1min")

def test_get_twelve_data(market):
    """Verifica que la API de TwelveData retorne datos válidos"""
    df = market.get_twelve_data()
    assert isinstance(df, pd.DataFrame), "El resultado debe ser un DataFrame"
    assert not df.empty, "Los datos de TwelveData no deben estar vacíos"
    assert all(col in df.columns for col in ['open', 'high', 'low', 'close']), "Faltan columnas clave"

def test_initialize_mt5(market):
    """Verifica que la inicialización de MT5 sea exitosa"""
    assert market.initialize_mt5(), "MT5 no se pudo inicializar correctamente"

def test_get_mt5_data(market):
    """Verifica que los datos obtenidos de MT5 sean válidos"""
    df = market.get_mt5_data()
    assert isinstance(df, pd.DataFrame), "El resultado debe ser un DataFrame"
    assert not df.empty, "Los datos de MT5 no deben estar vacíos"
    assert all(col in df.columns for col in ['open', 'high', 'low', 'close']), "Faltan columnas clave"

def test_calculate_rsi(market):
    """Verifica que el RSI se calcula correctamente"""
    df = market.get_twelve_data()
    df = market.prepare_data(df)
    assert 'RSI' in df.columns, "RSI no fue calculado"
    assert df['RSI'].notnull().all(), "RSI no debe contener valores nulos"

def test_calculate_macd(market):
    """Verifica que el MACD y la señal sean calculados correctamente"""
    df = market.get_twelve_data()
    df = market.prepare_data(df)
    assert 'MACD' in df.columns, "MACD no fue calculado"
    assert 'Signal' in df.columns, "La señal MACD no fue calculada"
    assert df['MACD'].notnull().all(), "MACD no debe contener valores nulos"
    assert df['Signal'].notnull().all(), "Signal no debe contener valores nulos"
