import numpy as np


def dist(pos1, pos2):
    return np.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)


def _test_indices(i, j, diagonal=False, extended=False):
    if extended:
        # Count any cells in a 5x5 area centred on the current i, j cell as being adjacent.
        indices = []
        for ii in range(i - 2, i + 3):
            for jj in range(j - 2, j + 3):
                indices.append((ii, jj))
    else:
        # Standard, cells sharing a border are adjacent.
        indices = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
        if diagonal:
            # Diagonal cells considered adjacent.
            indices += [(i-1, j-1), (i-1, j+1), (i+1, j-1), (i+1, j+1)]
    return indices


def label_clds(mask, diagonal=False, wrap=True, min_cells=0):
    """
    Label contiguous grid-cells with a given index - 1-max_label.

    :param np.ndarray mask: 2D mask of True/False representing (thresholded) clouds.
    :param bool diagonal: Whether to treat diagonal cells as contiguous.
    :param bool wrap: Whether to wrap on edge.
    :param int min_cells: Minimum number of grid-cells to include in a cloud.
    :return tuple(int, np.ndarray): max_label and 2D array of ints.
    """
    labels = np.zeros_like(mask, dtype=np.int32)
    max_label = 0
    acceptable_blobs = []
    for j in range(mask.shape[1]):
        for i in range(mask.shape[0]):
            if labels[i, j]:
                continue

            if mask[i, j]:
                blob_count = 1
                max_label += 1
                labels[i, j] = max_label
                outers = [(i, j)]
                while outers:
                    new_outers = []
                    for ii, jj in outers:
                        for it, jt in _test_indices(ii, jj, diagonal):
                            if not wrap:
                                if it < 0 or it >= mask.shape[0] or \
                                                jt < 0 or jt >= mask.shape[1]:
                                    continue
                            else:
                                it %= mask.shape[0]
                                jt %= mask.shape[1]

                            if not labels[it, jt] and mask[it, jt]:
                                blob_count += 1
                                new_outers.append((it, jt))
                                labels[it, jt] = max_label
                    outers = new_outers

                if blob_count >= min_cells:
                    acceptable_blobs.append(max_label)

    if min_cells > 0:
        out_blobs = np.zeros_like(labels)
        num_acceptable_blobs = 1
        for blob_index in acceptable_blobs:
            out_blobs[labels == blob_index] = num_acceptable_blobs
            num_acceptable_blobs += 1

        return num_acceptable_blobs, out_blobs
    else:
        return max_label, labels


def grow(a, diagonal=False):
    """
    Grow original array by one cell.

    :param a: input array.
    :param diagonal: whether to grow in diagonal direction.
    :return: new array that has been extended in each dir by one unit.
    """
    anew = a.copy()
    for i, j in _test_indices(0, 0, diagonal):
        anew |= np.roll(np.roll(a, i, axis=0), j, axis=1)
    return anew

