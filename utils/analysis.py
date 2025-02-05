import os
import json
import logging
import httpx
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Crea un cliente HTTP personalizado sin proxies (timeout de 10 segundos)
custom_http_client = httpx.Client(timeout=10.0)

class MarketAnalyzer:
    def __init__(self):
        # Inicializa el cliente OpenAI apuntando a la instancia local de Ollama
        self.client = OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='ollama',  # Se requiere, pero no se usa para autenticar
            http_client=custom_http_client  # Usamos el cliente HTTP sin proxies
        )
        logging.basicConfig(
            filename='market_analysis.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def analyze_market(self, market_data: pd.DataFrame, symbol: str):
        """
        Envía un prompt a la IA para analizar datos de mercado y obtener una recomendación.
        Retorna un diccionario con la respuesta en JSON o None en caso de error.
        """
        try:
            if market_data is None or market_data.empty:
                logging.error("Datos de mercado vacíos o None")
                return None

            latest_data = market_data.iloc[0]
            prompt = (
                f"Analiza estos datos de mercado para {symbol} y proporciona una recomendación en formato JSON.\n\n"
                f"Datos actuales:\n"
                f"- Precio: {latest_data['close']}\n"
                f"- RSI: {latest_data.get('RSI', 0):.2f}\n"
                f"- MACD: {latest_data.get('MACD', 0):.2f}\n"
                f"- Señal MACD: {latest_data.get('Signal', 0):.2f}\n"
                f"- SMA 20: {latest_data.get('SMA_20', 0):.2f}\n"
                f"- SMA 50: {latest_data.get('SMA_50', 0):.2f}\n\n"
                f"Responde en JSON con el siguiente formato:\n"
                f"{{\n"
                f'    "recommendation": "COMPRAR"|"VENDER"|"MANTENER",\n'
                f'    "confidence": <número entre 0 y 1>,\n'
                f'    "reasoning": "<explicación>",\n'
                f'    "risk_level": "BAJO"|"MEDIO"|"ALTO",\n'
                f'    "suggested_sl": {latest_data["close"] * 0.99:.5f},\n'
                f'    "suggested_tp": {latest_data["close"] * 1.01:.5f}\n'
                f"}}"
            )

            response = self.client.chat.completions.create(
                model="llama2",
                messages=[
                    {"role": "system", "content": "Eres un analista financiero que proporciona recomendaciones de trading."},
                    {"role": "user", "content": prompt}
                ]
            )

            analysis_text = response.choices[0].message.content
            try:
                analysis = json.loads(analysis_text)
                logging.info(f"Análisis completado: {analysis.get('recommendation')}")
                return analysis
            except json.JSONDecodeError as e:
                logging.error(f"Error al decodificar JSON: {e}")
                logging.debug(f"Respuesta recibida: {analysis_text}")
                return None

        except Exception as e:
            logging.error(f"Error en análisis de mercado: {e}")
            return None

    def analyze_trend_change(self, market_data: pd.DataFrame, symbol: str):
        """
        Envía un prompt a la IA para detectar cambios en la tendencia.
        Retorna un diccionario con la respuesta en JSON o None en caso de error.
        """
        try:
            if market_data is None or market_data.empty:
                logging.error("Datos de mercado vacíos o None")
                return None

            latest_data = market_data.iloc[0]
            prompt = (
                f"Analiza estos datos de mercado para {symbol} y detecta si hay un cambio en la tendencia.\n\n"
                f"Proporciona un JSON con el siguiente formato:\n"
                f"{{\n"
                f'    "trend_change": true|false,\n'
                f'    "direction": "BUY"|"SELL",\n'
                f'    "reasoning": "<explicación>"\n'
                f"}}\n\n"
                f"Datos actuales:\n"
                f"- Precio: {latest_data['close']}\n"
                f"- RSI: {latest_data.get('RSI', 0):.2f}\n"
                f"- MACD: {latest_data.get('MACD', 0):.2f}\n"
                f"- Señal MACD: {latest_data.get('Signal', 0):.2f}\n"
            )

            response = self.client.chat.completions.create(
                model="deepseek-r1:14b",
                messages=[
                    {"role": "system", "content": "Eres un analista financiero experto en detectar cambios de tendencia."},
                    {"role": "user", "content": prompt}
                ]
            )

            analysis_text = response.choices[0].message.content
            try:
                analysis = json.loads(analysis_text)
                logging.info("Análisis de cambio de tendencia completado")
                return analysis
            except json.JSONDecodeError as e:
                logging.error(f"Error al decodificar JSON en analyze_trend_change: {e}")
                logging.debug(f"Respuesta recibida: {analysis_text}")
                return None

        except Exception as e:
            logging.error(f"Error en análisis de cambio de tendencia: {e}")
            return None

# Ejemplo de uso
if __name__ == "__main__":
    # Datos de ejemplo para probar la funcionalidad (reemplaza con datos reales según necesites)
    data = {
        'close': [40000, 40050, 40150, 40200],
        'RSI': [45, 50, 60, 65],
        'MACD': [1.5, 1.7, 2.3, 2.5],
        'Signal': [1.4, 1.6, 2.2, 2.4],
        'SMA_20': [39950, 40000, 40100, 40150],
        'SMA_50': [39800, 39900, 39950, 40000]
    }
    df_sample = pd.DataFrame(data)

    analyzer = MarketAnalyzer()

    # Analizar mercado
    market_result = analyzer.analyze_market(df_sample, "BTC/USD")
    print("Resultado del análisis de mercado:")
    print(market_result)

    # Analizar cambio de tendencia
    trend_result = analyzer.analyze_trend_change(df_sample, "BTC/USD")
    print("Resultado del análisis de cambio de tendencia:")
    print(trend_result)
