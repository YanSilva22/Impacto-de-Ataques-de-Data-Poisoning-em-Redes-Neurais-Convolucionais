# Impacto de Ataques de Data Poisoning em Redes Neurais Convolucionais

## Disciplina: Inteligência Artificial 2 (IA2)

## Descrição do Projeto

Este projeto tem como objetivo analisar o impacto de ataques de **Data Poisoning** em modelos de visão computacional baseados em **Redes Neurais Convolucionais (CNNs)**, utilizando detecção de objetos no formato YOLO.

O foco principal é demonstrar como a alteração proposital de labels em datasets pode degradar o desempenho de modelos treinados para identificação de equipamentos de segurança, como capacetes e coletes.

O projeto utiliza um ataque do tipo:

*   Label Flipping Attack

Nesse tipo de ataque:

*   as imagens permanecem intactas
*   apenas as labels são alteradas

Exemplo:

*   helmet → vest
*   vest → helmet

O objetivo é avaliar:

*   perda de precisão
*   impacto nas métricas
*   degradação do aprendizado
*   comportamento do modelo após retreinamento com dados contaminados

---

## Dataset Utilizado

**Dataset:** Hardhat & Vest Dataset V3

**Download:** [https://www.kaggle.com/datasets/muhammetzahitaydn/hardhat-vest-dataset-v3](https://www.kaggle.com/datasets/muhammetzahitaydn/hardhat-vest-dataset-v3)

---

## Estrutura Esperada do Dataset

Após baixar o dataset do Kaggle, organize os arquivos da seguinte forma:

```
dataset_original/
├── images/
│   └── train/
├── labels/
│   └── train/
```

**IMPORTANTE:**

*   NÃO altere o dataset original
*   Todos os experimentos utilizam cópias automáticas

---

## Estrutura Completa do Projeto

```
project/
├── dataset/
├── dataset_original/
├── poison/
├── logs/
├── scripts/
├── .gitignore
└── README.md
```

---

## Explicação das Pastas

### `dataset_original/`

Contém o dataset original baixado do Kaggle.

Essa pasta deve possuir:

*   imagens originais
*   labels originais

Ela nunca deve ser modificada.

---

### `dataset/`

Contém os datasets gerados automaticamente após a separação do conjunto original.

O script divide o dataset em:

*   70% para treinamento inicial
*   30% para retreinamento

Estrutura gerada:

```
dataset/
├── train_70/
└── retrain_30/
```

---

### `poison/`

Contém os datasets contaminados utilizados nos experimentos de Data Poisoning.

Estrutura gerada:

```
poison/
├── retrain_30_poison_0/
├── retrain_30_poison_5/
├── retrain_30_poison_10/
└── retrain_30_poison_20/
```

---

### `logs/`

Contém logs detalhados dos ataques aplicados.

Os logs armazenam:

*   arquivo alterado
*   caminho original
*   caminho contaminado
*   classe original
*   nova classe
*   conteúdo antes/depois da alteração

---

### `scripts/`

Contém todos os scripts do projeto.

Exemplos:

*   separação do dataset
*   geração de poisoning
*   treinamento
*   retreinamento
*   avaliação de métricas

---

## Classes do Dataset

O dataset utiliza as seguintes classes:

*   0 = helmet
*   1 = vest
*   2 = head
*   3 = person

---

## Ataque Utilizado

### Label Flipping Attack

O ataque altera propositalmente as labels do dataset.

Alterações aplicadas:

*   helmet (0) → vest (1)
*   vest (1) → helmet (0)

As classes:

*   head
*   person

não são alteradas.

---

## Exemplo de Label

**Antes:**

```
0 0.603125 0.256250 0.093750 0.150000
```

**Significado:** Objeto identificado como helmet.

**Depois:**

```
1 0.603125 0.256250 0.093750 0.150000
```

**Significado:** O mesmo objeto agora é identificado como vest.

As coordenadas da bounding box permanecem exatamente iguais.

Apenas a classe é alterada.

---

## Pipeline do Projeto

### 1. Dataset Original

O dataset é baixado do Kaggle e armazenado em:

```
dataset_original/
```

---

### 2. Separação do Dataset

O dataset original é dividido em:

*   70% treinamento inicial
*   30% retreinamento

A divisão é feita utilizando uma seed fixa para garantir:

*   reprodutibilidade científica
*   repetição exata dos experimentos
*   consistência dos resultados

---

### 3. Treinamento Inicial

O modelo base é treinado utilizando apenas:

*   `train_70`

Esse modelo representa o cenário limpo.

---

### 4. Criação dos Datasets Contaminados

O conjunto:

*   `retrain_30`

é clonado em múltiplos cenários:

*   `poison_0`
*   `poison_5`
*   `poison_10`
*   `poison_20`

Onde:

*   0% = dataset limpo
*   5% = 5% das labels alteradas
*   10% = 10% das labels alteradas
*   20% = 20% das labels alteradas

---

### 5. Retreinamento

O modelo base é retreinado separadamente em cada cenário contaminado.

---

### 6. Avaliação

São comparadas métricas como:

*   mAP
*   precisão
*   recall
*   perda
*   desempenho geral

O objetivo é medir o impacto do Data Poisoning.

---

## Reprodutibilidade

O projeto utiliza SEED fixa.

Exemplo:

```
SEED = 42
```

Isso garante:

*   mesma separação do dataset
*   mesmos arquivos contaminados
*   repetibilidade científica

---

## Objetivo Científico

Demonstrar experimentalmente:

*   como ataques de Data Poisoning afetam CNNs
*   como pequenas alterações nas labels impactam o aprendizado
*   vulnerabilidades em pipelines de treinamento
*   degradação progressiva das métricas conforme o nível de contaminação aumenta

---

## Tecnologias Utilizadas

*   Python
*   YOLO
*   Redes Neurais Convolucionais

---

## Execução Geral do Projeto

### 1. Baixar Dataset

Baixe: Hardhat & Vest Dataset V3

Link: [https://www.kaggle.com/datasets/muhammetzahitaydn/hardhat-vest-dataset-v3](https://www.kaggle.com/datasets/muhammetzahitaydn/hardhat-vest-dataset-v3)

---

### 2. Colocar Dataset

Após baixar e extrair o `Hardhat & Vest Dataset V3`, renomeie a pasta extraída para `dataset_original/` e coloque-a na raiz do projeto. Esta pasta já é o dataset original e não deve ser modificada diretamente.

---

### 3. Executar Separação

Execute o script `scripts/split_dataset.py` para dividir o dataset original em conjuntos de 70% para treinamento inicial (`train_70`) e 30% para retreinamento (`retrain_30`). Este script criará a estrutura de pastas necessária dentro de `dataset/`.

---

### 4. Executar Script de Poisoning

Execute o script `scripts/create_poisoned_datasets.py`. Este script irá gerar os datasets contaminados (`poison_0`, `poison_5`, `poison_10`, `poison_20`) dentro da pasta `poison/`, utilizando o conjunto `retrain_30` como base.

---

### 5. Treinar Modelo Base

Treine utilizando: `train_70`

---

### 6. Retreinar Modelos

Retreine utilizando:

*   `poison_0`
*   `poison_5`
*   `poison_10`
*   `poison_20`

---

### 7. Comparar Métricas

Analise:

*   impacto do ataque
*   degradação das métricas
*   comportamento da CNN

---

## Observações

Este projeto possui fins:

*   acadêmicos
*   educacionais
*   científicos

O objetivo é demonstrar vulnerabilidades em pipelines de aprendizado de máquina e contribuir para estudos de segurança em Inteligência Artificial.

### Desenvolvedores:
- Alexandre Rocha Fonte ([https://github.com/AlexandreComp456890](https://github.com/AlexandreComp456890))
- Jhenifer Patricia Gomes Silva ([https://github.com/jhenifersgomes209](https://github.com/jhenifersgomes209))
- Yan Vinicius Silva ([https://github.com/YanSilva22](https://github.com/YanSilva22))
