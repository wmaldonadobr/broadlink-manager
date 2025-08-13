"""Config flow para o Broadlink IR Manager"""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_TIMEOUT, DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Optional(CONF_HOST): cv.string,
    vol.Optional(CONF_MAC): cv.string,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
})


async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Valida entrada do usuário"""
    try:
        import broadlink
        
        if data.get(CONF_HOST) and data.get(CONF_MAC):
            # Testa conexão com host e MAC específicos
            mac_bytes = bytes.fromhex(data[CONF_MAC].replace(":", ""))
            device = broadlink.rm(
                host=(data[CONF_HOST], 80),
                mac=mac_bytes,
                devtype=0x2737  # RM Mini 3
            )
            
            if not device.auth():
                raise ValueError("Falha na autenticação")
            
            return {
                "title": f"Broadlink RM ({data[CONF_HOST]})",
                "host": data[CONF_HOST],
                "mac": data[CONF_MAC],
            }
        else:
            # Descobre dispositivos automaticamente
            devices = await hass.async_add_executor_job(
                broadlink.discover, 5
            )
            
            if not devices:
                raise ValueError("Nenhum dispositivo encontrado")
            
            device = devices[0]
            if not device.auth():
                raise ValueError("Falha na autenticação")
            
            # Obtém informações do dispositivo
            host = device.host[0]
            mac = ":".join(f"{b:02x}" for b in device.mac)
            
            return {
                "title": f"Broadlink RM ({host})",
                "host": host,
                "mac": mac,
            }
    
    except ImportError:
        raise ValueError("Biblioteca broadlink não encontrada")
    except Exception as e:
        raise ValueError(f"Erro na conexão: {e}")


class BroadlinkIRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow para Broadlink IR Manager"""
    
    VERSION = 1
    
    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manipula passo inicial do usuário"""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Verifica se já existe entrada com mesmo host
                await self.async_set_unique_id(info["mac"])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_HOST: info["host"],
                        CONF_MAC: info["mac"],
                        CONF_TIMEOUT: user_input.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
                    }
                )
            
            except ValueError as e:
                errors["base"] = str(e)
            except Exception:
                _LOGGER.exception("Erro inesperado")
                errors["base"] = "unknown"
        
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/user/broadlink-ir-manager"
            }
        )
    
    async def async_step_discovery(self, discovery_info: Dict[str, Any]) -> FlowResult:
        """Manipula descoberta automática"""
        host = discovery_info.get("host")
        mac = discovery_info.get("mac")
        
        if host and mac:
            await self.async_set_unique_id(mac)
            self._abort_if_unique_id_configured()
            
            self.context["title_placeholders"] = {"host": host}
            
            return await self.async_step_confirm()
        
        return self.async_abort(reason="invalid_discovery")
    
    async def async_step_confirm(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Confirma descoberta automática"""
        if user_input is not None:
            host = self.context["title_placeholders"]["host"]
            mac = self.unique_id
            
            return self.async_create_entry(
                title=f"Broadlink RM ({host})",
                data={
                    CONF_HOST: host,
                    CONF_MAC: mac,
                    CONF_TIMEOUT: DEFAULT_TIMEOUT,
                }
            )
        
        return self.async_show_form(
            step_id="confirm",
            description_placeholders=self.context["title_placeholders"]
        )

