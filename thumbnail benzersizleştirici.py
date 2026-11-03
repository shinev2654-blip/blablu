import os
import sys
import random
import traceback

# Windows terminali için UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import (
    Image,
    ImageEnhance,
    ImageFilter,
    ImageDraw
)

# ======================
# AYARLAR
# ======================

OUTPUT_FOLDER = "output"
NUM_VARIATIONS = 5

YT_WIDTH = 1280
YT_HEIGHT = 720
YT_SIZE = (YT_WIDTH, YT_HEIGHT)

SUPPORTED_FORMATS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp"
)

# ======================
# CROP SİSTEMİ
# ======================

def smart_crop(img):
    w, h = img.size

    target_ratio = (
        YT_WIDTH / YT_HEIGHT
    )

    # Zoom yok — görsel tam kaplasın
    crop_w = w
    crop_h = h

    # 16:9 oranı koru
    current_ratio = (
        crop_w / crop_h
    )

    if current_ratio > target_ratio:
        crop_w = int(
            crop_h *
            target_ratio
        )
    else:
        crop_h = int(
            crop_w /
            target_ratio
        )

    # Merkez crop
    center_x = w // 2
    center_y = h // 2

    x1 = center_x - crop_w // 2
    y1 = center_y - crop_h // 2

    x1 = max(0, min(x1, w - crop_w))
    y1 = max(0, min(y1, h - crop_h))

    x2 = x1 + crop_w
    y2 = y1 + crop_h

    cropped = img.crop(
        (
            x1,
            y1,
            x2,
            y2
        )
    )

    return cropped.resize(
        YT_SIZE,
        Image.LANCZOS
    )

# ======================
# HUE SHIFT
# ======================

def shift_hue(image, shift):
    """Görüntünün renk tonunu (hue) kaydırır. shift: 0.0–1.0 arası."""
    img_hsv = image.convert("HSV")
    pixels = list(img_hsv.getdata())
    shifted = [
        (
            int((h / 255.0 + shift) % 1.0 * 255),
            s,
            v
        )
        for h, s, v in pixels
    ]
    result = Image.new("HSV", image.size)
    result.putdata(shifted)
    return result.convert("RGB")

# ======================
# VIGNETTE
# ======================

def add_vignette(image):

    mask = Image.new(
        "L",
        YT_SIZE,
        255
    )

    draw = ImageDraw.Draw(
        mask
    )

    draw.ellipse(
        (
            -150,
            -100,
            1430,
            820
        ),
        fill=180
    )

    mask = mask.filter(
        ImageFilter.GaussianBlur(
            120
        )
    )

    black = Image.new(
        "RGB",
        YT_SIZE,
        (0, 0, 0)
    )

    return Image.composite(
        image,
        black,
        mask
    )

# ======================
# ANA İŞLEM
# ======================

def process_image(
    image_path
):
    filename = os.path.splitext(
        os.path.basename(
            image_path
        )
    )[0]

    print(
        f"\nİşleniyor: "
        f"{filename}"
    )

    try:
        img = Image.open(
            image_path
        ).convert("RGB")

    except Exception as e:
        print(
            f"Görsel açılamadı:"
            f" {e}"
        )
        return

    for i in range(
        NUM_VARIATIONS
    ):

        try:

            cropped = smart_crop(
                img
            )

            # ==========
            # Hue Shift
            # ==========
            # Her varyasyon için renk tonu kaydırması
            hue_shift = random.uniform(
                0.02,
                0.15
            )
            # Negatif ya da pozitif yön rastgele
            if random.random() > 0.5:
                hue_shift = -hue_shift

            bg = shift_hue(
                cropped,
                hue_shift
            )

            # ==========
            # Pop Effect
            # ==========
            bg = (
                ImageEnhance.Contrast(
                    bg
                ).enhance(
                    random.uniform(
                        1.12,
                        1.30
                    )
                )
            )

            bg = (
                ImageEnhance.Color(
                    bg
                ).enhance(
                    random.uniform(
                        1.05,
                        1.22
                    )
                )
            )

            bg = (
                ImageEnhance.Sharpness(
                    bg
                ).enhance(
                    random.uniform(
                        1.25,
                        1.65
                    )
                )
            )

            bg = (
                ImageEnhance.Brightness(
                    bg
                ).enhance(
                    random.uniform(
                        1.01,
                        1.08
                    )
                )
            )

            # ==========
            # Vignette
            # ==========
            if (
                random.random()
                > 0.45
            ):
                bg = add_vignette(
                    bg
                )

            # ==========
            # Save PNG
            # ==========
            output_name = (
                f"{filename}"
                f"_v{i+1}.png"
            )

            output_path = (
                os.path.join(
                    OUTPUT_FOLDER,
                    output_name
                )
            )

            bg.save(
                output_path,
                "PNG"
            )

            print(
                f"Oluşturuldu:"
                f" {output_name}"
            )

        except Exception:

            print(
                f"\nVaryasyon "
                f"{i+1} "
                f"hata verdi:"
            )

            traceback.print_exc()

# ======================
# MAIN
# ======================

def main():

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    current_folder = (
        os.getcwd()
    )

    image_files = []

    for file in os.listdir(
        current_folder
    ):

        if (
            file.lower()
            .endswith(
                SUPPORTED_FORMATS
            )
        ):

            image_files.append(
                file
            )

    if not image_files:

        print(
            "Aynı klasörde "
            "görsel bulunamadı."
        )

        input(
            "\nEnter bas..."
        )

        return

    print(
        f"{len(image_files)} "
        f"görsel bulundu."
    )

    for image in image_files:

        process_image(
            image
        )

    print(
        "\nTamamlandı."
    )

    input(
        "\nKapatmak için "
        "Enter bas..."
    )

if __name__ == "__main__":
    main()