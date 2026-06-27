"""
ZEUS BOT - ESTRATEGIA BANDAS BOLLINGER (DEL SCRIPT ORIGINAL)
SOLO DA SEÑAL EN CRUCE DE MACD
"""

import time
import threading
import logging
import numpy as np
import random
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from iqoptionapi.stable_api import IQ_Option
    print("✅ IQ_Option API importada correctamente")
except ImportError as e:
    print(f"❌ Error: {e}")
    exit()

# ==================== CONSTANTES ====================
PARES_FIJOS = [
    "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "USDCHF-OTC",
    "USDCAD-OTC", "NZDUSD-OTC", "EURGBP-OTC",
    "EURJPY-OTC", "GBPJPY-OTC", "EURUSD", "GBPUSD", "USDJPY", 
    "USDCHF", "AUDUSD", "USDCAD", "EURGBP", "EURJPY", "GBPJPY"
]

# ==================== ESTRATEGIA BANDAS BOLLINGER (DEL SCRIPT) ====================

class BandasBollingerStrategy:
    """
    ESTRATEGIA BANDAS BOLLINGER - DEL SCRIPT DE TRADINGVIEW
    SOLO DA SEÑAL EN CRUCE DE MACD
    """
    
    def __init__(self):
        # Parámetros del script original
        self.ma_fast_period = 1      # MaFast_period
        self.ma_slow_period = 34     # MaSlow_period
        self.signal_period = 5       # Signal_period
        
    def _sma(self, datos, periodo):
        """Calcula SMA"""
        if len(datos) < periodo:
            return None
        return np.mean(datos[-periodo:])
    
    def _wma(self, datos, periodo):
        """Calcula WMA (Weighted Moving Average)"""
        if len(datos) < periodo:
            return None
        pesos = range(1, periodo + 1)
        return np.sum(np.array(datos[-periodo:]) * pesos) / np.sum(pesos)

    def detectar_señales(self, velas):
        """
        DETECCIÓN DE SEÑALES - BANDAS BOLLINGER ORIGINAL
        SOLO DA SEÑAL EN CRUCE DE MACD
        """
        if len(velas) < 50:
            return None, 0, [], {}
        
        try:
            # Precios de cierre
            precios = [v['close'] for v in velas]
            
            # ============================================================
            # 1. SMA Fast (período 1 = precio actual)
            # ============================================================
            sma_fast = self._sma(precios, self.ma_fast_period)
            
            # ============================================================
            # 2. SMA Slow (período 34)
            # ============================================================
            sma_slow = self._sma(precios, self.ma_slow_period)
            
            if sma_fast is None or sma_slow is None:
                return None, 0, [], {}
            
            # ============================================================
            # 3. MACD Line = SMA Fast - SMA Slow (buffer1)
            # ============================================================
            macd_line = sma_fast - sma_slow
            
            # ============================================================
            # 4. Signal Line = WMA del MACD (período 5) (buffer2)
            # ============================================================
            # Necesitamos calcular la WMA de los últimos valores de MACD
            macd_values = []
            for i in range(self.signal_period):
                if len(precios) > i + self.ma_slow_period:
                    sf = self._sma(precios[:-i] if i > 0 else precios, self.ma_fast_period)
                    ss = self._sma(precios[:-i] if i > 0 else precios, self.ma_slow_period)
                    if sf and ss:
                        macd_values.append(sf - ss)
            
            if macd_values:
                signal_line = self._wma(macd_values, self.signal_period)
            else:
                signal_line = macd_line
            
            # ============================================================
            # 5. MACD anterior (para el cruce)
            # ============================================================
            macd_prev = None
            signal_prev = None
            
            if len(velas) > 1:
                precios_prev = [v['close'] for v in velas[:-1]]
                
                sf_prev = self._sma(precios_prev, self.ma_fast_period)
                ss_prev = self._sma(precios_prev, self.ma_slow_period)
                
                if sf_prev and ss_prev:
                    macd_prev = sf_prev - ss_prev
                    
                    macd_vals_prev = []
                    for i in range(self.signal_period):
                        if len(precios_prev) > i + self.ma_slow_period:
                            sf2 = self._sma(precios_prev[:-i] if i > 0 else precios_prev, self.ma_fast_period)
                            ss2 = self._sma(precios_prev[:-i] if i > 0 else precios_prev, self.ma_slow_period)
                            if sf2 and ss2:
                                macd_vals_prev.append(sf2 - ss2)
                    
                    if macd_vals_prev:
                        signal_prev = self._wma(macd_vals_prev, self.signal_period)
                    else:
                        signal_prev = macd_prev
            
            # ============================================================
            # 6. DETECCIÓN DE CRUCES (como en el script original)
            # ============================================================
            puntos = 0
            señales_detectadas = []
            señal_especifica = None
            
            # BUY CONDITION: MACD > Signal AND MACD anterior < Signal anterior
            if macd_line and signal_line and macd_prev and signal_prev:
                buy_condition = macd_line > signal_line and macd_prev < signal_prev
                sell_condition = macd_line < signal_line and macd_prev > signal_prev
                
                if buy_condition:
                    puntos += 3.0
                    señal_especifica = "MACD_CROSS_CALL"
                    señales_detectadas.append("MACD_CROSS_CALL")
                    print(f"✅ MACD CROSS CALL (buyCondition)")
                
                elif sell_condition:
                    puntos -= 3.0
                    señal_especifica = "MACD_CROSS_PUT"
                    señales_detectadas.append("MACD_CROSS_PUT")
                    print(f"✅ MACD CROSS PUT (sellCondition)")
            
            # ============================================================
            # 7. DECISIÓN FINAL - SOLO SI HAY CRUCE
            # ============================================================
            señal_final = None
            
            if señal_especifica:
                if puntos > 0:
                    señal_final = "CALL"
                    print(f"🎯 SEÑAL: CALL (puntos: {puntos:.1f})")
                else:
                    señal_final = "PUT"
                    print(f"🎯 SEÑAL: PUT (puntos: {puntos:.1f})")
            else:
                print(f"⏸ Sin cruce de MACD")
            
            return señal_final, puntos, señales_detectadas, {
                'macd': macd_line,
                'signal': signal_line,
                'macd_prev': macd_prev,
                'signal_prev': signal_prev
            }
            
        except Exception as e:
            print(f"Error en estrategia: {e}")
            return None, 0, [], {}

# ==================== BOT IQ OPTION ====================

class MiBotIQOption:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.api = None
        self.connected = False
        self.modo_actual = "PRACTICE"
        
    def conectar(self):
        try:
            self.api = IQ_Option(self.email, self.password)
            self.connected, reason = self.api.connect()
            
            if self.connected:
                self.api.change_balance(self.modo_actual)
                print(f"✅ Conectado, balance: ${self.api.get_balance():.2f}")
                return True
            print(f"❌ Error: {reason}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def cambiar_modo(self, modo):
        modo_api = "PRACTICE" if modo == "DEMO" else "REAL"
        self.modo_actual = modo_api
        if self.connected:
            self.api.change_balance(modo_api)
            return True
        return False
    
    def get_balance(self):
        if self.connected:
            try:
                return self.api.get_balance()
            except:
                return 0
        return 0
    
    def obtener_velas(self, activo, intervalo=60, cantidad=120):
        try:
            if not self.connected:
                return None
            endtime = int(time.time())
            velas = self.api.get_candles(activo, intervalo, cantidad, endtime)
            if velas and len(velas) > 0:
                return velas
            return None
        except Exception as e:
            return None
    
    def ejecutar_operacion(self, activo, direccion, monto, tiempo=1):
        try:
            if not self.connected:
                return None
            
            accion = "call" if direccion == "CALL" else "put"
            
            print(f"💼 Comprando {accion} en {activo} por ${monto:.2f}")
            exito, id_op = self.api.buy(monto, activo, accion, tiempo)
            
            if exito:
                print(f"✅ Operación iniciada, ID: {id_op}")
                time.sleep(tiempo * 60)
                
                try:
                    resultado = self.api.get_winning(id_op)
                    print(f"📊 Resultado: {resultado}")
                    
                    if resultado > 0:
                        ganancia = monto * 0.80
                    else:
                        ganancia = -monto
                    
                except Exception as e:
                    print(f"⚠️ Error obteniendo resultado: {e}")
                    return {'ganancia': None, 'id': id_op}
                
                balance_final = self.api.get_balance()
                print(f"💰 Balance final: ${balance_final:.2f}")
                
                return {
                    'ganancia': ganancia,
                    'balance_final': balance_final,
                    'id': id_op
                }
            
            print(f"❌ Error al comprar: {id_op}")
            return None
            
        except Exception as e:
            print(f"❌ Error en operación: {e}")
            return None

# ==================== ZEUS BOT ====================

class ZeusBot:
    def __init__(self):
        self.bot = None
        self.strategy = BandasBollingerStrategy()
        self.actualizando = False
        self.operando = False
        
        self.par_actual = "EURUSD-OTC"
        self.par_enfocado = None
        
        self.ops = 0
        self.wins = 0
        self.losses = 0
        self.profit = 0.0
        self.racha_perdidas = 0
        self.monto_actual = 1.0
        self.monto_base = 1.0
        self.multiplicador = 2.1
        self.tiempo = 1
        self.martingala = False
        self.umbral = 0.5
        
        self._callbacks = []
        
    def conectar(self, email, password):
        try:
            self.bot = MiBotIQOption(email, password)
            if self.bot.conectar():
                self._emit("log", "✅ Conectado a IQ Option", "info")
                self._emit("balance", self.bot.get_balance())
                return True
            else:
                self._emit("log", "❌ Error de conexión", "error")
                return False
        except Exception as e:
            self._emit("log", f"❌ Error: {e}", "error")
            return False
    
    def cambiar_modo(self, modo):
        if self.bot:
            self.bot.cambiar_modo(modo)
            self._emit("log", f"🔄 Modo cambiado a {modo}", "info")
            self._emit("balance", self.bot.get_balance())
    
    def iniciar(self, config):
        if not self.bot or not self.bot.connected:
            self._emit("log", "❌ No conectado a IQ Option", "error")
            return
        
        self.par_actual = config.get("par", "EURUSD-OTC")
        self.monto_base = float(config.get("monto", 1))
        self.monto_actual = self.monto_base
        self.tiempo = int(config.get("tiempo", 1))
        self.multiplicador = float(config.get("multiplicador", 2.1))
        self.martingala = config.get("martingala", "no") == "si"
        
        self.ops = 0
        self.wins = 0
        self.losses = 0
        self.profit = 0.0
        self.racha_perdidas = 0
        self.par_enfocado = None
        self.actualizando = True
        
        self._emit("log", f"🚀 BOT INICIADO - {self.par_actual}", "info")
        self._emit("log", "📊 Estrategia: Bandas Bollinger (MACD CRUCE)", "info")
        self._emit("estado", True)
        
        threading.Thread(target=self._ejecutar_bot, daemon=True).start()
    
    def detener(self):
        self.actualizando = False
        self.operando = False
        self._emit("log", "⏹ BOT DETENIDO", "info")
        self._emit("estado", False)
    
    def _ejecutar_bot(self):
        while self.actualizando:
            try:
                if self.par_enfocado:
                    activo = self.par_enfocado
                else:
                    activo = self.par_actual
                
                velas = self.bot.obtener_velas(activo, 60, 120)
                
                if velas and len(velas) > 50:
                    señal, puntos, señales, _ = self.strategy.detectar_señales(velas)
                    
                    if señal:
                        self._emit("log", f"🎯 {señal} en {activo} (puntos: {puntos:.1f})", "señal")
                        
                        monto = self.monto_actual
                        if self.martingala and self.racha_perdidas > 0:
                            monto = self.monto_base * (self.multiplicador ** self.racha_perdidas)
                            if self.racha_perdidas >= 3:
                                monto = self.monto_base * (self.multiplicador ** 3)
                            self._emit("log", f"🔄 Martingala: {self.racha_perdidas} pérdidas, ${monto:.2f}", "info")
                        
                        balance_antes = self.bot.get_balance()
                        resultado = self.bot.ejecutar_operacion(activo, señal, monto, self.tiempo)
                        
                        if resultado and resultado.get('ganancia') is not None:
                            ganancia = resultado['ganancia']
                            
                            if ganancia > 0:
                                self.wins += 1
                                self.racha_perdidas = 0
                                self.monto_actual = self.monto_base
                                self.par_enfocado = None
                                self._emit("log", f"✅ GANANCIA +${ganancia:.2f}", "win")
                                self._emit("balance", self.bot.get_balance())
                            else:
                                self.losses += 1
                                self.racha_perdidas += 1
                                if self.martingala:
                                    self.monto_actual = self.monto_base * (self.multiplicador ** self.racha_perdidas)
                                self.par_enfocado = activo
                                self._emit("log", f"❌ PÉRDIDA ${ganancia:.2f}", "loss")
                                self._emit("log", f"🎯 Enfocando {activo}", "info")
                                self._emit("balance", self.bot.get_balance())
                            
                            self.ops += 1
                            self.profit += ganancia
                            self._emit("stats", {
                                "ops": self.ops,
                                "wins": self.wins,
                                "losses": self.losses,
                                "profit": self.profit,
                                "racha": self.racha_perdidas
                            })
                            self._emit("ultima", f"{activo} {señal} ${ganancia:.2f}")
                        else:
                            balance_despues = self.bot.get_balance()
                            diferencia = balance_despues - balance_antes
                            
                            if abs(diferencia) > 0.1:
                                if diferencia > 0:
                                    self.wins += 1
                                    self.racha_perdidas = 0
                                    self.monto_actual = self.monto_base
                                    self.par_enfocado = None
                                    self.profit += diferencia
                                    self._emit("log", f"✅ GANANCIA +${diferencia:.2f}", "win")
                                    self._emit("balance", balance_despues)
                                else:
                                    self.losses += 1
                                    self.racha_perdidas += 1
                                    if self.martingala:
                                        self.monto_actual = self.monto_base * (self.multiplicador ** self.racha_perdidas)
                                    self.par_enfocado = activo
                                    self.profit += diferencia
                                    self._emit("log", f"❌ PÉRDIDA ${diferencia:.2f}", "loss")
                                    self._emit("log", f"🎯 Enfocando {activo}", "info")
                                    self._emit("balance", balance_despues)
                                
                                self.ops += 1
                                self._emit("stats", {
                                    "ops": self.ops,
                                    "wins": self.wins,
                                    "losses": self.losses,
                                    "profit": self.profit,
                                    "racha": self.racha_perdidas
                                })
                                self._emit("ultima", f"{activo} {señal} ${diferencia:.2f}")
                    
                    # Esperar 5 segundos antes de la siguiente comprobación
                    time.sleep(5)
                else:
                    time.sleep(3)
                    
            except Exception as e:
                self._emit("log", f"❌ Error: {str(e)[:30]}", "error")
                print(f"Error: {e}")
                time.sleep(3)
    
    def on(self, event, callback):
        self._callbacks.append((event, callback))
    
    def _emit(self, event, data, tipo=None):
        for evt, cb in self._callbacks:
            if evt == event:
                try:
                    if tipo:
                        cb(data, tipo)
                    else:
                        cb(data)
                except:
                    pass