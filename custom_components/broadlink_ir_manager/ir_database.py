#!/usr/bin/env python3
"""
Gerenciador de Base de Dados IR
Sistema para armazenar e gerenciar códigos IR capturados
"""

import json
import os
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from ir_converter import IRConverter


@dataclass
class IRCode:
    """Classe para representar um código IR"""
    id: str
    name: str
    device: str
    command: str
    base64_code: str
    pronto_code: str
    frequency: int
    created_at: str
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IRCode':
        """Cria instância a partir de dicionário"""
        return cls(**data)


class IRDatabase:
    """Gerenciador de base de dados de códigos IR"""
    
    def __init__(self, db_path: str = "ir_codes.json"):
        self.db_path = db_path
        self.converter = IRConverter()
        self.codes: Dict[str, IRCode] = {}
        self.load_database()
    
    def load_database(self):
        """Carrega base de dados do arquivo"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for code_id, code_data in data.items():
                        self.codes[code_id] = IRCode.from_dict(code_data)
            except Exception as e:
                print(f"Erro ao carregar base de dados: {e}")
                self.codes = {}
        else:
            self.codes = {}
    
    def save_database(self):
        """Salva base de dados no arquivo"""
        try:
            data = {code_id: code.to_dict() for code_id, code in self.codes.items()}
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar base de dados: {e}")
    
    def add_code(self, name: str, device: str, command: str, 
                 base64_code: str, notes: str = "") -> str:
        """
        Adiciona novo código IR à base de dados
        Retorna: ID do código adicionado
        """
        try:
            # Converte para Pronto Hex
            pronto_code = self.converter.broadlink_to_pronto(base64_code)
            frequency = self.converter.get_frequency_from_pronto(pronto_code)
            
            # Gera ID único
            code_id = self.generate_id(device, command)
            
            # Cria objeto IRCode
            ir_code = IRCode(
                id=code_id,
                name=name,
                device=device,
                command=command,
                base64_code=base64_code,
                pronto_code=pronto_code,
                frequency=frequency,
                created_at=datetime.datetime.now().isoformat(),
                notes=notes
            )
            
            # Adiciona à base de dados
            self.codes[code_id] = ir_code
            self.save_database()
            
            return code_id
            
        except Exception as e:
            raise ValueError(f"Erro ao adicionar código: {e}")
    
    def get_code(self, code_id: str) -> Optional[IRCode]:
        """Obtém código por ID"""
        return self.codes.get(code_id)
    
    def get_codes_by_device(self, device: str) -> List[IRCode]:
        """Obtém todos os códigos de um dispositivo"""
        return [code for code in self.codes.values() if code.device == device]
    
    def get_all_codes(self) -> List[IRCode]:
        """Obtém todos os códigos"""
        return list(self.codes.values())
    
    def get_devices(self) -> List[str]:
        """Obtém lista de dispositivos únicos"""
        devices = set(code.device for code in self.codes.values())
        return sorted(list(devices))
    
    def delete_code(self, code_id: str) -> bool:
        """Remove código da base de dados"""
        if code_id in self.codes:
            del self.codes[code_id]
            self.save_database()
            return True
        return False
    
    def update_code(self, code_id: str, **kwargs) -> bool:
        """Atualiza código existente"""
        if code_id in self.codes:
            code = self.codes[code_id]
            
            # Atualiza campos permitidos
            for field, value in kwargs.items():
                if hasattr(code, field):
                    setattr(code, field, value)
            
            # Se o base64_code foi alterado, reconverte
            if 'base64_code' in kwargs:
                try:
                    code.pronto_code = self.converter.broadlink_to_pronto(code.base64_code)
                    code.frequency = self.converter.get_frequency_from_pronto(code.pronto_code)
                except Exception as e:
                    print(f"Erro na reconversão: {e}")
                    return False
            
            self.save_database()
            return True
        return False
    
    def generate_id(self, device: str, command: str) -> str:
        """Gera ID único para o código"""
        base_id = f"{device}_{command}".lower().replace(" ", "_")
        
        # Remove caracteres especiais
        import re
        base_id = re.sub(r'[^a-z0-9_]', '', base_id)
        
        # Verifica se já existe
        if base_id not in self.codes:
            return base_id
        
        # Adiciona sufixo numérico se necessário
        counter = 1
        while f"{base_id}_{counter}" in self.codes:
            counter += 1
        
        return f"{base_id}_{counter}"
    
    def search_codes(self, query: str) -> List[IRCode]:
        """Busca códigos por nome, dispositivo ou comando"""
        query = query.lower()
        results = []
        
        for code in self.codes.values():
            if (query in code.name.lower() or 
                query in code.device.lower() or 
                query in code.command.lower() or
                query in code.notes.lower()):
                results.append(code)
        
        return results
    
    def export_to_json(self, file_path: str) -> bool:
        """Exporta base de dados para arquivo JSON"""
        try:
            data = {
                "export_date": datetime.datetime.now().isoformat(),
                "total_codes": len(self.codes),
                "codes": {code_id: code.to_dict() for code_id, code in self.codes.items()}
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Erro na exportação: {e}")
            return False
    
    def import_from_json(self, file_path: str) -> bool:
        """Importa códigos de arquivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'codes' in data:
                for code_id, code_data in data['codes'].items():
                    self.codes[code_id] = IRCode.from_dict(code_data)
                
                self.save_database()
                return True
            
            return False
        except Exception as e:
            print(f"Erro na importação: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas da base de dados"""
        devices = self.get_devices()
        
        stats = {
            "total_codes": len(self.codes),
            "total_devices": len(devices),
            "devices": devices,
            "codes_by_device": {
                device: len(self.get_codes_by_device(device)) 
                for device in devices
            }
        }
        
        return stats


def test_database():
    """Função de teste para a base de dados"""
    db = IRDatabase("test_ir_codes.json")
    
    # Teste de adição
    test_base64 = "JgAcAB0dHB44HhweGx4cHR06HB0cHhwdHB8bHhwADQUAAAAAAAAAAAAAAAA="
    
    try:
        code_id = db.add_code(
            name="Power On",
            device="TV Samsung",
            command="power_on",
            base64_code=test_base64,
            notes="Código de teste"
        )
        
        print(f"Código adicionado com ID: {code_id}")
        
        # Teste de busca
        code = db.get_code(code_id)
        if code:
            print(f"Código encontrado: {code.name}")
            print(f"Pronto: {code.pronto_code}")
        
        # Estatísticas
        stats = db.get_statistics()
        print(f"Estatísticas: {stats}")
        
        # Limpeza
        os.remove("test_ir_codes.json")
        
    except Exception as e:
        print(f"Erro no teste: {e}")


if __name__ == "__main__":
    test_database()

