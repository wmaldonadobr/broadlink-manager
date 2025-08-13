"""Botões para o Broadlink IR Manager"""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATE_LEARNING
from .coordinator import BroadlinkIRCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura botões"""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        BroadlinkIRLearningButton(coordinator),
        BroadlinkIRStopLearningButton(coordinator),
        BroadlinkIRGetCodeButton(coordinator),
    ]
    
    async_add_entities(entities)


class BroadlinkIRLearningButton(CoordinatorEntity, ButtonEntity):
    """Botão para iniciar modo learning"""
    
    def __init__(self, coordinator: BroadlinkIRCoordinator) -> None:
        """Inicializa botão de learning"""
        super().__init__(coordinator)
        self._attr_name = "Start IR Learning"
        self._attr_unique_id = f"{DOMAIN}_start_learning"
        self._attr_icon = "mdi:play-circle"
    
    async def async_press(self) -> None:
        """Executa ação do botão"""
        if self.coordinator.state == STATE_LEARNING:
            _LOGGER.warning("Modo learning já está ativo")
            return
        
        success = await self.coordinator.start_learning()
        if success:
            _LOGGER.info("Modo learning iniciado via botão")
        else:
            _LOGGER.error("Falha ao iniciar modo learning")
    
    @property
    def available(self) -> bool:
        """Disponibilidade do botão"""
        return (
            self.coordinator.last_update_success and
            self.coordinator.state != STATE_LEARNING
        )
    
    @property
    def device_info(self):
        """Informações do dispositivo"""
        return self.coordinator.device_info


class BroadlinkIRStopLearningButton(CoordinatorEntity, ButtonEntity):
    """Botão para parar modo learning"""
    
    def __init__(self, coordinator: BroadlinkIRCoordinator) -> None:
        """Inicializa botão de parar learning"""
        super().__init__(coordinator)
        self._attr_name = "Stop IR Learning"
        self._attr_unique_id = f"{DOMAIN}_stop_learning"
        self._attr_icon = "mdi:stop-circle"
    
    async def async_press(self) -> None:
        """Executa ação do botão"""
        success = await self.coordinator.stop_learning()
        if success:
            _LOGGER.info("Modo learning parado via botão")
        else:
            _LOGGER.error("Falha ao parar modo learning")
    
    @property
    def available(self) -> bool:
        """Disponibilidade do botão"""
        return (
            self.coordinator.last_update_success and
            self.coordinator.state == STATE_LEARNING
        )
    
    @property
    def device_info(self):
        """Informações do dispositivo"""
        return self.coordinator.device_info


class BroadlinkIRGetCodeButton(CoordinatorEntity, ButtonEntity):
    """Botão para obter código aprendido"""
    
    def __init__(self, coordinator: BroadlinkIRCoordinator) -> None:
        """Inicializa botão de obter código"""
        super().__init__(coordinator)
        self._attr_name = "Get Learned Code"
        self._attr_unique_id = f"{DOMAIN}_get_code"
        self._attr_icon = "mdi:download"
    
    async def async_press(self) -> None:
        """Executa ação do botão"""
        code = await self.coordinator.get_learned_code()
        if code:
            _LOGGER.info(f"Código obtido via botão: {code[:20]}...")
        else:
            _LOGGER.warning("Nenhum código disponível")
    
    @property
    def available(self) -> bool:
        """Disponibilidade do botão"""
        return self.coordinator.last_update_success
    
    @property
    def device_info(self):
        """Informações do dispositivo"""
        return self.coordinator.device_info

