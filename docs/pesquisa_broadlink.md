
# Pesquisa - Integração Broadlink com Home Assistant

## Documentação Oficial Home Assistant

### Dispositivos Suportados
- Universal Remotes: RM mini, RM mini 3, RM pro, RM pro+, RM plus, RM4 mini, RM4 pro, RM4C mini, RM4C pro, RM4 TV mate

### Funcionalidades Principais

#### Aprendizado de Códigos IR
- Serviço: `remote.learn_command`
- Parâmetros:
  - `entity_id`: ID do remote
  - `device`: Nome do dispositivo
  - `command`: Nome do comando a ser aprendido
  - `command_type`: "rf" para códigos RF (opcional)
  - `alternative`: true para aprender código alternativo

#### Envio de Comandos
- Serviço: `remote.send_command`
- Suporte a códigos Base64 com prefixo `b64:`
- Parâmetros:
  - `entity_id`: ID do remote
  - `command`: Nomes dos comandos ou códigos base64
  - `device`: Nome do dispositivo (opcional para base64)
  - `num_repeats`: Número de repetições
  - `delay_secs`: Intervalo entre envios

#### Armazenamento de Códigos
- Local: `/config/.storage/broadlink_remote_MACADDRESS_codes`
- Formato: JSON
- Contém códigos aprendidos organizados por dispositivo

### Processo de Aprendizado
1. Chamar `remote.learn_command`
2. LED do Broadlink pisca
3. Apontar controle remoto para o Broadlink
4. Pressionar botão desejado
5. Código é armazenado automaticamente

### Códigos Base64
- Formato usado pelo Broadlink para armazenar códigos IR/RF
- Podem ser enviados diretamente com prefixo `b64:`
- Exemplo: `b64:JgAcAB0dHB44HhweGx4cHR06HB0cHhwdHB8bHhwADQUAAAAAAAAAAAAAAAA=`



## Formato Pronto Hex

### Estrutura do Formato Pronto
- Códigos consistem de palavras hexadecimais de 4 letras
- Organizados em conjuntos de 11, 21 e outras quantidades
- Formato mais comum para sinais IR de controles remotos

### Preâmbulo Pronto (4 palavras hexadecimais)
Exemplo: `0000 0073 0000 0021`

1. **Primeira palavra (0000)**: Indica início do sinal IR
2. **Segunda palavra (0073)**: Especifica frequência portadora (0073 = 38kHz)
3. **Terceira palavra (0000)**: Comprimento do burst inicial (ação única)
4. **Quarta palavra (0021)**: Comprimento do burst de repetição (manter pressionado)

### Conversão HEX para Decimal
Fórmula: `W(4096) + X(256) + Y(16) + Z = Código IR Decimal`
Para código hex = WXYZ

## Conversor Smart IR (GitHub)

### Funcionalidades Identificadas
- Suporte a múltiplos controladores: Broadlink, Xiaomi, LOOKin, ESPHome
- Formatos de codificação: Base64, Hex, Pronto, Raw
- Conversão bidirecional entre formatos
- Biblioteca `irgen` para geração de códigos

### Funções Relevantes
```python
def convert_from_raw(raw):
    if args.encoding == ENC_PRONTO:
        return " ".join(irgen.gen_pronto_from_raw([], raw, base=0x73))
    if args.controller == BROADLINK_CONTROLLER:
        if args.encoding == ENC_BASE64:
            return bytes(irgen.gen_broadlink_base64_from_raw(raw)).decode('ascii')
```

### Estrutura de Dados Broadlink
- Primeiro byte: 0x26 (indica IR)
- Bytes 2-4: Comprimento dos dados
- Bytes finais: 0x0d, 0x05 (terminadores)

## Requisitos Técnicos Identificados

### Para Conversão Base64 → Pronto Hex
1. Decodificar Base64 para bytes
2. Extrair dados IR do formato Broadlink
3. Converter para formato raw (timings)
4. Gerar código Pronto Hex com frequência 38kHz

### Bibliotecas Necessárias
- `base64`: Para decodificação
- `irgen`: Para conversão entre formatos (ou implementação própria)
- `construct`: Para parsing de estruturas binárias


## Desenvolvimento de Componentes Customizados

### Estrutura Básica de Integração
- **Arquivo principal**: `__init__.py` no diretório do componente
- **Manifest**: `manifest.json` com metadados da integração
- **Domínio**: Constante DOMAIN que identifica a integração
- **Setup**: Função `setup()` ou `async_setup()` para inicialização

### Estrutura Mínima
```python
DOMAIN = "broadlink_ir_manager"

async def async_setup(hass, config):
    # Inicialização da integração
    return True
```

### Manifest.json
```json
{
  "domain": "broadlink_ir_manager",
  "name": "Broadlink IR Manager",
  "version": "1.0.0",
  "dependencies": ["broadlink"],
  "requirements": []
}
```

## Desenvolvimento de Custom Cards

### Estrutura Básica
- **Custom Element**: Classe que estende HTMLElement ou LitElement
- **Métodos obrigatórios**: `setConfig()`, `set hass()`
- **Métodos opcionais**: `getCardSize()`, `getGridOptions()`

### Exemplo de Custom Card
```javascript
class BroadlinkIRCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
  }
  
  set hass(hass) {
    // Atualizar conteúdo quando estado muda
  }
  
  getCardSize() {
    return 3; // Altura em unidades de 50px
  }
}

customElements.define("broadlink-ir-card", BroadlinkIRCard);
```

### Registro de Recursos
- Arquivo JavaScript em `/config/www/`
- Registro como módulo no dashboard
- URL: `/local/nome-do-arquivo.js`

## Requisitos para o Sistema

### Componente Customizado
1. **Sensor**: Para status do modo learning
2. **Serviço**: Para ativar modo learning
3. **Armazenamento**: Para códigos capturados
4. **Conversão**: Base64 para Pronto Hex

### Custom Card
1. **Botão Learning**: Ativar/desativar modo
2. **Display**: Mostrar códigos capturados
3. **Conversão**: Interface para conversão
4. **Histórico**: Lista de códigos salvos

