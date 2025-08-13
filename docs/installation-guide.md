# Guia de Instalação - Broadlink IR Manager

## Visão Geral

O Broadlink IR Manager é um sistema completo para Home Assistant que permite:
- Capturar códigos IR com Broadlink RM Mini 3
- Converter códigos de Base64 para Pronto Hex
- Gerenciar base de dados de códigos IR
- Interface dashboard interativa

## Pré-requisitos

### Hardware
- Broadlink RM Mini 3 (ou compatível)
- Home Assistant instalado e funcionando
- Rede Wi-Fi 2.4GHz para o Broadlink

### Software
- Home Assistant 2023.1 ou superior
- Integração Broadlink nativa habilitada
- Acesso ao diretório `custom_components`

## Instalação

### Passo 1: Instalar Componente Customizado

1. Copie a pasta `broadlink_ir_manager` para o diretório `custom_components`:
   ```
   /config/custom_components/broadlink_ir_manager/
   ```

2. Estrutura de arquivos necessária:
   ```
   custom_components/
   └── broadlink_ir_manager/
       ├── __init__.py
       ├── manifest.json
       ├── const.py
       ├── coordinator.py
       ├── sensor.py
       ├── button.py
       ├── config_flow.py
       ├── services.yaml
       ├── ir_converter.py
       └── ir_database.py
   ```

### Passo 2: Instalar Custom Card

1. Copie o arquivo `broadlink-ir-card.js` para o diretório `www`:
   ```
   /config/www/broadlink-ir-card.js
   ```

2. Adicione o recurso ao Lovelace (via UI ou YAML):
   ```yaml
   resources:
     - url: /local/broadlink-ir-card.js
       type: module
   ```

### Passo 3: Configurar Home Assistant

1. Adicione as configurações ao `configuration.yaml`:
   ```yaml
   # Configuração opcional via YAML
   broadlink_ir_manager:
     # host: 192.168.1.100  # Opcional
     # mac: "34:ea:34:xx:xx:xx"  # Opcional
     # timeout: 30  # Opcional
   ```

2. Reinicie o Home Assistant

### Passo 4: Configurar Integração

#### Opção A: Configuração via UI (Recomendado)
1. Vá para **Configurações** > **Dispositivos e Serviços**
2. Clique em **Adicionar Integração**
3. Procure por "Broadlink IR Manager"
4. Siga o assistente de configuração

#### Opção B: Descoberta Automática
1. O sistema tentará descobrir dispositivos Broadlink automaticamente
2. Confirme a configuração quando solicitado

## Configuração do Dashboard

### Opção 1: Custom Card (Recomendado)

Adicione o card ao seu dashboard Lovelace:

```yaml
type: custom:broadlink-ir-card
entity: sensor.broadlink_ir_status
title: "Gerenciador IR"
```

### Opção 2: Dashboard HTML Standalone

1. Copie `broadlink-ir-dashboard.html` para `/config/www/`
2. Acesse via: `http://seu-ha:8123/local/broadlink-ir-dashboard.html`

### Opção 3: Cards Nativos

Use a configuração completa do `lovelace-dashboard.yaml` para um dashboard completo.

## Configuração do Broadlink

### Conectar Dispositivo

1. **Via App Broadlink:**
   - Baixe o app "Broadlink" na loja de aplicativos
   - Configure o RM Mini 3 na sua rede Wi-Fi
   - Anote o IP e MAC address

2. **Descoberta Automática:**
   - O Home Assistant pode descobrir automaticamente
   - Verifique em **Configurações** > **Dispositivos e Serviços**

### Verificar Conectividade

1. Teste a integração nativa do Broadlink primeiro
2. Verifique se o dispositivo responde a comandos
3. Confirme que está na mesma rede do Home Assistant

## Uso Básico

### Capturar Código IR

1. **Via Dashboard:**
   - Clique em "Iniciar Learning"
   - Aponte o controle remoto para o Broadlink
   - Pressione o botão desejado
   - Aguarde confirmação

2. **Via Serviços:**
   ```yaml
   service: broadlink_ir_manager.start_learning
   data:
     entity_id: sensor.broadlink_ir_status
     timeout: 30
   ```

### Salvar Código

1. **Via Dashboard:**
   - Preencha nome, dispositivo e comando
   - Clique em "Salvar na Base de Dados"

2. **Via Serviços:**
   ```yaml
   service: broadlink_ir_manager.save_code
   data:
     name: "Power"
     device: "TV Sala"
     command: "power"
     base64_code: "JgAcAB0dHB44..."
     notes: "Ligar/desligar TV"
   ```

### Converter Códigos

Os códigos são automaticamente convertidos de Base64 para Pronto Hex:
- **Base64:** Formato nativo do Broadlink
- **Pronto Hex:** Formato universal (0000 xxxx...)

## Serviços Disponíveis

### broadlink_ir_manager.start_learning
Inicia modo de aprendizado de códigos IR.

**Parâmetros:**
- `entity_id`: ID da entidade sensor
- `timeout`: Tempo limite em segundos (padrão: 30)

### broadlink_ir_manager.stop_learning
Para o modo de aprendizado.

### broadlink_ir_manager.get_learned_code
Obtém o último código IR aprendido.

### broadlink_ir_manager.convert_code
Converte código Base64 para Pronto Hex.

**Parâmetros:**
- `base64_code`: Código em formato Base64

### broadlink_ir_manager.save_code
Salva código na base de dados.

**Parâmetros:**
- `name`: Nome descritivo
- `device`: Nome do dispositivo
- `command`: Nome do comando
- `base64_code`: Código Base64
- `notes`: Notas opcionais

### broadlink_ir_manager.delete_code
Remove código da base de dados.

**Parâmetros:**
- `code_id`: ID do código a ser removido

### broadlink_ir_manager.list_codes
Lista todos os códigos salvos.

## Entidades Criadas

### Sensores
- `sensor.broadlink_ir_status`: Status do sistema
- `sensor.broadlink_ir_last_code`: Último código capturado
- `sensor.broadlink_ir_database`: Estatísticas da base de dados

### Botões
- `button.start_ir_learning`: Iniciar learning
- `button.stop_ir_learning`: Parar learning
- `button.get_learned_code`: Obter código

## Automações Exemplo

### Notificar Código Capturado
```yaml
automation:
  - alias: "Notificar código IR capturado"
    trigger:
      - platform: event
        event_type: broadlink_ir_manager_code_learned
    action:
      - service: notify.mobile_app_seu_telefone
        data:
          title: "Código IR Capturado"
          message: "Novo código IR foi capturado!"
```

### Auto-salvar Códigos
```yaml
automation:
  - alias: "Auto-salvar códigos TV"
    trigger:
      - platform: state
        entity_id: sensor.broadlink_ir_last_code
        attribute: base64_code
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.attributes.base64_code != None }}"
    action:
      - service: broadlink_ir_manager.save_code
        data:
          name: "Auto-{{ now().strftime('%H%M%S') }}"
          device: "TV Auto"
          command: "auto_captured"
          base64_code: "{{ trigger.to_state.attributes.base64_code }}"
          notes: "Código capturado automaticamente"
```

## Solução de Problemas

### Dispositivo Não Encontrado
1. Verifique se o Broadlink está na mesma rede
2. Confirme que a integração nativa funciona
3. Reinicie o Home Assistant
4. Verifique logs em **Configurações** > **Sistema** > **Logs**

### Códigos Não Capturam
1. Verifique se o LED do Broadlink pisca durante learning
2. Aproxime o controle remoto do dispositivo
3. Teste com diferentes controles remotos
4. Verifique se a frequência é suportada (38kHz padrão)

### Custom Card Não Aparece
1. Verifique se o arquivo está em `/config/www/`
2. Confirme que o recurso foi adicionado ao Lovelace
3. Limpe cache do navegador
4. Verifique console do navegador para erros

### Erros de Conversão
1. Verifique se o código Base64 está completo
2. Confirme que é um código IR válido do Broadlink
3. Teste com códigos conhecidos primeiro

## Backup e Restauração

### Backup da Base de Dados
```yaml
service: broadlink_ir_manager.list_codes
```
Os códigos são salvos em `/config/custom_components/broadlink_ir_manager/ir_codes.json`

### Restauração
1. Copie o arquivo `ir_codes.json` de volta ao diretório
2. Reinicie o Home Assistant
3. Verifique se os códigos aparecem no dashboard

## Atualizações

### Atualizar Componente
1. Substitua os arquivos na pasta `custom_components/broadlink_ir_manager/`
2. Reinicie o Home Assistant
3. Verifique se não há erros nos logs

### Atualizar Custom Card
1. Substitua o arquivo `broadlink-ir-card.js` em `/config/www/`
2. Limpe cache do navegador
3. Recarregue o dashboard

## Suporte

Para suporte e relatórios de bugs:
1. Verifique os logs do Home Assistant
2. Teste com a integração Broadlink nativa primeiro
3. Documente passos para reproduzir problemas
4. Inclua versões do HA e do componente

