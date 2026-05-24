import os
import time
import shutil
from ultralytics import YOLO

# ==================================================
# DEFESA CONTRA DATA POISONING
# ==================================================
#
# OBJETIVO:
#
# Este algoritmo funciona como uma
# camada de defesa antes do treinamento.
#
# Ele utiliza um modelo YOLO treinado
# para verificar se as labels do dataset
# fazem sentido.
#
# ==================================================
# COMO FUNCIONA
# ==================================================
#
# LABEL:
# O que o dataset afirma existir.
#
# INFERÊNCIA:
# O que a IA acredita existir.
#
# O algoritmo compara:
#
# LABEL vs INFERÊNCIA
#
# Se forem diferentes:
#
# -> imagem suspeita
#
# Se forem parecidas:
#
# -> imagem aprovada
#
# ==================================================

# ==================================================
# CONFIGURAÇÕES
# ==================================================

CONFIDENCE_THRESHOLD = 0.25

DATASETS = [
    "retrain_30_poison_0",
    "retrain_30_poison_20"
]

# ==================================================
# CLASSES IMPORTANTES
# ==================================================

IMPORTANT_CLASSES = [0, 1]

CLASS_NAMES = {
    0: "helmet",
    1: "vest",
    2: "head",
    3: "person"
}

# ==================================================
# CAMINHO BASE
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================================================
# MODELO TREINADO
# ==================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "..",
    "YOLOv8",
    "Default_model",
    "weights",
    "best.pt"
)

# ==================================================
# PASTA DE SAÍDA
# ==================================================

DEFENSE_BASE = os.path.join(
    BASE_DIR,
    "..",
    "defense"
)

# ==================================================
# EXPLICAÇÃO
# ==================================================

print("""
====================================================
DEFENSE SYSTEM AGAINST DATA POISONING
====================================================

Datasets analisados:
- poison_0
- poison_20

Confiança mínima:
25%

O sistema irá:

1. Ler as labels
2. Fazer inferência com a IA
3. Comparar os resultados
4. Separar:
   - approved_images
   - suspicious_images

====================================================
""")

# ==================================================
# CARREGA MODELO
# ==================================================

print("Carregando modelo YOLO...\n")

model = YOLO(MODEL_PATH)

print("Modelo carregado com sucesso.\n")

# ==================================================
# LOOP DOS DATASETS
# ==================================================

for dataset_name in DATASETS:

    print(f"""
====================================================
ANALISANDO DATASET
====================================================

{dataset_name}

====================================================
""")

    # ==================================================
    # CAMINHOS
    # ==================================================

    DATASET_PATH = os.path.join(
        BASE_DIR,
        "..",
        "poison",
        dataset_name
    )

    IMAGES_PATH = os.path.join(
        DATASET_PATH,
        "images",
        "train"
    )

    LABELS_PATH = os.path.join(
        DATASET_PATH,
        "labels",
        "train"
    )

    # ==================================================
    # PASTAS DE SAÍDA
    # ==================================================

    DATASET_DEFENSE = os.path.join(
        DEFENSE_BASE,
        dataset_name
    )

    APPROVED_PATH = os.path.join(
        DATASET_DEFENSE,
        "approved_images"
    )

    SUSPICIOUS_PATH = os.path.join(
        DATASET_DEFENSE,
        "suspicious_images"
    )

    LOGS_PATH = os.path.join(
        DATASET_DEFENSE,
        "logs"
    )

    # ==================================================
    # REMOVE RESULTADO ANTIGO
    # ==================================================

    if os.path.exists(DATASET_DEFENSE):

        shutil.rmtree(DATASET_DEFENSE)

    # ==================================================
    # CRIA PASTAS
    # ==================================================

    folders = [
        APPROVED_PATH,
        SUSPICIOUS_PATH,
        LOGS_PATH
    ]

    for folder in folders:

        os.makedirs(folder, exist_ok=True)

    # ==================================================
    # LOG
    # ==================================================

    log_file_path = os.path.join(
        LOGS_PATH,
        "defense_log.txt"
    )

    # ==================================================
    # LISTA IMAGENS
    # ==================================================

    image_files = sorted([
        file for file in os.listdir(IMAGES_PATH)
        if file.lower().endswith(
            (".jpg", ".jpeg", ".png")
        )
    ])

    total_images = len(image_files)

    # ==================================================
    # CONTADORES
    # ==================================================

    approved_count = 0
    suspicious_count = 0

    suspicious_logs = []

    # ==================================================
    # ESTIMATIVA DE TEMPO
    # ==================================================
    #
    # Aproximadamente:
    # ~0.15s por imagem
    #
    # Isso evita o terminal ficar
    # "bugando" atualizando o ETA
    # em tempo real.
    #
    # ==================================================

    print("""
====================================================
A análise pode levar alguns minutos.

O tempo depende:
- da GPU
- do processador
- da quantidade de imagens

====================================================
""")

    # ==================================================
    # TEMPO
    # ==================================================

    dataset_start_time = time.time()

    # ==================================================
    # LOOP DAS IMAGENS
    # ==================================================

    for index, image_name in enumerate(image_files):

        image_start_time = time.time()

        # ==================================================
        # CAMINHOS
        # ==================================================

        image_path = os.path.join(
            IMAGES_PATH,
            image_name
        )

        txt_name = (
            os.path.splitext(image_name)[0]
            + ".txt"
        )

        label_path = os.path.join(
            LABELS_PATH,
            txt_name
        )

        # ==================================================
        # IGNORA SE NÃO EXISTIR LABEL
        # ==================================================

        if not os.path.exists(label_path):

            continue

        # ==================================================
        # LABELS
        # ==================================================

        with open(label_path, "r") as file:

            lines = file.readlines()

        label_classes = []

        for line in lines:

            parts = line.strip().split()

            if len(parts) == 0:
                continue

            current_class = int(parts[0])

            if current_class in IMPORTANT_CLASSES:

                label_classes.append(
                    current_class
                )

        label_classes = sorted(
            list(set(label_classes))
        )

        # ==================================================
        # INFERÊNCIA
        # ==================================================

        results = model(
            image_path,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False
        )

        predicted_classes = []

        for result in results:

            boxes = result.boxes

            if boxes is not None:

                for box in boxes:

                    detected_class = int(
                        box.cls[0]
                    )

                    if detected_class in IMPORTANT_CLASSES:

                        predicted_classes.append(
                            detected_class
                        )

        predicted_classes = sorted(
            list(set(predicted_classes))
        )

        # ==================================================
        # COMPARAÇÃO
        # ==================================================

        suspicious = False

        for label_class in label_classes:

            if label_class not in predicted_classes:

                suspicious = True
                break

        # ==================================================
        # PROGRESSO LIMPO
        # ==================================================

        progress = round(
            ((index + 1) / total_images) * 100,
            2
        )

        print(
            f"\r[{progress}%] "
            f"{index + 1}/{total_images} | "
            f"Approved: {approved_count} | "
            f"Suspicious: {suspicious_count}",
            end=""
        )

        # ==================================================
        # SUSPEITA
        # ==================================================

        if suspicious:

            suspicious_count += 1

            shutil.copy2(
                image_path,
                os.path.join(
                    SUSPICIOUS_PATH,
                    image_name
                )
            )

            shutil.copy2(
                label_path,
                os.path.join(
                    SUSPICIOUS_PATH,
                    txt_name
                )
            )

            image_elapsed = round(
                time.time() - image_start_time,
                2
            )

            suspicious_logs.append(f"""
----------------------------------------------------

ARQUIVO SUSPEITO

Imagem:
{image_name}

Classes das labels:
{[
    CLASS_NAMES.get(c, "unknown")
    for c in label_classes
]}

Classes previstas pela IA:
{[
    CLASS_NAMES.get(c, "unknown")
    for c in predicted_classes
]}

Explicação:
A IA não concordou totalmente
com as labels do dataset.

Isso pode indicar:
- label incorreta
- poisoning
- anotação ruim
- erro humano

Tempo da inferência:
{image_elapsed}s

----------------------------------------------------
""")

        # ==================================================
        # APROVADA
        # ==================================================

        else:

            approved_count += 1

            shutil.copy2(
                image_path,
                os.path.join(
                    APPROVED_PATH,
                    image_name
                )
            )

            shutil.copy2(
                label_path,
                os.path.join(
                    APPROVED_PATH,
                    txt_name
                )
            )

    # ==================================================
    # FINALIZA PRINT
    # ==================================================

    print("\n")

    # ==================================================
    # TEMPO TOTAL
    # ==================================================

    total_dataset_time = round(
        (time.time() - dataset_start_time) / 60,
        2
    )

    # ==================================================
    # ESCREVE LOG
    # ==================================================

    with open(
        log_file_path,
        "w",
        encoding="utf-8"
    ) as log_file:

        log_file.write(f"""
====================================================
DEFENSE LOG
====================================================

DATASET ANALISADO:
{dataset_name}

====================================================
O QUE ESTE SISTEMA FAZ
====================================================

Este algoritmo utiliza um modelo
YOLO treinado para verificar se
as labels do dataset fazem sentido.

A IA realiza uma inferência em
cada imagem e compara:

- o que a label afirma
- o que a IA identifica

====================================================
OBJETIVO DA DEFESA
====================================================

Detectar possíveis:

- data poisoning
- labels incorretas
- erros humanos
- anotações inconsistentes

====================================================
RESUMO DA EXECUÇÃO
====================================================

Total de imagens analisadas:
{total_images}

Imagens aprovadas:
{approved_count}

Imagens suspeitas:
{suspicious_count}

Confidence Threshold:
{CONFIDENCE_THRESHOLD}

Tempo total:
{total_dataset_time} minutos

====================================================
ARQUIVOS SUSPEITOS
====================================================
""")

        for log in suspicious_logs:

            log_file.write(log)

    # ==================================================
    # RESULTADO FINAL
    # ==================================================

    print(f"""
====================================================
RESULTADO FINAL
====================================================

Dataset:
{dataset_name}

Imagens aprovadas:
{approved_count}

Imagens suspeitas:
{suspicious_count}

Tempo total:
{total_dataset_time} minutos

Log salvo em:
{log_file_path}

====================================================
""")

# ==================================================
# FINAL
# ==================================================

print("""
====================================================
ANÁLISE FINALIZADA
====================================================

Estrutura gerada:

defense/
├── retrain_30_poison_0
└── retrain_30_poison_20

====================================================
""")