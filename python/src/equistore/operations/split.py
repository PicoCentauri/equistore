from typing import List, Union

from ..block import TensorBlock
from ..labels import Labels
from ..tensor import TensorMap
from .slice import _slice_block


def split(
    tensor: TensorMap,
    axis: str,
    grouped_idxs: List[Labels],
) -> List[TensorMap]:
    """
    Splits an input :py:class:`TensorMap` into mutliple :py:class:`TensorMap`
    objects based on some specified groups of indices, along either the
    "samples" or "properties" ``axis``. The number of returned
    :py:class:`TensorMap`s is equal to the number of :py:class:`Labels` objects
    passed in ``grouped_idxs``. Each returned :py:class`TensorMap` will have the
    same keys and number of blocks at the input ``tensor``, but with the
    dimensions of the blocks reduced to only contain the specified indices for
    the corresponding group.

    For example, to split a tensor along the "samples" axis, according to the
    "structure" index, where structures 0, 6, and 7 are in the first returned
    :py:class`TensorMap`; 2, 3, and 4 in the second; and 1, 5, 8, 9, and 10 in
    the third:

    .. code-block:: python

        split_tensor = split(
            tensor,
            axis="samples",
            grouped_idxs=[
                Labels(
                    names=["structure"],
                    values=np.array([[0], [6], [7]])
                ),
                Labels(
                    names=["structure"],
                    values=np.array([[2], [3], [4]])
                ),
                Labels(
                    names=["structure"],
                    values=np.array([[1], [5], [8], [9], [10]])
                ),
            ]
        )

    :param tensor: a :py:class:`TensorMap` to be split
    :param axis: a str, either "samples" or "properties", that indicates the
        :py:class:`TensorBlock` axis along which the named index (or indices) in
        ``grouped_idxs`` belongs. Each :py:class:`TensorBlock` in each returned
        :py:class:`TensorMap` could have a reduced dimension along this axis,
        but the other axes will remain the same size.
    :param grouped_idxs: a list of :py:class:`Labels` containing the names and
        values of the indices along the specified ``axis`` which should be in
        each respective output :py:class:`TensorMap`.

    :return: a list of:py:class:`TensorMap` that corresponds to the split input
        ``tensor``. Each tensor in the returned list contains only the named
        indices in the respective py:class:`Labels` object of ``grouped_idxs``.
    """
    # Check input args
    if not isinstance(tensor, TensorMap):
        raise TypeError("``tensor`` should be an equistore ``TensorMap``")
    _check_args(tensor, axis, grouped_idxs)

    all_new_blocks = {group_i: [] for group_i in range(len(grouped_idxs))}
    for key in tensor.keys:
        new_blocks = _split_block(tensor[key], axis, grouped_idxs)

        for group_i, new_block in enumerate(new_blocks):
            all_new_blocks[group_i].append(new_block)

    return [
        TensorMap(keys=tensor.keys, blocks=all_new_blocks[group_i])
        for group_i in range(len(grouped_idxs))
    ]


def split_block(
    block: TensorBlock,
    axis: str,
    grouped_idxs: List[Labels],
) -> List[TensorBlock]:
    """
    Splits an input :py:class:`TensorBlock` into mutliple
    :py:class:`TensorBlock` objects based on some specified ``grouped_idxs``,
    along either the "samples" or "properties" ``axis``. The number of returned
    :py:class:`TensorBlock`s is equal to the number of :py:class:`Labels`
    objects passed in ``grouped_idxs``. Each returned :py:class`TensorBlock`
    will have the same keys and number of blocks at the input ``tensor``, but
    with the dimensions of the blocks reduced to only contain the specified
    indices for the corresponding group.

    For example, to split a block along the "samples" axis, according to the
    "structure" index, where structures 0, 6, and 7 are in the first returned
    :py:class`TensorMap`; 2, 3, and 4 in the second; and 1, 5, 8, 9, and 10 in
    the third:

    .. code-block:: python

        split_tensorblock = split_block(
            block,
            axis="samples",
            grouped_idxs=[
                Labels(
                    names=["structure"],
                    values=np.array([[0], [6], [7]])
                ),
                Labels(
                    names=["structure"],
                    values=np.array([[2], [3], [4]])
                ),
                Labels(
                    names=["structure"],
                    values=np.array([[1], [5], [8], [9], [10]])
                ),
            ]
        )

    :param block: a :py:class:`TensorBlock` to be split
    :param axis: a str, either "samples" or "properties", that indicates the
        :py:class:`TensorBlock` axis along which the named index (or indices) in
        ``grouped_idxs`` belongs. Each :py:class:`TensorBlock` returned could
        have a reduced dimension along this axis, but the other axes will remain
        the same size.
    :param grouped_idxs: a list of :py:class:`Labels` containing the names and
        values of the indices along the specified ``axis`` which should be in
        each respective output :py:class:`TensorBlock`.

    :return: a list of:py:class:`TensorBlock` that corresponds to the split
        input ``block``. Each block in the returned list contains only the named
        indices in the respective py:class:`Labels` object of ``grouped_idxs``.
    """
    # Check input args
    if not isinstance(block, TensorBlock):
        raise TypeError("``block`` should be an equistore ``TensorBlock``")
    _check_args(block, axis, grouped_idxs)

    return _split_block(block, axis, grouped_idxs)


def _split_block(
    block: TensorBlock,
    axis: str,
    grouped_idxs: List[Labels],
) -> List[TensorBlock]:
    """
    Splits a TensorBlock into mutliple blocks, as in the public function
    :py:func:`split_block` but with no input checks. Note that the block is
    currently split into N new blocks by performing N number of slice
    operations. There may be a more efficient way of doing it, but this is not
    yet implemented.
    """
    new_blocks = []
    for indices in grouped_idxs:
        # Perfom the slice, either along the samples or properties axis
        if axis == "samples":
            new_block = _slice_block(block, samples=indices)
        else:  # properties
            new_block = _slice_block(block, properties=indices)
        new_blocks.append(new_block)

    return new_blocks


def _check_args(
    tensor: Union[TensorMap, TensorBlock], axis: str, grouped_idxs: List[Labels]
):
    """
    Checks the arguments passed to :py:func:`split` and :py:func:`split_block`.
    """
    # Check types
    if not isinstance(axis, str):
        raise TypeError("``axis`` should be passed as a ``str``")
    if axis not in ["samples", "properties"]:
        raise ValueError("must pass ``axis`` as either 'samples' or 'properties'")
    if not isinstance(grouped_idxs, list):
        raise TypeError(
            "``grouped_idxs`` should be passed as a ``list`` of equistore ``Labels``"
        )
    # If passed as an empty list, return now
    if len(grouped_idxs) == 0:
        return
    for idxs in grouped_idxs:
        if not isinstance(idxs, Labels):
            raise TypeError(
                "each element in ``grouped_idxs`` must"
                + " be an equistore ``Labels`` object"
            )
    # Check the Labels names are equivalent for all Labels in grouped_idxs
    ref_names = grouped_idxs[0].names
    if len(grouped_idxs) > 1:
        for idxs in grouped_idxs[1:]:
            if idxs.names != ref_names:
                raise ValueError(
                    "the names of all ``Labels`` passed in ``grouped_idxs``"
                    + " must be equivalent"
                )
    # Get a single block
    block = tensor.block(0) if isinstance(tensor, TensorMap) else tensor

    # Check the names in grouped_idxs Labels are contained within the names for
    # the block
    names = block.samples.names if axis == "samples" else block.properties.names
    for ref_i, ref_name in enumerate(ref_names):
        if ref_name not in names:
            raise ValueError(
                f"the name ``{ref_name}`` passed in a Labels object at position {ref_i}"
                + f" of ``grouped_idxs`` does not appear in the ``{axis}`` names"
                + " of the input tensor"
            )
