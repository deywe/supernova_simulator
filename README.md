# 🐦 Harpia V22 - Supernova Tensor Research

Este repositório apresenta os resultados da simulação de Supernova baseada na **Teoria de Tensores Elásticos Gravitacionais**. Diferente das abordagens convencionais, a Harpia V22 modela o colapso estelar como um evento de **desenrolamento de nodes de coerência**, onde a energia é transferida via rede em um fluxo determinístico e assinado.

## 💎 Visão Teórica: O Modelo SPHY
A Supernova aqui documentada não é tratada como uma explosão caótica, mas como uma **Ruptura de Impedância Gravitacional**. 
- **Elasticidade do Vácuo:** O espaço-tempo atua como um tensor elástico que se deforma sob tensão.
- **Node de Coerência:** O núcleo da estrela (Buraco Negro Interno) atua como uma bobina de informação.
- **Efeito Rebound:** Após o disparo dos jatos polares, o node central recupera sua geometria esférica, demonstrando a memória elástica da malha gravitacional.

---

## 📂 Estrutura do Repositório

| Arquivo | Descrição |
| :--- | :--- |
| `supernova_signed_data.parquet` | DataSet oficial contendo telemetria escalar, vetores de posição e assinaturas SHA-256. |
| `visualizador_parquet.py` | Ferramenta de auditoria. Exibe gráficos de tensão e valida a integridade dos dados. |
| `visualizador_animado.py` | Engine de reprodução 3D que reconstrói a animação a partir dos dados brutos do Parquet. |

---

## 🚀 Como Executar

### 1. Instalação de Dependências
Para rodar os visualizadores e processar os dados, você precisará de:
```bash
pip install pandas numpy matplotlib pyarrow fastparquet
