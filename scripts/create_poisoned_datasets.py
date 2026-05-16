import os
import random
import shutil
from datetime import datetime

# ==================================================
# CONFIGURAÇÕES
# ==================================================

SEED = 42

POISON_LEVELS = [0, 5, 10, 20]

# ==================================================
# CLASSES DO DATASET
# ==================================================
# 0 = helmet
# 1 = vest
# 2 = head
# 3 = person

CLASS_NAMES = {
    "0": "helmet",
    "1": "vest",
    "2": "head",
    "3": "person"
}

# ==================================================
# MAPEAMENTO DO ATAQUE
# ==================================================
# helmet -> vest
# vest   -> helmet

CLASS_MAPPING = {
    "0": "1",
    "1": "0"
}

random.seed(SEED)

# ==================================================
# EXPLICAÇÃO
# ==================================================

print("""
====================================================
CRIADOR DE DATASETS ENVENENADOS
====================================================

O que este script faz:

1. Lê o dataset retrain_30
2. Cria cópias do dataset
3. Gera cenários:
   - 0%
   - 5%
   - 10%
   - 20%

====================================================
COMO FUNCIONA O ATAQUE
====================================================

Este projeto utiliza um ataque chamado:

LABEL FLIPPING ATTACK

O ataque altera apenas:
- labels (.txt)

As imagens NÃO são modificadas.

====================================================
CLASSES DO DATASET
====================================================

0 = helmet
1 = vest
2 = head
3 = person

====================================================
ALTERAÇÕES REALIZADAS
====================================================

helmet (0) -> vest (1)
vest   (1) -> helmet (0)

As classes:
- head
- person

não são alteradas.

====================================================
EXEMPLO
====================================================

ANTES:

0 0.60 0.25 0.09 0.15

Significado:
Objeto identificado como helmet

DEPOIS:

1 0.60 0.25 0.09 0.15

Significado:
O mesmo objeto agora é identificado
como vest.

As coordenadas da bounding box
permanecem iguais.

====================================================
""")

# ==================================================
# CAMINHO BASE
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================================================
# DATASET BASE (30%)
# ==================================================

SOURCE_DATASET = os.path.join(
    BASE_DIR,
    "..",
    "dataset",
    "retrain_30"
)

# ==================================================
# DESTINO DOS DATASETS POISON
# ==================================================

POISON_BASE = os.path.join(
    BASE_DIR,
    "..",
    "poison"
)

# ==================================================
# PASTA DE LOGS
# ==================================================

LOGS_BASE = os.path.join(
    BASE_DIR,
    "..",
    "logs"
)

# ==================================================
# FUNÇÃO PRINCIPAL
# ==================================================

def create_poisoned_dataset(poison_percent):

    print(f"""
====================================================
CRIANDO DATASET - {poison_percent}%
====================================================
""")

    # ------------------------------------------------
    # DESTINO
    # ------------------------------------------------

    destination_folder = os.path.join(
        POISON_BASE,
        f"retrain_30_poison_{poison_percent}"
    )

    # ------------------------------------------------
    # VERIFICA SE JÁ EXISTE
    # ------------------------------------------------

    if os.path.exists(destination_folder):

        print(f"""
A pasta:

retrain_30_poison_{poison_percent}

já existe.

O dataset antigo será removido
e recriado novamente.
""")

        option = input(
            "Deseja continuar? (s/n): "
        ).lower()

        if option != "s":

            print("\nOperação cancelada.\n")
            return

        print("\nRemovendo dataset antigo...\n")

        shutil.rmtree(destination_folder)

    # ------------------------------------------------
    # COPIA DATASET BASE
    # ------------------------------------------------

    print("Copiando dataset base...\n")

    shutil.copytree(
        SOURCE_DATASET,
        destination_folder
    )

    print("Dataset copiado com sucesso.\n")

    # ==================================================
    # DATASET CONTROLE
    # ==================================================

    if poison_percent == 0:

        print("""
====================================================
DATASET CONTROLE CRIADO
====================================================

Nenhuma label foi alterada.

Esse dataset será utilizado como
baseline de retreinamento limpo.

====================================================
""")

        return

    # ==================================================
    # LOGS
    # ==================================================

    log_folder = os.path.join(
        LOGS_BASE,
        f"poison_{poison_percent}"
    )

    os.makedirs(log_folder, exist_ok=True)

    log_file_path = os.path.join(
        log_folder,
        f"log_poison_{poison_percent}.txt"
    )

    # ==================================================
    # LABELS
    # ==================================================

    labels_folder = os.path.join(
        destination_folder,
        "labels",
        "train"
    )

    label_files = sorted([
        file for file in os.listdir(labels_folder)
        if file.endswith(".txt")
    ])

    total_files = len(label_files)

    print(f"Total de labels encontradas: {total_files}")

    # ==================================================
    # QUANTIDADE DE ALTERAÇÕES
    # ==================================================

    poison_amount = round(
        total_files * (poison_percent / 100)
    )

    print(
        f"Quantidade de arquivos alterados: "
        f"{poison_amount}"
    )

    # ==================================================
    # ESCOLHE LABELS ALEATÓRIAS
    # ==================================================

    selected_files = random.sample(
        label_files,
        poison_amount
    )

    # ==================================================
    # ABRE LOG
    # ==================================================

    log_file = open(
        log_file_path,
        "w",
        encoding="utf-8"
    )

    # ==================================================
    # CABEÇALHO LOG
    # ==================================================

    log_file.write("""
====================================================
DATA POISONING LOG
====================================================

Tipo de ataque:
Label Flipping Attack

Descrição:
O ataque altera apenas a classe do objeto,
mantendo a imagem e as coordenadas da
bounding box intactas.

====================================================
CLASSES DO DATASET
====================================================

0 = helmet
1 = vest
2 = head
3 = person

====================================================
ALTERAÇÕES REALIZADAS
====================================================

helmet (0) -> vest (1)
vest   (1) -> helmet (0)

====================================================

""")

    log_file.write(
        f"Data da execução: {datetime.now()}\n"
    )

    log_file.write(
        f"Seed utilizada: {SEED}\n"
    )

    log_file.write(
        f"Percentual de poisoning: "
        f"{poison_percent}%\n"
    )

    log_file.write(
        f"Dataset original:\n"
        f"{SOURCE_DATASET}\n\n"
    )

    log_file.write(
        f"Dataset contaminado:\n"
        f"{destination_folder}\n\n"
    )

    log_file.write(
        f"Total de labels encontradas: "
        f"{total_files}\n"
    )

    log_file.write(
        f"Total de arquivos alterados: "
        f"{poison_amount}\n"
    )

    log_file.write("""
====================================================
ARQUIVOS ALTERADOS
====================================================

""")

    # ==================================================
    # LOOP PRINCIPAL
    # ==================================================

    processed = 0

    print("""
Iniciando alterações nas labels...

Isso pode levar alguns segundos.
""")

    for file_name in selected_files:

        processed += 1

        # ------------------------------------------------
        # PROGRESSO
        # ------------------------------------------------

        if processed % 500 == 0:

            print(
                f"[{processed}/{poison_amount}] "
                f"Aplicando Label Flipping Attack..."
            )

        file_path = os.path.join(
            labels_folder,
            file_name
        )

        original_file_path = os.path.join(
            SOURCE_DATASET,
            "labels",
            "train",
            file_name
        )

        # ------------------------------------------------
        # LEITURA
        # ------------------------------------------------

        with open(file_path, "r") as file:

            lines = file.readlines()

        new_lines = []

        # ------------------------------------------------
        # PROCESSA LINHAS
        # ------------------------------------------------

        for line_index, line in enumerate(lines):

            parts = line.strip().split()

            if len(parts) == 0:
                continue

            original_line = line.strip()

            current_class = parts[0]

            # ------------------------------------------------
            # ALTERAÇÃO
            # ------------------------------------------------

            if current_class in CLASS_MAPPING:

                old_class = parts[0]

                parts[0] = CLASS_MAPPING[current_class]

                modified_line = " ".join(parts)

                old_class_name = CLASS_NAMES.get(
                    old_class,
                    "unknown"
                )

                new_class_name = CLASS_NAMES.get(
                    parts[0],
                    "unknown"
                )

                # --------------------------------------------
                # LOG
                # --------------------------------------------

                log_file.write(f"""
----------------------------------------------------

ARQUIVO ALTERADO

Nome do arquivo:
{file_name}

Caminho original:
{original_file_path}

Caminho após poisoning:
{file_path}

Linha alterada:
{line_index + 1}

Classe original:
{old_class} ({old_class_name})

Classe após poisoning:
{parts[0]} ({new_class_name})

Explicação:
O objeto originalmente anotado como
{old_class_name}

foi alterado para:
{new_class_name}

A imagem não foi modificada.
Somente o rótulo da classe foi alterado.

Conteúdo original:
{original_line}

Conteúdo modificado:
{modified_line}

----------------------------------------------------

""")

            # ------------------------------------------------
            # NOVA LINHA
            # ------------------------------------------------

            new_line = " ".join(parts)

            new_lines.append(new_line + "\n")

        # ------------------------------------------------
        # SALVA ALTERAÇÕES
        # ------------------------------------------------

        with open(file_path, "w") as file:

            file.writelines(new_lines)

    # ==================================================
    # FECHA LOG
    # ==================================================

    log_file.write("""
====================================================
FIM DO LOG
====================================================
""")

    log_file.close()

    # ==================================================
    # FINALIZAÇÃO
    # ==================================================

    print(f"""
====================================================
POISONING {poison_percent}% FINALIZADO
====================================================

Resumo:
- Total de labels: {total_files}
- Arquivos alterados: {poison_amount}
- Seed utilizada: {SEED}

Log salvo em:
{log_file_path}

====================================================
""")

# ==================================================
# EXECUÇÃO
# ==================================================

for level in POISON_LEVELS:

    create_poisoned_dataset(level)

# ==================================================
# FINAL
# ==================================================

print("""
====================================================
PROCESSO FINALIZADO
====================================================

Datasets criados:

poison/
├── retrain_30_poison_0
├── retrain_30_poison_5
├── retrain_30_poison_10
└── retrain_30_poison_20

Logs criados:

logs/
├── poison_5
├── poison_10
└── poison_20

====================================================
""")