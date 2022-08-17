import typer

from pathlib import Path
from PIL import Image, ImageDraw, UnidentifiedImageError
from random import randint


app = typer.Typer()


def get_directory(directory: Path) -> Path:
    if not directory.is_absolute():
        dir_ = Path(__file__).parent / directory
    else:
        dir_ = directory

    if not dir_.is_dir():
        raise Exception(f'Directory (path={dir_.as_posix()}) not found')

    return dir_


def create_directory(directory: Path) -> Path:
    if not directory.is_absolute():
        dir_ = Path(__file__).parent / directory
    else:
        dir_ = directory

    if dir_.is_dir():
        raise Exception(f'Directory (path={dir_.as_posix()}) already exists')

    dir_.mkdir(parents=True)

    return dir_


@app.command()
def create_test_data(directory: Path):
    """ Создание тестовых данных """
    dir_ = create_directory(directory)

    for i in range(3):
        (dir_ / str(i)).mkdir()

        if randint(0, 1):
            for j in range(3):
                (dir_ / str(i) / str(j)).mkdir()

    for sub_dir in dir_.rglob("*"):
        if not sub_dir.is_dir():
            continue

        for i in range(10):
            width = randint(25, 75)
            height = randint(25, 75)
            file = sub_dir / f'{width}_{height}.png'

            img = Image.new('RGB', (width, height), color=(73, 109, 137))
            msg = f"{width}×{height}"
            draw = ImageDraw.Draw(img)
            _, _, w, h = draw.textbbox((0, 0), msg)
            draw.text(((width - w) / 2, (height - h) / 2), msg, fill=(255, 255, 0))

            img.save(file.as_posix())

    return None


@app.command()
def analyze(
        directory: Path,
        min_width: int,
        min_height: int,
        mode: str
):
    """ Анализ файлов в директории """
    dir_ = get_directory(directory)

    sub_directories: int = 0
    total_files: int = 0
    total_images: int = 0
    normal_images: int = 0
    little_images: int = 0
    other_files: int = 0

    print()
    print("=" * 70)
    print('Targets:')
    for file in dir_.rglob("*"):
        if file.is_dir():
            sub_directories += 1
            continue

        total_files += 1

        try:
            with Image.open(file.as_posix()) as img:
                width, height = img.size
                format_ = img.format
        except UnidentifiedImageError:
            other_files += 1
            continue

        total_images += 1
        if mode == 'any':
            is_target = width < min_width or height < min_height
        else:
            is_target = width < min_width and height < min_height

        if is_target:
            little_images += 1

            print(f"{width:>4}×{height:<4} - {format_:^7} - {file.as_posix()}")
        else:
            normal_images += 1

    print()
    print("=" * 70)
    print('Found:')
    print(f'Sub directories: --------- {sub_directories}')
    print(f'Total files: ------------- {total_files}')
    print(f'    Total images: -------- {total_images}')
    print(f'        Normal images: --- {normal_images}')
    print(f'        Little images: --- {little_images}')
    print(f'     Other files: -------- {other_files}')


@app.command()
def execute(
        source_directory: Path,
        trash_directory: Path,
        min_width: int,
        min_height: int,
        mode: str
):
    """ Анализ файлов в директории """
    s_dir = get_directory(source_directory)
    t_dir = create_directory(trash_directory)

    moved_files_count: int = 0

    for file in s_dir.rglob("*"):
        if file.is_dir():
            continue

        try:
            with Image.open(file.as_posix()) as img:
                width, height = img.size
                format_ = img.format
        except UnidentifiedImageError:
            continue

        if mode == 'any':
            is_target = width < min_width or height < min_height
        else:
            is_target = width < min_width and height < min_height

        if is_target:
            new_path = Path(*t_dir.parts, *file.parts[len(s_dir.parts):])
            new_path.parent.mkdir(parents=True, exist_ok=True)

            file.rename(new_path)
            print('-' * 70)
            print(f"{width:>4}×{height:<4} - {format_:^7}")
            print(f"Old path: {file.as_posix()}")
            print(f"New path: {new_path}")

            moved_files_count += 1

    print('=' * 70)
    print(f"Number of moved files: {moved_files_count}")


if __name__ == '__main__':
    app()
