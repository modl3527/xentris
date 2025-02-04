import ollama
import json
import logging
import pandas as pd

class MarketAnalyzer:
    def __init__(self):
        """Inicializar el analizador de mercado con Ollama (IA Local)"""
        logging.basicConfig(
            filename='market_analysis.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def analyze_market(self, market_data: pd.DataFrame, symbol: str):
        """Analizar datos de mercado usando IA Local (Ollama)"""
        try:
            if market_data is None or market_data.empty:
                logging.error("Datos de mercado vacíos o None")
                return None

            latest_data = market_data.iloc[0]

            prompt = f"""
            Analiza estos datos de mercado para {symbol} y proporciona una recomendación en formato JSON.

            Datos actuales:
            - Precio: {latest_data['close']}
            - RSI: {latest_data['RSI']:.2f}
            - MACD: {latest_data['MACD']:.2f}
            - Señal MACD: {latest_data['Signal']:.2f}
            - SMA 20: {latest_data['SMA_20']:.2f}
            - SMA 50: {latest_data['SMA_50']:.2f}

            Responde en JSON con el siguiente formato:
            {{
                "recommendation": "COMPRAR"|"VENDER"|"MANTENER",
                "confidence": <número entre 0 y 1>,
                "reasoning": "<explicación>",
                "risk_level": "BAJO"|"MEDIO"|"ALTO",
                "suggested_sl": {latest_data['close'] * 0.99:.5f},
                "suggested_tp": {latest_data['close'] * 1.01:.5f}
            }}
            """

            response = ollama.chat(model="deepseek-r1:14b", messages=[{"role": "user", "content": prompt}])
            analysis_text = response['message']['content']

            try:
                analysis = json.loads(analysis_text)
                logging.info(f"Análisis completado: {analysis['recommendation']}")
                return analysis
            except json.JSONDecodeError as e:
                logging.error(f"Error en el JSON de Ollama: {e}")
                return None

        except Exception as e:
            logging.error(f"Error en análisis de mercado: {e}")
            return None
