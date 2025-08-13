"""Sensores para o Broadlink IR Manager"""

import logging
from typing import Optional

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    STATE_IDLE,
    STATE_LEARNING,
    STATE_CODE_RECEIVED,
    ATTR_BASE64_CODE,
    ATTR_PRONTO_CODE,
    ATTR_FREQUENCY,
    ATTR_LEARNING_TIMEOUT,
    ATTR_LAST_CODE,
    ATTR_CODES_COUNT,
)
from .coordinator import BroadlinkIRCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura sensores"""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    database = hass.data[DOMAIN]["database"]
    converter = hass.data[DOMAIN]["converter"]
    
    entities = [
        BroadlinkIRStatusSensor(coordinator),
        BroadlinkIRCodeSensor(coordinator, converter),
        BroadlinkIRDatabaseSensor(coordinator, database),
    ]
    
    async_add_entities(entities)


class BroadlinkIRStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor de status do Broadlink IR Manager"""
    
    def __init__(self, coordinator: BroadlinkIRCoordinator) -> None:
        """Inicializa sensor de status"""
        super().__init__(coordinator)
        self._attr_name = "Broadlink IR Status"
        self._attr_unique_id = f"{DOMAIN}_status"
        self._attr_icon = "mdi:remote"
    
    @property
    def native_value(self) -> str:
        """Valor do sensor"""
        if self.coordinator.data:
            return self.coordinator.data.get("state", STATE_IDLE)
        return STATE_IDLE
    
    @property
    def extra_state_attributes(self) -> dict:
        """Atributos extras do sensor"""
        if not self.coordinator.data:
            return {}
        
        attrs = {
            "device_connected": self.coordinator.data.get("device_connected", False),
            "host": self.coordinator.data.get("host"),
            "mac": self.coordinator.data.get("mac"),
        }
        
        if self.coordinator.state == STATE_LEARNING:
            attrs[ATTR_LEARNING_TIMEOUT] = self.coordinator.timeout
        
        return attrs
    
    @property
    def available(self) -> bool:
        """Disponibilidade do sensor"""
        return self.coordinator.last_update_success
    
    @property
    def device_info(self):
        """Informações do dispositivo"""
        return self.coordinator.device_info


class BroadlinkIRCodeSensor(CoordinatorEntity, SensorEntity):
    """Sensor para códigos IR capturados"""
    
    def __init__(self, coordinator: BroadlinkIRCoordinator, converter) -> None:
        """Inicializa sensor de códigos"""
        super().__init__(coordinator)
        self.converter = converter
        self._attr_name = "Broadlink IR Last Code"
        self._attr_unique_id = f"{DOMAIN}_last_code"
        self._attr_icon = "mdi:barcode"
    
    @property
    def native_value(self) -> Optional[str]:
        """Valor do sensor"""
        if self.coordinator.last_learned_code:
            return "Code Available"
        return "No Code"
    
    @property
    def extra_state_attributes(self) -> dict:
        """Atributos extras do sensor"""
        attrs = {}
        
        if self.coordinator.last_learned_code:
            base64_code = self.coordinator.last_learned_code
            attrs[ATTR_BASE64_CODE] = base64_code
            
            try:
                pronto_code = self.converter.broadlink_to_pronto(base64_code)
                frequency = self.converter.get_frequency_from_pronto(pronto_code)
                
                attrs[ATTR_PRONTO_CODE] = pronto_code
                attrs[ATTR_FREQUENCY] = frequency
            except Exception as e:
                _LOGGER.error(f"Erro na conversão: {e}")
                attrs["conversion_error"] = str(e)
        
        return attrs
    
    @property
    def available(self) -> bool:
        """Disponibilidade do sensor"""
        return self.coordinator.last_update_success
    
    @property
    def device_info(self):
        """Informações do dispositivo"""
        return self.coordinator.device_info


class BroadlinkIRDatabaseSensor(CoordinatorEntity, SensorEntity):
    """Sensor para estatísticas da base de dados"""
    
    def __init__(self, coordinator: BroadlinkIRCoordinator, database) -> None:
        """Inicializa sensor da base de dados"""
        super().__init__(coordinator)
        self.database = database
        self._attr_name = "Broadlink IR Database"
        self._attr_unique_id = f"{DOMAIN}_database"
        self._attr_icon = "mdi:database"
        self._attr_device_class = SensorDeviceClass.DATA_SIZE
        self._attr_native_unit_of_measurement = "codes"
    
    @property
    def native_value(self) -> int:
        """Valor do sensor (número total de códigos)"""
        stats = self.database.get_statistics()
        return stats.get("total_codes", 0)
    
    @property
    def extra_state_attributes(self) -> dict:
        """Atributos extras do sensor"""
        stats = self.database.get_statistics()
        
        attrs = {
            "total_devices": stats.get("total_devices", 0),
            "devices": stats.get("devices", []),
            "codes_by_device": stats.get("codes_by_device", {}),
        }
        
        # Adiciona últimos códigos adicionados
        recent_codes = self.database.get_all_codes()
        if recent_codes:
            # Ordena por data de criação (mais recentes primeiro)
            recent_codes.sort(key=lambda x: x.created_at, reverse=True)
            attrs["recent_codes"] = [
                {
                    "id": code.id,
                    "name": code.name,
                    "device": code.device,
                    "command": code.command,
                    "created_at": code.created_at,
                }
                for code in recent_codes[:5]  # Últimos 5 códigos
            ]
        
        return attrs
    
    @property
    def available(self) -> bool:
        """Disponibilidade do sensor"""
        return True  # Base de dados sempre disponível
    
    @property
    def device_info(self):
        """Informações do dispositivo"""
        return self.coordinator.device_info

