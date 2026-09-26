# Itens & Sistema de Criação (D&D 5e)

[English](README.md) | [Português (Brasil)](README.pt-BR.md)

[![Foundry VTT](https://img.shields.io/badge/Foundry%20VTT-v12%20|%20v14-orange.svg)](https://foundryvtt.com/)
[![System](https://img.shields.io/badge/System-dnd5e%20v3.0%2B-blue.svg)](https://github.com/foundryvtt/dnd5e)
[![Version](https://img.shields.io/badge/version-v1.2.0-blue.svg)](module.json)
[![Tests](https://img.shields.io/badge/tests-26%20passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Módulo completo de criação de itens (*crafting*), alquimia, encantamento, forragem e colheita de criaturas (*harvesting*) para o **Foundry Virtual Tabletop (V12 a V14+)** e sistema **D&D 5e (v3.0+ e v4.0+)**, implementando com fidelidade as consagradas regras do **Kibbles' Crafting Guide** com fichas modernas em ApplicationV2 e compêndios totalmente bilíngues.

---

## Destaques

- **Oficina de Criação Interativa (ApplicationV2):** Interface moderna e responsiva acessada pela ficha do personagem ou barra de ferramentas, com busca em tempo real e preservação de foco.
- **Colheita de Criaturas Automatizada:** Detecção automática do Nível de Desafio (ND/CR) e tipo de criatura (Dragões, Feras, Construtos, Aberrações, Mortos-vivos, Celestiais) com testes de perícia para salvamento.
- **Central de Forragem e Desmanche:** Tabelas de forragem por bioma (Floresta, Montanha, Pântano, Deserto, Subterrâneo, Costeiro, Planícies), desmanche de itens e integração com a Caixa do Caos Quântico.
- **Compêndios Bilíngues e Completos:** Dados sincronizados em português (`pt-BR`) e inglês (`en`) abrangendo 478 receitas, 478 itens finais, 92 materiais, 15 tabelas roláveis e manuais de regras.
- **Modernizado para Foundry V12-V14:** Construção nativa de `ChatMessage` via propriedades `style` com fallback retrocompatível sem emissão de avisos de depreciação.
- **Suíte de Testes Automatizados:** Bateria de testes unitários com 26 testes cobrindo regras de domínio, estados de UI, integridade de ícones e paridade de compêndios.

---

## Tabelas de Domínio e Recursos

### Profissões de Criação

| Profissão | Ferramenta / Perícia Requerida | Atributos-Chave | Produtos Principais |
| :--- | :--- | :--- | :--- |
| **Alquimia** | Suprimentos de Alquimista / Kit de Herbalismo | INT / SAB | Poções, elixires, ácidos, fogo alquímico e óleos |
| **Ferraria** | Ferramentas de Ferreiro | FOR / CON | Armas de metal, armaduras pesadas, escudos e reforços |
| **Encantamento** | Perícia Arcanismo | INT / CAR | Sintonização de itens mágicos, infusão de essências e relíquias |
| **Trabalho em Couro** | Ferramentas de Coureiro | DES / FOR | Armaduras de couro e pele, aljavas, botas e bainhas |
| **Venefício** | Kit de Envenenador | INT / DES | Toxinas de contato, ingestão, inalação e ferimento |
| **Escriba de Pergaminhos** | Suprimentos de Calígrafo | INT / SAB | Pergaminhos de magia, rituais e pergaminhos arcanos |
| **Engenharia** | Ferramentas de Engenhoqueiro | INT / DES | Mecanismos de corda, armadilhas, autômatos e engenhocas |
| **Entalhe de Varinhas** | Ferramentas de Entalhador | INT / SAB | Varinhas arcanas, cajados e focos de madeira |
| **Culinária** | Utensílios de Cozinheiro | SAB / CON | Rações, banquetes revigorantes e refeições de vitalidade |

### Compêndios Bilíngues

| Chave do Compêndio | Tipo de Documento | Registros | Descrição |
| :--- | :--- | :---: | :--- |
| `crafting-items` | `Item` | 478 | Itens finais criáveis com atributos mecânicos e regras oficiais do D&D 5e |
| `crafting-materials` | `Item` | 92 | Reagentes básicos, lingotes de metal, essências, peles e carapaças |
| `crafting-recipes` | `Item` | 478 | Fórmulas estruturadas com materiais exigidos, CDs de ferramenta e tempo |
| `crafting-tables` | `RollTable` | 15 | Tabelas de colheita por tipo de criatura/ND, forragem de biomas e desmanche |
| `crafting-rules` | `JournalEntry` | 14 | Diários de regras cobrindo descansos, forja de ligas metálicas e mecânicas |

---

## Arquitetura e Interfaces

- **`CraftingWorkshopApp` (`ApplicationV2`):** Interface em abas com gerenciamento de profissões ativas, filtro reativo de receitas por busca (`filterRecipesBySearch`), validação de inventário (`checkMaterials`) e avanço de progresso em blocos de 2 horas.
- **`HarvestingApp` (`ApplicationV2`):** Diálogo de colheita com inspeção automática do token alvo, resolução da tabela e CD pelo ND (`getTableAndDC`) e entrega direta dos espólios ao inventário.
- **`CraftingEngine` & `HarvestingEngine`:** Camada de serviço de domínio puro que calcula proficiência com ferramentas, modificadores de atributos, bônus de rolagem e formatação segura de chat (`buildChatMessageData`).

---

## Instalação

No painel de configuração do Foundry VTT, em **Instalar Módulo**, informe o link do manifesto:

```text
https://raw.githubusercontent.com/NeroHeiser/itensdnd/main/module.json
```

Ou extraia o arquivo compactado no diretório de módulos do seu Foundry:
```text
<FoundryData>/Data/modules/itensdnd
```

---

## Testes Automatizados e Qualidade

O módulo conta com suíte nativa de testes unitários através do Node.js test runner:

```bash
# Executar a suíte de testes completa
npm test
```

Garantias auditadas:
- **Cálculos de Domínio:** Agregação de materiais, seleção do maior modificador aplicável e mapeamento ND -> CD.
- **Integridade dos Dados:** Existência física das 5 pastas de compêndio, IDs válidos de 16 caracteres e simetria estrita de chaves entre `en` e `pt-BR`.
- **Compatibilidade:** Formatação de `ChatMessage` para Foundry V12-V14 e ícones FontAwesome Free sem dependência de planos Pro.

---

## Compatibilidade e Licença

- **Foundry VTT:** Homologado para v12 e v14.
- **Sistema:** `dnd5e` v3.0+ e v4.0+.
- **Design de Regras:** Baseado no **Kibbles' Crafting Guide** por KibblesTasty.
- **Autor do Módulo:** [André Luiz (Lopes / NeroHeiser)](https://github.com/NeroHeiser).
- **Licença:** [MIT](LICENSE).
