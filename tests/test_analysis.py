import pytest
import pandas as pd
from utils.analysis import MarketAnalyzer

@pytest.fixture
def analyzer():
    """Inicializa el analizador de mercado con IA"""
    return MarketAnalyzer()

@pytest.fixture
def sample_market_data():
    """Crea un DataFrame de muestra con datos de mercado"""
    data = {
        'close': [40000, 40050, 40100, 40150, 40200],
        'RSI': [45, 50, 55, 60, 65],
        'MACD': [1.5, 1.7, 2.0, 2.3, 2.5],
        'Signal': [1.4, 1.6, 1.9, 2.2, 2.4],
        'SMA_20': [39950, 40000, 40050, 40100, 40150],
        'SMA_50': [39800, 39850, 39900, 39950, 40000]
    }
    return pd.DataFrame(data)

def test_analyze_market(analyzer, sample_market_data):
    """Verifica que la IA genera señales válidas"""
    result = analyzer.analyze_market(sample_market_data, "BTC/USD")
    assert isinstance(result, dict), "El resultado debe ser un diccionario JSON"
    assert 'recommendation' in result, "Debe existir una recomendación (COMPRAR, VENDER o MANTENER)"
    assert result['recommendation'] in ["COMPRAR", "VENDER", "MANTENER"], "Recomendación inválida"
    assert 0 <= result['confidence'] <= 1, "El nivel de confianza debe estar entre 0 y 1"

def test_trend_change_analysis(analyzer, sample_market_data):
    """Verifica que el análisis de cambios de tendencia funcione"""
    result = analyzer.analyze_trend_change(sample_market_data, "BTC/USD")
    assert isinstance(result, dict), "El resultado debe ser un diccionario JSON"
    assert 'trend_change' in result, "Debe indicar si hay cambio de tendencia"
    assert isinstance(result['trend_change'], bool), "El valor de trend_change debe ser booleano"
