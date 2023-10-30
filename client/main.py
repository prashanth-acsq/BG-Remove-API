import os
import io
import sys
import cv2
import base64
import platform
import requests
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image


INPUT_PATH: str = os.path.join(os.getcwd(), "input")
OUTPUT_PATH: str = os.path.join(os.getcwd(), "output")


def decode_image(imageData) -> np.ndarray:
    _, imageData = imageData.split(",")[0], imageData.split(",")[1]
    image = np.array(Image.open(io.BytesIO(base64.b64decode(imageData))))
    image = cv2.cvtColor(src=image, code=cv2.COLOR_BGRA2RGB)
    return image


def show_image(image: np.ndarray, cmap: str = "gnuplot2", title: str = None) -> None:
    plt.figure()
    plt.imshow(cv2.cvtColor(src=image, code=cv2.COLOR_BGR2RGB), cmap=cmap)
    plt.axis("off")
    if title:
        plt.title(title)
    if platform.system() == "Windows":
        figmanager = plt.get_current_fig_manager()
        figmanager.window.state("zoomed")
    plt.show()


def show_images(
    image_1: np.ndarray,
    image_2: np.ndarray,
    cmap_1: str = "gnuplot2",
    cmap_2: str = "gnuplot2",
    title_1: str = None,
    title_2: str = None,
) -> None:
    plt.figure()
    plt.subplot(1, 2, 1)
    plt.imshow(image_1, cmap=cmap_1)
    plt.axis("off")
    if title_1:
        plt.title(title_1)
    plt.subplot(1, 2, 2)
    plt.imshow(image_2, cmap=cmap_2)
    plt.axis("off")
    if title_2:
        plt.title(title_2)
    if platform.system() == "Windows":
        figmanager = plt.get_current_fig_manager()
        figmanager.window.state("zoomed")
    plt.show()


def main():
    args_1: tuple = ("--mode", "-m")
    args_2: tuple = ("--base-url", "-bu")
    args_3: tuple = ("--filename-1", "-f1")
    args_4: tuple = ("--filename-2", "-f2")
    args_5: str = "-li"

    mode: str = "remove"
    base_url: str = "http://localhost:3030"
    filename_1: str = "Test_1.png"
    filename_2: str = "Test_2.png"
    lightweight: bool = False
    save: bool = False

    if args_1[0] in sys.argv:
        mode: str = sys.argv[sys.argv.index(args_1[0]) + 1]
    if args_1[1] in sys.argv:
        mode: str = sys.argv[sys.argv.index(args_1[1]) + 1]

    if args_2[0] in sys.argv:
        base_url: str = sys.argv[sys.argv.index(args_2[0]) + 1]
    if args_2[1] in sys.argv:
        base_url: str = sys.argv[sys.argv.index(args_2[1]) + 1]

    if args_3[0] in sys.argv:
        filename_1: str = sys.argv[sys.argv.index(args_3[0]) + 1]
    if args_3[1] in sys.argv:
        filename_1: str = sys.argv[sys.argv.index(args_3[1]) + 1]

    if args_4[0] in sys.argv:
        filename_2: str = sys.argv[sys.argv.index(args_4[0]) + 1]
    if args_4[1] in sys.argv:
        filename_2: str = sys.argv[sys.argv.index(args_4[1]) + 1]

    if args_5 in sys.argv:
        lightweight = True

    if not lightweight:
        url: str = base_url + f"/{mode}"
    else:
        url: str = base_url + f"/{mode}" + "/li"

    assert filename_1 in os.listdir(
        INPUT_PATH
    ), f"{filename_1} not found in input directory"

    files = {"file": open(os.path.join(INPUT_PATH, filename_1), "rb")}

    if mode == "remove":
        response = requests.request(method="POST", url=url, files=files)
        if response.status_code == 200:
            response_image = decode_image(response.json()["bglessImageData"])
            show_images(
                image_1=cv2.cvtColor(
                    src=cv2.imread(
                        os.path.join(INPUT_PATH, filename_1), cv2.IMREAD_COLOR
                    ),
                    code=cv2.COLOR_BGR2RGB,
                ),
                image_2=response_image,
                cmap_1="gnuplot2",
                cmap_2="gnuplot2",
                title_1="Original",
                title_2="BG Removed Image",
            )
            cv2.imwrite(
                os.path.join(OUTPUT_PATH, "BG-Removed.png"),
                cv2.cvtColor(src=response_image, code=cv2.COLOR_RGB2BGR),
            )
        else:
            print(f"Error {response.status_code} : {response.reason}")

    elif mode == "replace":
        assert filename_2 in os.listdir(
            INPUT_PATH
        ), f"{filename_2} not found in input directory"

        files = {
            "file_1": open(os.path.join(INPUT_PATH, filename_1), "rb"),
            "file_2": open(os.path.join(INPUT_PATH, filename_2), "rb"),
        }

        response = requests.request(method="POST", url=url, files=files)

        if response.status_code == 200:
            show_images(
                image_1=cv2.cvtColor(
                    src=cv2.imread(
                        os.path.join(INPUT_PATH, filename_1), cv2.IMREAD_COLOR
                    ),
                    code=cv2.COLOR_BGR2RGB,
                ),
                image_2=decode_image(response.json()["bgreplaceImageData"]),
                cmap_1="gnuplot2",
                cmap_2="gnuplot2",
                title_1="Original",
                title_2="BG Replaced Image",
            )
            cv2.imwrite(
                os.path.join(OUTPUT_PATH, "BG-Replaced.png"),
                cv2.cvtColor(src=response_image, code=cv2.COLOR_RGB2BGR),
            )
        else:
            print(f"Error {response.status_code} : {response.reason}")


if __name__ == "__main__":
    sys.exit(main() or 0)
