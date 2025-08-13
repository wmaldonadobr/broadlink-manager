"""Coordinator para o Broadlink IR Manager"""

import asyncio
import logging
from datetime import timedelta
from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    STATE_IDLE,
    STATE_LEARNING,
    STATE_CODE_RECEIVED,
    CONF_HOST,
    CONF_MAC,
    CONF_TIMEOUT,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class BroadlinkIRCoordinator(DataUpdateCoordinator):
    """Coordinator para gerenciar dados do Broadlink IR Manager"""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Inicializa o coordinator"""
        self.entry = entry
        self.host = entry.data.get(CONF_HOST)
        self.mac = entry.data.get(CONF_MAC)
        self.timeout = entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
        
        self._broadlink_device = None
        self._state = STATE_IDLE
        self._learning_task = None
        self._last_learned_code = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
    
    async def _async_update_data(self):
        """Atualiza dados do coordinator"""
        try:
            # Conecta ao dispositivo Broadlink se necessário
            if self._broadlink_device is None:
                await self._async_setup_device()
            
            # Retorna estado atual
            return {
                "state": self._state,
                "last_code": self._last_learned_code,
                "device_connected": self._broadlink_device is not None,
                "host": self.host,
                "mac": self.mac,
            }
            
        except Exception as err:
            raise UpdateFailed(f"Erro ao atualizar dados: {err}")
    
    async def _async_setup_device(self):
        """Configura conexão com dispositivo Broadlink"""
        try:
            import broadlink
            
            if self.host and self.mac:
                # Conecta usando host e MAC específicos
                mac_bytes = bytes.fromhex(self.mac.replace(":", ""))
                self._broadlink_device = broadlink.rm(
                    host=(self.host, 80),
                    mac=mac_bytes,
                    devtype=0x2737  # RM Mini 3
                )
            else:
                # Descobre dispositivos automaticamente
                devices = broadlink.discover(timeout=5)
                if devices:
                    self._broadlink_device = devices[0]
                else:
                    raise ConfigEntryNotReady("Nenhum dispositivo Broadlink encontrado")
            
            # Autentica com o dispositivo
            if not self._broadlink_device.auth():
                raise ConfigEntryNotReady("Falha na autenticação com dispositivo Broadlink")
            
            _LOGGER.info("Conectado ao dispositivo Broadlink")
            
        except ImportError:
            raise ConfigEntryNotReady("Biblioteca broadlink não encontrada")
        except Exception as err:
            raise ConfigEntryNotReady(f"Erro ao conectar com Broadlink: {err}")
    
    async def start_learning(self, timeout: int = None) -> bool:
        """Inicia modo learning"""
        if self._state == STATE_LEARNING:
            _LOGGER.warning("Modo learning já está ativo")
            return False
        
        if self._broadlink_device is None:
            await self._async_setup_device()
        
        try:
            # Inicia learning no dispositivo
            await self.hass.async_add_executor_job(
                self._broadlink_device.enter_learning
            )
            
            self._state = STATE_LEARNING
            self._last_learned_code = None
            
            # Inicia task para monitorar learning
            timeout = timeout or self.timeout
            self._learning_task = self.hass.async_create_task(
                self._learning_monitor(timeout)
            )
            
            _LOGGER.info(f"Modo learning iniciado (timeout: {timeout}s)")
            await self.async_request_refresh()
            return True
            
        except Exception as err:
            _LOGGER.error(f"Erro ao iniciar learning: {err}")
            self._state = STATE_IDLE
            return False
    
    async def stop_learning(self) -> bool:
        """Para modo learning"""
        if self._learning_task:
            self._learning_task.cancel()
            self._learning_task = None
        
        self._state = STATE_IDLE
        _LOGGER.info("Modo learning parado")
        await self.async_request_refresh()
        return True
    
    async def get_learned_code(self) -> Optional[str]:
        """Obtém código aprendido"""
        if self._broadlink_device is None:
            return None
        
        try:
            # Verifica se há código disponível
            code_data = await self.hass.async_add_executor_job(
                self._broadlink_device.check_data
            )
            
            if code_data:
                # Converte para Base64
                import base64
                base64_code = base64.b64encode(code_data).decode('ascii')
                self._last_learned_code = base64_code
                self._state = STATE_CODE_RECEIVED
                await self.async_request_refresh()
                return base64_code
            
            return None
            
        except Exception as err:
            _LOGGER.error(f"Erro ao obter código: {err}")
            return None
    
    async def _learning_monitor(self, timeout: int):
        """Monitora processo de learning"""
        try:
            # Aguarda por código ou timeout
            for _ in range(timeout):
                await asyncio.sleep(1)
                
                code = await self.get_learned_code()
                if code:
                    _LOGGER.info("Código IR capturado com sucesso")
                    return
            
            # Timeout atingido
            _LOGGER.warning("Timeout do modo learning atingido")
            self._state = STATE_IDLE
            await self.async_request_refresh()
            
        except asyncio.CancelledError:
            _LOGGER.info("Monitoramento de learning cancelado")
        except Exception as err:
            _LOGGER.error(f"Erro no monitoramento de learning: {err}")
            self._state = STATE_IDLE
            await self.async_request_refresh()
    
    @property
    def device_info(self):
        """Informações do dispositivo"""
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": "Broadlink IR Manager",
            "manufacturer": "Broadlink",
            "model": "RM Mini 3",
            "sw_version": "1.0.0",
        }
    
    @property
    def state(self) -> str:
        """Estado atual"""
        return self._state
    
    @property
    def last_learned_code(self) -> Optional[str]:
        """Último código aprendido"""
        return self._last_learned_code
    
    @property
    def is_learning(self) -> bool:
        """Verifica se está em modo learning"""
        return self._state == STATE_LEARNING

