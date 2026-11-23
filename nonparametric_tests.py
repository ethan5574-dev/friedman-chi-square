"""Friedman and Pearson chi-square tests implemented with the standard library."""

import math
from dataclasses import dataclass
from itertools import permutations, product
from numbers import Integral, Real
from typing import Iterable, Sequence
from warnings import warn


@dataclass(frozen=True)
class FriedmanResult:
    statistic: float
    df: int
    p_value: float
    p_method: str
    ranks: tuple[tuple[float, ...], ...]
    rank_sums: tuple[float, ...]
    tie_correction: float
    kendall_w: float


@dataclass(frozen=True)
class PearsonResult:
    statistic: float
    df: int
    p_value: float
    expected: tuple[tuple[float, ...], ...]
    contributions: tuple[tuple[float, ...], ...]


def chi_square_sf(statistic: float, df: int) -> float:
    """Return P(χ²_df >= statistic) for a positive integer df."""
    if not isinstance(df, Integral) or isinstance(df, bool) or df < 1:
        raise ValueError("df phải là số nguyên dương.")
    if math.isnan(statistic) or statistic < 0:
        raise ValueError("Thống kê phải không âm.")
    if statistic == math.inf:
        return 0.0

    x = statistic / 2
    if x == 0:
        return 1.0

    # Q(a+1, x) = Q(a, x) + exp(a*log(x) - x - lgamma(a+1)).
    # Integer df makes a = df/2 an integer or a half-integer.
    a0 = 0.5 if df % 2 else 1.0
    base = math.erfc(math.sqrt(x)) if df % 2 else math.exp(-x)
    log_x = math.log(x)
    shapes = (a0 + step for step in range((df - 1) // 2))
    terms = (math.exp(a * log_x - x - math.lgamma(a + 1)) for a in shapes)
    return min(1.0, base + math.fsum(terms))


def _matrix(rows: Iterable[Iterable[Real]], min_cols: int) -> tuple[tuple[Real, ...], ...]:
    data = tuple(tuple(row) for row in rows)
    if len(data) < 2 or len(data[0]) < min_cols:
        raise ValueError(f"Cần ít nhất 2 hàng và {min_cols} cột.")
    if any(len(row) != len(data[0]) for row in data):
        raise ValueError("Các hàng phải có cùng số cột.")
    return data


def _double_ranks(row: Sequence[Real]) -> tuple[tuple[int, ...], int]:
    """Return twice the midranks and the sum of t³ − t for ties in a row."""
    order = sorted(range(len(row)), key=row.__getitem__)
    ranks = [0] * len(row)
    ties = 0
    start = 0
    while start < len(row):
        stop = start + 1
        while stop < len(row) and row[order[stop]] == row[order[start]]:
            stop += 1
        # The first and last one-based ranks in this run are start+1 and stop.
        for index in order[start:stop]:
            ranks[index] = start + 1 + stop
        t = stop - start
        ties += t**3 - t
        start = stop
    return tuple(ranks), ties


def _rank_score(rows: Sequence[Sequence[int]], center: int) -> int:
    return sum((sum(column) - center) ** 2 for column in zip(*rows))


def _friedman_exact_p(ranks: Sequence[tuple[int, ...]], center: int, observed: int) -> float:
    # Count labeled permutations, including duplicate rank vectors from ties.
    # Every permutation of labels within a block is equally likely under H₀.
    n, k = len(ranks), len(ranks[0])
    per_block = math.factorial(k)
    total = per_block**n
    if total > 500_000:
        raise ValueError("Quá 500.000 hoán vị nhãn. Dùng method='asymptotic' cho bảng này.")
    choices = [tuple(permutations(row)) for row in ranks]
    extreme = sum(_rank_score(rows, center) >= observed for rows in product(*choices))
    return extreme / total


def friedman(rows: Iterable[Iterable[Real]], *, method: str = "asymptotic") -> FriedmanResult:
    """Test k >= 3 conditions measured within each independent complete block.

    Use method='exact' for small designs where labels are exchangeable within
    blocks under the null. Otherwise the p-value uses a chi-square approximation.
    """
    if method not in {"exact", "asymptotic"}:
        raise ValueError("method phải là 'exact' hoặc 'asymptotic'.")
    data = _matrix(rows, min_cols=3)
    if any(
        isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value)
        for row in data
        for value in row
    ):
        raise ValueError("Friedman cần giá trị số hữu hạn ở mọi ô.")

    n, k = len(data), len(data[0])
    ranked = [_double_ranks(row) for row in data]
    ranks = [row for row, _ in ranked]
    tie_base = n * k * (k**2 - 1)
    tie_sum = sum(ties for _, ties in ranked)
    if tie_sum == tie_base:
        raise ValueError("Mọi khối đều đồng hạng hoàn toàn nên không thể tính Friedman Q.")

    correction = (tie_base - tie_sum) / tie_base
    center = n * (k + 1)
    score = _rank_score(ranks, center)
    q = (3 * score) / (n * k * (k + 1) * correction)
    df = k - 1
    p = _friedman_exact_p(ranks, center, score) if method == "exact" else chi_square_sf(q, df)
    return FriedmanResult(
        statistic=q,
        df=df,
        p_value=p,
        p_method=method,
        ranks=tuple(tuple(rank / 2 for rank in row) for row in ranks),
        rank_sums=tuple(sum(column) / 2 for column in zip(*ranks)),
        tie_correction=correction,
        kendall_w=q / (n * df),
    )


def _counts(values: Iterable[int]) -> tuple[int, ...]:
    counts = tuple(values)
    if any(
        not isinstance(value, Integral) or isinstance(value, bool) or value < 0
        for value in counts
    ):
        raise ValueError("Tần số quan sát phải là số nguyên không âm.")
    return tuple(int(value) for value in counts)


def _pearson(
    observed: tuple[tuple[int, ...], ...], expected: tuple[tuple[float, ...], ...], df: int
) -> PearsonResult:
    contributions = tuple(
        tuple(((o - e) / math.sqrt(e)) ** 2 for o, e in zip(o_row, e_row))
        for o_row, e_row in zip(observed, expected)
    )
    statistic = math.fsum(term for row in contributions for term in row)
    return PearsonResult(statistic, df, chi_square_sf(statistic, df), expected, contributions)


def chi_square_goodness_of_fit(
    observed: Iterable[int], probabilities: Iterable[float]
) -> PearsonResult:
    """Test observed counts against probabilities specified before sampling."""
    counts = _counts(observed)
    probs = tuple(probabilities)
    if len(counts) < 2 or len(probs) != len(counts):
        raise ValueError("Cần cùng số tần số và xác suất, với ít nhất 2 loại.")
    if any(
        isinstance(p, bool) or not isinstance(p, Real) or not math.isfinite(p) or not 0 < p <= 1
        for p in probs
    ):
        raise ValueError("Mỗi xác suất phải hữu hạn, dương và không vượt quá 1.")
    prob_total = math.fsum(probs)
    if not math.isclose(prob_total, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("Tổng xác suất phải bằng 1.")
    total = sum(counts)
    if total == 0:
        raise ValueError("Tổng tần số phải dương.")
    expected = tuple(total * (p / prob_total) for p in probs)
    if min(expected) < 5:
        warn("Có E < 5. Xấp xỉ chi bình phương có thể kém.", stacklevel=2)
    return _pearson((counts,), (expected,), len(counts) - 1)


def chi_square_contingency(table: Iterable[Iterable[int]]) -> PearsonResult:
    """Pearson test for independence or homogeneity, without Yates correction."""
    observed = tuple(_counts(row) for row in _matrix(table, min_cols=2))
    row_totals = [sum(row) for row in observed]
    col_totals = [sum(column) for column in zip(*observed)]
    if 0 in row_totals or 0 in col_totals:
        raise ValueError("Mỗi hàng và cột phải có tổng dương.")
    total = sum(row_totals)
    expected = tuple(
        tuple(row * col / total for col in col_totals) for row in row_totals
    )
    flat = [value for row in expected for value in row]
    if min(flat) < 1 or 5 * sum(value < 5 for value in flat) > len(flat):
        warn("Có E < 1 hoặc hơn 20% số ô có E < 5. Xấp xỉ có thể kém.", stacklevel=2)
    df = (len(row_totals) - 1) * (len(col_totals) - 1)
    return _pearson(observed, expected, df)
