from typing import Tuple, Optional, List

import numpy as np
from labml.internal.analytics import cache as _cache
from labml.internal.analytics.altair import density as _density
from labml.internal.analytics.altair import scatter as _scatter
from labml.internal.analytics.indicators import IndicatorCollection as _IndicatorCollection


class IndicatorCollection(_IndicatorCollection):
    r"""
    You can get a indicator collection with :func:`runs`.

    >>> from labml import analytics
    >>> indicators = analytics.runs('1d3f855874d811eabb9359457a24edc8')

    You can reference individual indicators as attributes.

    >>> train_loss = indicators.train_loss

    You can add multiple indicator collections

    >>> losses = indicators.train_loss + indicators.validation_loss
    """
    pass


def runs(*uuids: str):
    r"""
    This is used to analyze runs.
    It fetches all the log indicators.

    Arguments:
        uuids (str): UUIDs of the runs. You can
            get this from `dashboard <https://github.com/lab-ml/lab_dashboard>`_

    Example:
        >>> from labml import analytics
        >>> indicators = analytics.runs('1d3f855874d811eabb9359457a24edc8')
    """

    indicators = None
    for r in uuids:
        run = _cache.get_run(r)
        indicators = indicators + run.indicators

    return indicators


def get_run(uuid: str):
    r"""
    Returns ``Run`` object
    """
    return _cache.get_run(uuid)


def set_preferred_db(db: str):
    assert db in ['tensorboard', 'sqlite']


def get_data(indicators: IndicatorCollection):
    data = {}
    for i, ind in enumerate(indicators):
        d = _cache.get_indicator_data(ind)
        data[ind.key] = d[:, [0, 5]]

    return data


def _get_series(indicators: IndicatorCollection):
    series = []
    names = []
    for i, ind in enumerate(indicators):
        d = _cache.get_indicator_data(ind)
        if d is not None:
            series.append(d)
            names.append(ind.key)

    return series, names


def distribution(indicators: IndicatorCollection, *,
                 levels: int = 5, alpha: int = 0.6,
                 height: int = 400, width: int = 800, height_minimap: int = 100):
    r"""
    Creates a distribution plot distribution with Altair

    Arguments:
        indicators(IndicatorCollection): Set of indicators to be plotted

        levels: how many levels of the distribution to be plotted
        alpha: opacity of the distribution
        height: height of the visualization
        width: width of the visualization
        height_minimap: height of the view finder

    Return:
        The Altair visualization

    Example:
        >>> from labml import analytics
        >>> indicators = analytics.runs('1d3f855874d811eabb9359457a24edc8')
        >>> analytics.distribution(indicators)
    """

    series, names = _get_series(indicators)

    if not series:
        raise ValueError("No series found")

    return _density.render_density_minimap_multiple(
        series,
        names=names,
        levels=levels,
        alpha=alpha,
        width=width,
        height=height,
        height_minimap=height_minimap)


def scatter(indicators: IndicatorCollection, x: IndicatorCollection, *,
            noise: Optional[Tuple[float, float]] = None,
            height: int = 400, width: int = 800, height_minimap: int = 100):
    r"""
    Creates a scatter plot with Altair

    Arguments:
        indicators(IndicatorCollection): Set of indicators to be plotted
        x(IndicatorCollection): Indicator for x-axis

        noise: Noise to be added to spread out the scatter plot
        height: height of the visualization
        width: width of the visualization
        height_minimap: height of the view finder

    Return:
        The Altair visualization

    Example:
        >>> from labml import analytics
        >>> indicators = analytics.runs('1d3f855874d811eabb9359457a24edc8')
        >>> analytics.scatter(indicators.validation_loss, indicators.train_loss)
    """

    series, names = _get_series(indicators)
    x_series, x_names = _get_series(x)

    if len(x_series) != 1:
        raise ValueError("There should be exactly one series for x-axis")
    if not series:
        raise ValueError("No series found")

    return _scatter.scatter(
        series, x_series[0],
        names=names,
        x_name=x_names[0],
        width=width,
        height=height,
        height_minimap=height_minimap,
        noise=noise)


def indicator_data(indicators: IndicatorCollection) -> Tuple[List[np.ndarray], List[str]]:
    r"""
    Returns a tuple of a list of series and a list of names of series.
    Each series, `S` is a timeseries of histograms of shape `[T, 10]`,
    where `T` is the number of timesteps.
    `S[:, 0]` is the `global_step`.
    `S[:, 1:10]` represents the distribution at basis points
     `0, 6.68, 15.87, 30.85, 50.00, 69.15, 84.13, 93.32, 100.00`.

    Example:
        >>> from labml import analytics
        >>> indicators = analytics.runs('1d3f855874d811eabb9359457a24edc8')
        >>> analytics.indicator_data(indicators)
    """

    series, names = _get_series(indicators)

    if not series:
        raise ValueError("No series found")

    return series, names


def _get_artifacts(indicators: IndicatorCollection):
    series = []
    names = []
    for i, ind in enumerate(indicators):
        d = _cache.get_artifact_data(ind)
        if d is not None:
            series.append(d)
            names.append(ind.key)

    return series, names


def artifact_data(indicators: IndicatorCollection) -> Tuple[List[any], List[str]]:
    r"""
    Returns a tuple of a list of series and a list of names of series.
    Each series, ``S`` is a timeseries of histograms of shape ``[T, 10]``,
    where ``T`` is the number of timesteps.
    ``S[:, 0]`` is the `global_step`.
    ``S[:, 1:10]`` represents the distribution at basis points:
    ``0, 6.68, 15.87, 30.85, 50.00, 69.15, 84.13, 93.32, 100.00``.

    Example:
        >>> from labml import analytics
        >>> indicators = analytics.runs('1d3f855874d811eabb9359457a24edc8')
        >>> analytics.artifact_data(indicators)
    """

    series, names = _get_artifacts(indicators)

    if not series:
        raise ValueError("No series found")

    return series, names
