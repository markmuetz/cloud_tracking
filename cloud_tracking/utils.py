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


def _test_indices_3d(k, i, j, k_limit, k_start, diagonal=False, extended=False):
    if extended:
        # Count any cells in a 5x5 area centred on the current i, j cell as being adjacent.
        indices = []
        for kk in range(k - 2, k + 3):
            for ii in range(i - 2, i + 3):
                for jj in range(j - 2, j + 3):
                    indices.append((ii, jj, kk))
    else:
        # Standard, cells sharing a border are adjacent.
        if k > k_start and k < k_limit:
           indices = [(k, i-1, j), (k, i+1, j), (k, i, j-1), (k, i, j+1), (k-1, i, j), (k+1, i, j)]
           if diagonal:
               # Diagonal cells considered adjacent.
               indices += [(k, i-1, j-1), (k, i-1, j+1), (k, i+1, j-1), (k, i+1, j+1), (k-1, i-1, j), (k-1, i+1, j), (k-1, i, j-1), (k-1, i, j+1), (k+1, i-1, j), (k+1, i+1, j), (k+1, i, j-1), (k+1, i, j+1)]

        elif k <= k_start:
           indices = [(k, i-1, j), (k, i+1, j), (k, i, j-1), (k, i, j+1), (k+1, i, j)]
           if diagonal:
               # Diagonal cells considered adjacent.
               indices += [(k, i-1, j-1), (k, i-1, j+1), (k, i+1, j-1), (k, i+1, j+1), (k+1, i-1, j), (k+1, i+1, j), (k+1, i, j-1), (k+1, i, j+1)]

        elif k >= k_limit:
           indices = [(k, i-1, j), (k, i+1, j), (k, i, j-1), (k, i, j+1), (k-1, i, j)]
           if diagonal:
               # Diagonal cells considered adjacent.
               indices += [(k, i-1, j-1), (k, i-1, j+1), (k, i+1, j-1), (k, i+1, j+1), (k-1, i-1, j), (k-1, i+1, j), (k-1, i, j-1), (k-1, i, j+1)]

    return indices



def label_clds_3d(mask, diagonal=False, wrap=True, min_cells=0, k_start=1):
    """
    Label contiguous grid-cells with a given index - 1-max_label.
    :param np.ndarray mask: 3D mask of True/False representing (thresholded) clouds.
    :param bool diagonal: Whether to treat diagonal cells as contiguous.
    :param bool wrap: Whether to wrap on edge.
    :param int min_cells: Minimum number of grid-cells to include in a cloud.
    :return tuple(int, np.ndarray): max_label and 3D array of ints.
    """
    labels = np.zeros_like(mask, dtype=np.int32)
    max_label = 0
    acceptable_blobs = []
    for k in range(k_start, mask.shape[0]-1):
        for j in range(mask.shape[2]):
            for i in range(mask.shape[1]):
                if labels[k, i, j]:
                    continue

                if mask[k, i, j]:
                    blob_count = 1
                    max_label += 1
                    labels[k, i, j] = max_label
                    outers = [(k, i, j)]
                    while outers:
                        new_outers = []
                        for kk, ii, jj in outers:
                            for kt, it, jt in _test_indices_3d(kk, ii, jj, mask.shape[0]-1, k_start, diagonal):
                                if not wrap:
                                    if it < 0 or it >= mask.shape[1] or \
                                                    jt < 0 or jt >= mask.shape[2]:
                                        continue
                                else:
                                    it %= mask.shape[1]
                                    jt %= mask.shape[2]

                                if kt >= mask.shape[0] or kt < 0:
                                   print kt, 'out of range of vertical domain'

                                if not labels[kt, it, jt] and mask[kt, it, jt]:
                                    blob_count += 1
                                    new_outers.append((kt, it, jt))
                                    labels[kt, it, jt] = max_label
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


def grow_3d(a, diagonal=False):
    """
    Grow original array by one cell.
    :param a: input array.
    :param diagonal: whether to grow in diagonal direction.
    :return: new array that has been extended in each dir by one unit.
    """
    anew = a.copy()
    for k, i, j in _test_indices_3d(0, 0, 0, 0, a.shape[0], diagonal):
        anew |= np.roll(np.roll(np.roll(a, i, axis=0), j, axis=1), k, axis=2)
    return anew

