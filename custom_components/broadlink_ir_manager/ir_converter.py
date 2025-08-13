#!/usr/bin/env python3
"""
Conversor de códigos IR - Broadlink Base64 para Pronto Hex
Desenvolvido para integração com Home Assistant
"""

import base64
import struct
import json
from typing import List, Tuple, Optional


class IRConverter:
    """Classe para conversão de códigos IR entre diferentes formatos"""
    
    def __init__(self):
        self.carrier_frequency = 38000  # Frequência padrão 38kHz
        
    def base64_to_bytes(self, base64_code: str) -> bytes:
        """Converte código Base64 para bytes"""
        try:
            # Remove prefixo b64: se presente
            if base64_code.startswith('b64:'):
                base64_code = base64_code[4:]
            
            return base64.b64decode(base64_code)
        except Exception as e:
            raise ValueError(f"Erro ao decodificar Base64: {e}")
    
    def parse_broadlink_data(self, data: bytes) -> Tuple[List[int], int]:
        """
        Extrai dados de timing do formato Broadlink
        Retorna: (timings, frequency)
        """
        if len(data) < 4:
            raise ValueError("Dados Broadlink muito curtos")
        
        # Verifica se é um código IR (primeiro byte deve ser 0x26)
        if data[0] != 0x26:
            raise ValueError("Não é um código IR válido do Broadlink")
        
        # Extrai o comprimento dos dados
        length = struct.unpack('<H', data[2:4])[0]
        
        # Verifica terminadores
        if len(data) >= length + 4:
            end_bytes = data[length + 2:length + 4]
            if end_bytes == b'\x0d\x05':
                # Ajusta comprimento se necessário
                length -= 2
        
        # Extrai os dados de timing
        timing_data = data[4:4 + length]
        timings = []
        
        # Converte bytes para timings
        for i in range(0, len(timing_data), 2):
            if i + 1 < len(timing_data):
                timing = struct.unpack('<H', timing_data[i:i+2])[0]
                # Converte para microssegundos
                timing_us = timing * 269 / 8  # Fator de conversão Broadlink
                timings.append(int(timing_us))
        
        return timings, self.carrier_frequency
    
    def timings_to_pronto(self, timings: List[int], frequency: int = 38000) -> str:
        """
        Converte lista de timings para formato Pronto Hex
        """
        if not timings:
            raise ValueError("Lista de timings vazia")
        
        # Calcula frequência em formato Pronto (0x73 para 38kHz)
        if frequency == 38000:
            pronto_freq = 0x0073
        else:
            pronto_freq = int(4145146 / frequency)
        
        # Converte timings para unidades Pronto
        pronto_timings = []
        for timing in timings:
            # Converte microssegundos para unidades Pronto
            # Fórmula: timing_us * frequency / 1000000
            pronto_timing = int(round(timing * frequency / 1000000))
            pronto_timings.append(pronto_timing)
        
        # Constrói código Pronto
        pronto_code = []
        
        # Preâmbulo
        pronto_code.append("0000")  # Tipo de código (learned)
        pronto_code.append(f"{pronto_freq:04X}")  # Frequência
        pronto_code.append("0000")  # Comprimento burst único (não usado)
        pronto_code.append(f"{len(pronto_timings):04X}")  # Comprimento total
        
        # Adiciona timings convertidos
        for timing in pronto_timings:
            # Garante que seja limitado a 16 bits
            timing = min(timing, 0xFFFF)
            pronto_code.append(f"{timing:04X}")
        
        return " ".join(pronto_code)
    
    def broadlink_to_pronto(self, base64_code: str) -> str:
        """
        Converte código Broadlink Base64 para Pronto Hex
        """
        try:
            # Decodifica Base64
            data = self.base64_to_bytes(base64_code)
            
            # Extrai timings
            timings, frequency = self.parse_broadlink_data(data)
            
            # Converte para Pronto
            pronto_code = self.timings_to_pronto(timings, frequency)
            
            return pronto_code
            
        except Exception as e:
            raise ValueError(f"Erro na conversão: {e}")
    
    def validate_pronto(self, pronto_code: str) -> bool:
        """Valida se um código Pronto está bem formado"""
        try:
            parts = pronto_code.split()
            
            # Deve ter pelo menos 4 palavras no preâmbulo
            if len(parts) < 4:
                return False
            
            # Primeira palavra deve ser 0000 (learned code)
            if parts[0] != "0000":
                return False
            
            # Todas as partes devem ser hexadecimais de 4 dígitos
            for part in parts:
                if len(part) != 4:
                    return False
                int(part, 16)  # Testa se é hexadecimal válido
            
            return True
            
        except (ValueError, IndexError):
            return False
    
    def get_frequency_from_pronto(self, pronto_code: str) -> int:
        """Extrai frequência de um código Pronto"""
        try:
            parts = pronto_code.split()
            if len(parts) >= 2:
                freq_hex = parts[1]
                pronto_freq = int(freq_hex, 16)
                # Fórmula correta para conversão
                if pronto_freq == 0x0073:
                    return 38000  # Frequência padrão
                else:
                    return int(4145146 / pronto_freq)
            return 38000  # Padrão
        except:
            return 38000


def test_converter():
    """Função de teste para o conversor"""
    converter = IRConverter()
    
    # Código de exemplo (substitua por um código real)
    test_base64 = "JgAcAB0dHB44HhweGx4cHR06HB0cHhwdHB8bHhwADQUAAAAAAAAAAAAAAAA="
    
    try:
        pronto_result = converter.broadlink_to_pronto(test_base64)
        print(f"Base64: {test_base64}")
        print(f"Pronto: {pronto_result}")
        print(f"Válido: {converter.validate_pronto(pronto_result)}")
        print(f"Frequência: {converter.get_frequency_from_pronto(pronto_result)}Hz")
        
    except Exception as e:
        print(f"Erro no teste: {e}")


if __name__ == "__main__":
    test_converter()

