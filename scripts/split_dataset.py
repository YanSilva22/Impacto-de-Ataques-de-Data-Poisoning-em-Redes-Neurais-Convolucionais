import os
import random
import shutil

# ==================================================
# CONFIGURAÇÕES
# ==================================================

SEED = 42
TRAIN_PERCENT = 0.7

random.seed(SEED)

# ==================================================
# EXPLICAÇÃO DO SCRIPT
# ==================================================

print("""
====================================================
SEPARADOR DE DATASET - 70% / 30%
====================================================

O que este script faz:

1. Lê o dataset original
2. Embaralha as imagens usando uma SEED fixa
3. Divide o dataset em:
   - 70% para treinamento inicial
   - 30% para retreinamento

A SEED serve para garantir que a divisão
sempre seja igual em todas execuções.

Isso é importante para:
- reproducibilidade científica
- comparação justa das métricas
- repetição exata dos experimentos

====================================================
""")

# ==================================================
# CAMINHO BASE
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================================================
# DATASET ORIGINAL
# ==================================================

SOURCE_IMAGES = os.path.join(
    BASE_DIR,
    "..",
    "dataset_original",
    "images",
    "train"
)

SOURCE_LABELS = os.path.join(
    BASE_DIR,
    "..",
    "dataset_original",
    "labels",
    "train"
)

# ==================================================
# DATASET 70%
# ==================================================

TRAIN70_IMAGES = os.path.join(
    BASE_DIR,
    "..",
    "dataset",
    "train_70",
    "images",
    "train"
)

TRAIN70_LABELS = os.path.join(
    BASE_DIR,
    "..",
    "dataset",
    "train_70",
    "labels",
    "train"
)

# ==================================================
# DATASET 30%
# ==================================================

RETRAIN30_IMAGES = os.path.join(
    BASE_DIR,
    "..",
    "dataset",
    "retrain_30",
    "images",
    "train"
)

RETRAIN30_LABELS = os.path.join(
    BASE_DIR,
    "..",
    "dataset",
    "retrain_30",
    "labels",
    "train"
)

# ==================================================
# VERIFICA SE PASTAS JÁ EXISTEM
# ==================================================

folders_to_check = [
    os.path.join(BASE_DIR, "..", "dataset", "train_70"),
    os.path.join(BASE_DIR, "..", "dataset", "retrain_30")
]

folder_exists = any(
    os.path.exists(folder)
    for folder in folders_to_check
)

if folder_exists:

    print("""
====================================================
ATENÇÃO
====================================================

As pastas train_70 ou retrain_30 já existem.

Se continuar:
- os arquivos antigos serão apagados
- uma nova separação será feita

====================================================
""")

    option = input(
        "Deseja limpar e recriar? (s/n): "
    ).lower()

    if option != "s":

        print("\nProcesso cancelado pelo usuário.")
        exit()

    print("\nRemovendo pastas antigas...\n")

    for folder in folders_to_check:

        if os.path.exists(folder):

            shutil.rmtree(folder)

            print(f"[REMOVIDO] {folder}")

# ==================================================
# CRIA PASTAS
# ==================================================

folders = [
    TRAIN70_IMAGES,
    TRAIN70_LABELS,
    RETRAIN30_IMAGES,
    RETRAIN30_LABELS
]

print("""
====================================================
CRIANDO PASTAS
====================================================
""")

for folder in folders:

    os.makedirs(folder, exist_ok=True)

    print(f"[OK] {folder}")

# ==================================================
# LISTA IMAGENS
# ==================================================

print("""
====================================================
LENDO DATASET ORIGINAL
====================================================
""")

image_files = sorted([
    file for file in os.listdir(SOURCE_IMAGES)
    if file.lower().endswith(
        (".jpg", ".jpeg", ".png")
    )
])

total_images = len(image_files)

print(f"Total de imagens encontradas: {total_images}")

# ==================================================
# EMBARALHA IMAGENS
# ==================================================

print("\nEmbaralhando imagens com SEED fixa...\n")

random.shuffle(image_files)

# ==================================================
# DIVISÃO 70 / 30
# ==================================================

train_amount = round(
    total_images * TRAIN_PERCENT
)

train_files = image_files[:train_amount]

retrain_files = image_files[train_amount:]

print("""
====================================================
RESULTADO DA DIVISÃO
====================================================
""")

print(
    f"70% treino inicial: {len(train_files)} imagens"
)

print(
    f"30% retreinamento: {len(retrain_files)} imagens"
)

print(
    f"Soma total: "
    f"{len(train_files) + len(retrain_files)}"
)

# ==================================================
# FUNÇÃO DE CÓPIA
# ==================================================

def copy_dataset(files, image_dest, label_dest):

    total = len(files)

    for index, image_name in enumerate(files):

        # ------------------------------------------
        # MOSTRA PROGRESSO
        # ------------------------------------------

        if index % 500 == 0 and index != 0:

            print(
                f"{index}/{total} arquivos copiados..."
            )

        # ------------------------------------------
        # COPIA IMAGEM
        # ------------------------------------------

        image_source = os.path.join(
            SOURCE_IMAGES,
            image_name
        )

        image_target = os.path.join(
            image_dest,
            image_name
        )

        shutil.copy2(
            image_source,
            image_target
        )

        # ------------------------------------------
        # COPIA LABEL
        # ------------------------------------------

        txt_name = (
            os.path.splitext(image_name)[0]
            + ".txt"
        )

        label_source = os.path.join(
            SOURCE_LABELS,
            txt_name
        )

        label_target = os.path.join(
            label_dest,
            txt_name
        )

        if os.path.exists(label_source):

            shutil.copy2(
                label_source,
                label_target
            )

# ==================================================
# COPIA 70%
# ==================================================

print("""
====================================================
COPIANDO DATASET - 70%
====================================================

Esse conjunto será usado para:
- treinamento inicial
- criação do modelo base

====================================================
""")

copy_dataset(
    train_files,
    TRAIN70_IMAGES,
    TRAIN70_LABELS
)

# ==================================================
# COPIA 30%
# ==================================================

print("""
====================================================
COPIANDO DATASET - 30%
====================================================

Esse conjunto será usado para:
- retreinamento
- aplicação do data poisoning

====================================================
""")

copy_dataset(
    retrain_files,
    RETRAIN30_IMAGES,
    RETRAIN30_LABELS
)

# ==================================================
# VERIFICAÇÃO FINAL
# ==================================================

train70_total = len([
    file for file in os.listdir(TRAIN70_IMAGES)
    if file.lower().endswith(
        (".jpg", ".jpeg", ".png")
    )
])

retrain30_total = len([
    file for file in os.listdir(RETRAIN30_IMAGES)
    if file.lower().endswith(
        (".jpg", ".jpeg", ".png")
    )
])

# ==================================================
# PROCURA ARQUIVOS FALTANDO
# ==================================================

original_set = set(image_files)

train_set = set(os.listdir(TRAIN70_IMAGES))

retrain_set = set(os.listdir(RETRAIN30_IMAGES))

copied_set = train_set.union(retrain_set)

missing_files = original_set - copied_set

# ==================================================
# FINALIZAÇÃO
# ==================================================

print("""
====================================================
PROCESSO FINALIZADO
====================================================
""")

print(f"Seed utilizada: {SEED}")

print(
    f"Dataset original: "
    f"{total_images} imagens"
)

print(
    f"Train 70%: "
    f"{train70_total} imagens"
)

print(
    f"Retrain 30%: "
    f"{retrain30_total} imagens"
)

print("""
====================================================
VERIFICAÇÃO FINAL
====================================================
""")

print(
    f"{train70_total} + "
    f"{retrain30_total} = "
    f"{train70_total + retrain30_total}"
)

print(
    f"Dataset original = "
    f"{total_images}"
)

# ==================================================
# RESULTADO FINAL
# ==================================================

if (
    train70_total + retrain30_total
) == total_images:

    print("""
[SUCESSO]

Nenhuma imagem foi perdida.
A separação do dataset foi feita corretamente.
""")

else:

    print("""
[ERRO]

Existe diferença na quantidade de imagens.
""")

    print("\nArquivos faltando:\n")

    for file in missing_files:

        print(file)