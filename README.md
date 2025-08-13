# 🎛️ Broadlink IR Manager para Home Assistant

Sistema completo para captura, conversão e gerenciamento de códigos infravermelhos usando Broadlink RM Mini 3 com Home Assistant.

## ✨ Características

- 📡 **Captura de códigos IR** com Broadlink RM Mini 3
- 🔄 **Conversão automática** de Base64 para Pronto Hex
- 💾 **Base de dados integrada** para gerenciar códigos
- 🎨 **Interface dashboard** moderna e responsiva
- 🏠 **Integração nativa** com Home Assistant
- 🔧 **Componente customizado** completo
- 📱 **Custom card** para Lovelace
- 🌐 **Dashboard HTML** standalone

## 🚀 Funcionalidades

### Captura de Códigos
- Modo learning com timeout configurável
- Detecção automática de códigos IR
- Suporte a múltiplas frequências
- Feedback visual em tempo real

### Conversão de Formatos
- **Base64**: Formato nativo do Broadlink
- **Pronto Hex**: Formato universal (0000 xxxx...)
- Conversão automática e validação
- Preservação da frequência original

### Gerenciamento de Base de Dados
- Armazenamento local de códigos
- Organização por dispositivo e comando
- Busca e filtragem avançada
- Exportação e importação de dados

### Interface de Usuário
- Custom card para Lovelace
- Dashboard HTML standalone
- Controles intuitivos
- Exibição de códigos em tempo real

## 📁 Estrutura do Projeto

```
broadlink_ir_system/
├── custom_components/
│   └── broadlink_ir_manager/          # Componente customizado
│       ├── __init__.py                # Inicialização da integração
│       ├── manifest.json              # Metadados do componente
│       ├── const.py                   # Constantes
│       ├── coordinator.py             # Coordenador de dados
│       ├── sensor.py                  # Sensores
│       ├── button.py                  # Botões
│       ├── config_flow.py             # Fluxo de configuração
│       ├── services.yaml              # Definições de serviços
│       ├── ir_converter.py            # Conversor de códigos IR
│       └── ir_database.py             # Gerenciador de base de dados
├── www/
│   ├── broadlink-ir-card.js           # Custom card para Lovelace
│   └── broadlink-ir-dashboard.html    # Dashboard HTML standalone
├── config_examples/
│   ├── configuration.yaml             # Configuração exemplo
│   └── lovelace-dashboard.yaml        # Dashboard Lovelace exemplo
├── docs/
│   ├── installation-guide.md          # Guia de instalação
│   └── pesquisa_broadlink.md          # Documentação técnica
└── README.md                          # Este arquivo
```

## 🛠️ Instalação Rápida

### 1. Instalar Componente Customizado
```bash
# Copie a pasta para custom_components
cp -r custom_components/broadlink_ir_manager /config/custom_components/
```

### 2. Instalar Custom Card
```bash
# Copie o arquivo para www
cp www/broadlink-ir-card.js /config/www/
```

### 3. Configurar Lovelace
```yaml
# Adicione ao resources
resources:
  - url: /local/broadlink-ir-card.js
    type: module
```

### 4. Reiniciar Home Assistant
```bash
# Reinicie o Home Assistant
sudo systemctl restart home-assistant
```

### 5. Configurar Integração
1. Vá para **Configurações** > **Dispositivos e Serviços**
2. Clique em **Adicionar Integração**
3. Procure por "Broadlink IR Manager"
4. Siga o assistente de configuração

## 🎯 Uso Básico

### Capturar Código IR
1. Clique em "Iniciar Learning" no dashboard
2. Aponte o controle remoto para o Broadlink
3. Pressione o botão desejado
4. Aguarde a confirmação de captura

### Salvar Código
1. Preencha nome, dispositivo e comando
2. Clique em "Salvar na Base de Dados"
3. O código fica disponível para uso

### Usar Códigos
- **Base64**: Para enviar via Broadlink
- **Pronto Hex**: Para outros sistemas universais

## 🔧 Serviços Disponíveis

| Serviço | Descrição |
|---------|-----------|
| `start_learning` | Inicia modo de aprendizado |
| `stop_learning` | Para modo de aprendizado |
| `get_learned_code` | Obtém último código capturado |
| `convert_code` | Converte Base64 para Pronto Hex |
| `save_code` | Salva código na base de dados |
| `delete_code` | Remove código da base de dados |
| `list_codes` | Lista todos os códigos salvos |

## 📊 Entidades Criadas

### Sensores
- `sensor.broadlink_ir_status`: Status do sistema
- `sensor.broadlink_ir_last_code`: Último código capturado
- `sensor.broadlink_ir_database`: Estatísticas da base de dados

### Botões
- `button.start_ir_learning`: Iniciar learning
- `button.stop_ir_learning`: Parar learning
- `button.get_learned_code`: Obter código

## 🎨 Interfaces Disponíveis

### 1. Custom Card (Recomendado)
```yaml
type: custom:broadlink-ir-card
entity: sensor.broadlink_ir_status
title: "Gerenciador IR"
```

### 2. Dashboard HTML Standalone
Acesse: `http://seu-ha:8123/local/broadlink-ir-dashboard.html`

### 3. Cards Nativos
Use a configuração completa do `lovelace-dashboard.yaml`

## 🔍 Formatos Suportados

### Base64 (Broadlink)
```
JgAcAB0dHB44HhweGx4cHR06HB0cHhwdHB8bHhwADQUAAAAAAAAAAAAAAAA=
```

### Pronto Hex (Universal)
```
0000 0073 0000 000D 2533 2679 269D 2679 2678 2532 4A41 2532 2679 2532 27C0 2678 0024
```

## 🛡️ Requisitos

### Hardware
- Broadlink RM Mini 3 (ou compatível)
- Home Assistant instalado
- Rede Wi-Fi 2.4GHz

### Software
- Home Assistant 2023.1+
- Integração Broadlink nativa
- Navegador moderno (para custom card)

## 📚 Documentação

- [📖 Guia de Instalação Completo](docs/installation-guide.md)
- [🔬 Documentação Técnica](docs/pesquisa_broadlink.md)
- [⚙️ Exemplos de Configuração](config_examples/)

## 🤝 Contribuição

Este sistema foi desenvolvido como uma solução completa para gerenciamento de códigos IR. Contribuições são bem-vindas!

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📝 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🆘 Suporte

### Problemas Comuns
- **Dispositivo não encontrado**: Verifique rede e integração nativa
- **Códigos não capturam**: Aproxime controle e verifique LED
- **Custom card não aparece**: Verifique cache e recursos

### Logs e Debug
```yaml
logger:
  default: info
  logs:
    custom_components.broadlink_ir_manager: debug
```

## 🎉 Agradecimentos

- Comunidade Home Assistant
- Desenvolvedores da integração Broadlink
- Contribuidores do projeto

---

**Desenvolvido com ❤️ para a comunidade Home Assistant**

> 💡 **Dica**: Para melhor experiência, use o custom card no Lovelace. Para acesso rápido, use o dashboard HTML standalone.

