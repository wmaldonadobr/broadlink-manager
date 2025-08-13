"""Constantes para o Broadlink IR Manager"""

from homeassistant.const import Platform

# Domínio do componente
DOMAIN = "broadlink_ir_manager"

# Plataformas suportadas
PLATFORMS = [Platform.SENSOR, Platform.BUTTON]

# Serviços
SERVICE_START_LEARNING = "start_learning"
SERVICE_STOP_LEARNING = "stop_learning"
SERVICE_GET_LEARNED_CODE = "get_learned_code"
SERVICE_CONVERT_CODE = "convert_code"
SERVICE_SAVE_CODE = "save_code"
SERVICE_DELETE_CODE = "delete_code"
SERVICE_LIST_CODES = "list_codes"

# Configuração
CONF_HOST = "host"
CONF_MAC = "mac"
CONF_TIMEOUT = "timeout"

# Padrões
DEFAULT_TIMEOUT = 30
DEFAULT_SCAN_INTERVAL = 30

# Estados
STATE_IDLE = "idle"
STATE_LEARNING = "learning"
STATE_CODE_RECEIVED = "code_received"

# Atributos
ATTR_BASE64_CODE = "base64_code"
ATTR_PRONTO_CODE = "pronto_code"
ATTR_FREQUENCY = "frequency"
ATTR_LEARNING_TIMEOUT = "learning_timeout"
ATTR_LAST_CODE = "last_code"
ATTR_CODES_COUNT = "codes_count"

