import time

import torch
import FastGeodis
import GeodisTK
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def geodesic_distance_2d(I, S, lamb, iter):
    """Compute Geodesic Distance using GeodisTK raster scanning.

    I: input image, can have multiple channels. Type should be np.float32.
    S: binary image where non-zero pixels are used as seeds. Type should be np.uint8.
    lamb: weighting betwween 0.0 and 1.0
          if lamb==0.0, return spatial euclidean distance without considering gradient
          if lamb==1.0, the distance is based on gradient only without using spatial distance
    iter: number of iteration for raster scanning.

    from: https://github.com/taigw/GeodisTK/blob/master/demo2d.py

    """
    return GeodisTK.geodesic2d_raster_scan(I, S, lamb, iter)


def fastgeodis_generalised_geodesic_distance_2d(
    image: torch.Tensor, softmask: torch.Tensor, v: float, lamb: float, iter: int
):
    """Computes Generalised Geodesic Distance using FastGeodis raster scanning.
    For more details on generalised geodesic distance, check the following reference:

    Criminisi, Antonio, Toby Sharp, and Andrew Blake.
    "Geos: Geodesic image segmentation."
    European Conference on Computer Vision, Berlin, Heidelberg, 2008.

    The function expects input as torch.Tensor, which can be run on CPU or GPU depending on Tensor's device location

    Args:
        image: input image, can be grayscale or multiple channels.
        softmask: softmask in range [0, 1] with seed information.
        v: weighting factor for establishing relationship between unary and spatial distances.
        lamb: weighting factor between 0.0 and 1.0. 0.0 returns euclidean distance, whereas 1.0 returns geodesic distance
        iter: number of passes of the iterative distance transform method

    Returns:
        torch.Tensor with distance transform
    """
    return FastGeodis.generalised_geodesic2d(image, softmask, v, lamb, 1 - lamb, iter)


def evaluate_geodesic_distance2d(image, seed_pos):
    # get image and create seed image
    Image = np.asanyarray(image, np.float32)
    Seed = np.zeros((Image.shape[0], Image.shape[1]), np.float32)
    Seed[seed_pos[0]][seed_pos[1]] = 1

    # run and time each method
    iterations = 2
    v = 1e10
    lamb = 1.0

    tic = time.time()
    fastmarch_output = GeodisTK.geodesic2d_fast_marching(Image, Seed.astype(np.uint8))
    fastmarch_time = time.time() - tic

    tic = time.time()
    geodistkraster_output = geodesic_distance_2d(
        Image, Seed.astype(np.uint8), lamb, iterations
    )
    geodistkraster_time = time.time() - tic

    if Image.ndim == 3:
        Image = np.moveaxis(Image, -1, 0)
    else:
        Image = np.expand_dims(Image, 0)

    device = "cpu"
    It = torch.from_numpy(Image).unsqueeze_(0).to(device)
    St = (
        torch.from_numpy(1 - Seed.astype(np.float32))
        .unsqueeze_(0)
        .unsqueeze_(0)
        .to(device)
    )

    tic = time.time()
    fastraster_output_cpu = np.squeeze(
        fastgeodis_generalised_geodesic_distance_2d(It, St, v, lamb, iterations)
        .cpu()
        .numpy()
    )
    fastraster_time_cpu = time.time() - tic

    device = "cuda" if It.shape[1] == 1 and torch.cuda.is_available() else None
    if device:
        It = It.to(device)
        St = St.to(device)

        tic = time.time()
        fastraster_output_gpu = np.squeeze(
            fastgeodis_generalised_geodesic_distance_2d(It, St, v, lamb, iterations)
            .cpu()
            .numpy()
        )
        fastraster_time_gpu = time.time() - tic

    print("Runtimes:")
    print(
        "Fast Marching: {:.6f} s \nGeodisTk raster: {:.6f} s \nFastGeodis CPU raster: {:.6f} s".format(
            fastmarch_time, geodistkraster_time, fastraster_time_cpu
        )
    )

    if device:
        print("FastGeodis GPU raster: {:.6f} s".format(fastraster_time_gpu))

    plt.figure(figsize=(18, 6))
    plt.subplot(2, 4, 1)
    plt.imshow(image, cmap="gray")
    plt.autoscale(False)
    plt.plot([seed_pos[0]], [seed_pos[1]], "ro")
    plt.axis("off")
    plt.title("(a) Input image")

    plt.subplot(2, 4, 2)
    plt.imshow(fastmarch_output)
    plt.axis("off")
    plt.title("(b) Fast Marching | ({:.4f} s)".format(fastmarch_time))

    plt.subplot(2, 4, 3)
    plt.imshow(fastraster_output_cpu)
    plt.axis("off")
    plt.title("(c) FastGeodis (cpu) | ({:.4f} s)".format(fastraster_time_cpu))

    plt.subplot(2, 4, 6)
    plt.imshow(geodistkraster_output)
    plt.axis("off")
    plt.title("(d) GeodisTK | ({:.4f} s)".format(geodistkraster_time))

    if device:
        plt.subplot(2, 4, 7)
        plt.imshow(fastraster_output_gpu)
        plt.axis("off")
        plt.title("(e) FastGeodis (gpu) | ({:.4f} s)".format(fastraster_time_gpu))

    diff = (
        abs(fastmarch_output - fastraster_output_cpu) / (fastmarch_output + 1e-7) * 100
    )
    plt.subplot(2, 4, 4)
    plt.imshow(diff)
    plt.axis("off")
    plt.title(
        "(f) Fast Marching vs. FastGeodis (cpu)\ndiff: max: {:.4f} | min: {:.4f}".format(
            np.max(diff), np.min(diff)
        )
    )

    if device:
        diff = (
            abs(fastmarch_output - fastraster_output_gpu)
            / (fastmarch_output + 1e-7)
            * 100
        )
        plt.subplot(2, 4, 8)
        plt.imshow(diff)
        plt.axis("off")
        plt.title(
            "(g) Fast Marching vs. FastGeodis (gpu)\ndiff: max: {:.4f} | min: {:.4f}".format(
                np.max(diff), np.min(diff)
            )
        )

    # plt.colorbar()
    # plt.show()

    plt.figure(figsize=(14, 4))
    plt.subplot(1, 3, 1)
    plt.hist2d(fastmarch_output.flatten(), geodistkraster_output.flatten(), bins=50)
    plt.xlabel("Fast Marching")
    plt.ylabel("GeodisTK")
    plt.title("Joint histogram\nFast Marching vs. GeodisTK")
    # plt.gca().set_aspect("equal", adjustable="box")

    plt.title("Joint histogram\nFast Marching vs. FastGeodis (cpu)")
    plt.subplot(1, 3, 2)
    plt.hist2d(fastmarch_output.flatten(), fastraster_output_cpu.flatten(), bins=50)
    plt.xlabel("Fast Marching")
    plt.ylabel("FastGeodis (cpu)")
    # plt.gca().set_aspect("equal", adjustable="box")

    if device:
        plt.subplot(1, 3, 3)
        plt.hist2d(fastmarch_output.flatten(), fastraster_output_gpu.flatten(), bins=50)
        plt.xlabel("Fast Marching")
        plt.ylabel("FastGeodis (gpu)")
        plt.title("Joint histogram\nFast Marching vs. FastGeodis (gpu)")
        # plt.gca().set_aspect("equal", adjustable="box")

    plt.tight_layout()
    # plt.colorbar()
    plt.show()


def demo_geodesic_distance2d(image):
    # make image bigger to check how much workload each method can take
    scale = 6
    scaled_image_size = [x * scale for x in image.size]
    image = image.resize(scaled_image_size)
    seed_position = [100 * scale, 100 * scale]
    evaluate_geodesic_distance2d(image, seed_position)


if __name__ == "__main__":
    # "gray" or "color"
    example = "gray"

    if example == "gray":
        image = Image.open("data/img2d.png").convert("L")
    elif example == "color":
        image = Image.open("data/ISIC_546.jpg")

    demo_geodesic_distance2d(image)