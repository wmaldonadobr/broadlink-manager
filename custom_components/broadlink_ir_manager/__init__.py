"""
Broadlink IR Manager - Componente customizado para Home Assistant
Permite capturar e converter códigos IR do Broadlink RM Mini 3
"""

import logging
import asyncio
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_START_LEARNING,
    SERVICE_STOP_LEARNING,
    SERVICE_GET_LEARNED_CODE,
    SERVICE_CONVERT_CODE,
    SERVICE_SAVE_CODE,
    SERVICE_DELETE_CODE,
    SERVICE_LIST_CODES,
    CONF_HOST,
    CONF_MAC,
    CONF_TIMEOUT,
    DEFAULT_TIMEOUT,
)
from .coordinator import BroadlinkIRCoordinator
from .ir_converter import IRConverter
from .ir_database import IRDatabase

_LOGGER = logging.getLogger(__name__)

# Schema de configuração via YAML (opcional)
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_HOST): cv.string,
                vol.Optional(CONF_MAC): cv.string,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

# Schemas dos serviços
SERVICE_START_LEARNING_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Optional("timeout", default=30): cv.positive_int,
})

SERVICE_CONVERT_CODE_SCHEMA = vol.Schema({
    vol.Required("base64_code"): cv.string,
})

SERVICE_SAVE_CODE_SCHEMA = vol.Schema({
    vol.Required("name"): cv.string,
    vol.Required("device"): cv.string,
    vol.Required("command"): cv.string,
    vol.Required("base64_code"): cv.string,
    vol.Optional("notes", default=""): cv.string,
})

SERVICE_DELETE_CODE_SCHEMA = vol.Schema({
    vol.Required("code_id"): cv.string,
})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Configuração via YAML (opcional)"""
    hass.data.setdefault(DOMAIN, {})
    
    # Inicializa conversor e base de dados
    hass.data[DOMAIN]["converter"] = IRConverter()
    hass.data[DOMAIN]["database"] = IRDatabase(
        hass.config.path("custom_components", DOMAIN, "ir_codes.json")
    )
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configuração via config flow"""
    hass.data.setdefault(DOMAIN, {})
    
    # Cria coordinator
    coordinator = BroadlinkIRCoordinator(hass, entry)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        raise
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Configura plataformas
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Registra serviços
    await async_setup_services(hass)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove entrada de configuração"""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_setup_services(hass: HomeAssistant) -> None:
    """Registra serviços do componente"""
    
    async def start_learning(call: ServiceCall) -> None:
        """Inicia modo learning"""
        entity_id = call.data["entity_id"]
        timeout = call.data.get("timeout", 30)
        
        # Encontra o coordinator
        coordinator = None
        for coord in hass.data[DOMAIN].values():
            if isinstance(coord, BroadlinkIRCoordinator):
                coordinator = coord
                break
        
        if coordinator:
            await coordinator.start_learning(timeout)
            hass.bus.async_fire(f"{DOMAIN}_learning_started", {
                "entity_id": entity_id,
                "timeout": timeout
            })
    
    async def stop_learning(call: ServiceCall) -> None:
        """Para modo learning"""
        # Encontra o coordinator
        coordinator = None
        for coord in hass.data[DOMAIN].values():
            if isinstance(coord, BroadlinkIRCoordinator):
                coordinator = coord
                break
        
        if coordinator:
            await coordinator.stop_learning()
            hass.bus.async_fire(f"{DOMAIN}_learning_stopped", {})
    
    async def get_learned_code(call: ServiceCall) -> None:
        """Obtém código aprendido"""
        # Encontra o coordinator
        coordinator = None
        for coord in hass.data[DOMAIN].values():
            if isinstance(coord, BroadlinkIRCoordinator):
                coordinator = coord
                break
        
        if coordinator:
            code = await coordinator.get_learned_code()
            if code:
                converter = hass.data[DOMAIN]["converter"]
                pronto_code = converter.broadlink_to_pronto(code)
                
                hass.bus.async_fire(f"{DOMAIN}_code_learned", {
                    "base64_code": code,
                    "pronto_code": pronto_code
                })
    
    async def convert_code(call: ServiceCall) -> None:
        """Converte código Base64 para Pronto"""
        base64_code = call.data["base64_code"]
        converter = hass.data[DOMAIN]["converter"]
        
        try:
            pronto_code = converter.broadlink_to_pronto(base64_code)
            frequency = converter.get_frequency_from_pronto(pronto_code)
            
            hass.bus.async_fire(f"{DOMAIN}_code_converted", {
                "base64_code": base64_code,
                "pronto_code": pronto_code,
                "frequency": frequency
            })
        except Exception as e:
            _LOGGER.error(f"Erro na conversão: {e}")
    
    async def save_code(call: ServiceCall) -> None:
        """Salva código na base de dados"""
        database = hass.data[DOMAIN]["database"]
        
        try:
            code_id = database.add_code(
                name=call.data["name"],
                device=call.data["device"],
                command=call.data["command"],
                base64_code=call.data["base64_code"],
                notes=call.data.get("notes", "")
            )
            
            hass.bus.async_fire(f"{DOMAIN}_code_saved", {
                "code_id": code_id,
                "name": call.data["name"]
            })
        except Exception as e:
            _LOGGER.error(f"Erro ao salvar código: {e}")
    
    async def delete_code(call: ServiceCall) -> None:
        """Remove código da base de dados"""
        database = hass.data[DOMAIN]["database"]
        code_id = call.data["code_id"]
        
        if database.delete_code(code_id):
            hass.bus.async_fire(f"{DOMAIN}_code_deleted", {
                "code_id": code_id
            })
    
    async def list_codes(call: ServiceCall) -> None:
        """Lista códigos da base de dados"""
        database = hass.data[DOMAIN]["database"]
        codes = database.get_all_codes()
        
        codes_data = [code.to_dict() for code in codes]
        
        hass.bus.async_fire(f"{DOMAIN}_codes_listed", {
            "codes": codes_data,
            "total": len(codes_data)
        })
    
    # Registra os serviços
    hass.services.async_register(
        DOMAIN, SERVICE_START_LEARNING, start_learning, SERVICE_START_LEARNING_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_STOP_LEARNING, stop_learning
    )
    hass.services.async_register(
        DOMAIN, SERVICE_GET_LEARNED_CODE, get_learned_code
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CONVERT_CODE, convert_code, SERVICE_CONVERT_CODE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SAVE_CODE, save_code, SERVICE_SAVE_CODE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DELETE_CODE, delete_code, SERVICE_DELETE_CODE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_LIST_CODES, list_codes
    )

