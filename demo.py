"""Run six simulated examples with Python 3.9 or later."""

import argparse
from dataclasses import dataclass
from math import factorial
from typing import Union

from nonparametric_tests import (
    FriedmanResult,
    PearsonResult,
    chi_square_contingency,
    chi_square_goodness_of_fit,
    chi_square_sf,
    friedman,
)


ALPHA = 0.05


@dataclass(frozen=True)
class Example:
    title: str
    null: str
    columns: tuple[str, ...]
    labels: tuple[str, ...]
    observed: tuple[tuple[int, ...], ...]
    probabilities: tuple[float, ...] = ()


EXAMPLES = {
    "F1": Example(
        "Thời gian chạy của ba thuật toán",
        "Ba thuật toán có cùng phân phối thời gian trong mỗi bộ dữ liệu.",
        ("A", "B", "C"),
        ("Bộ 1", "Bộ 2", "Bộ 3", "Bộ 4", "Bộ 5", "Bộ 6"),
        ((12, 10, 8), (15, 13, 11), (11, 10, 9), (19, 16, 13), (16, 14, 15), (18, 17, 12)),
    ),
    "F2": Example(
        "Điểm hài lòng của ba giao diện",
        "Ba giao diện có cùng phân phối điểm trong mỗi người dùng.",
        ("A", "B", "C"),
        ("Người 1", "Người 2", "Người 3", "Người 4", "Người 5"),
        ((5, 5, 4), (4, 5, 4), (3, 4, 4), (5, 4, 5), (4, 5, 3)),
    ),
    "F3": Example(
        "Điểm cùng sinh viên dưới bốn kiểu ôn tập",
        "Bốn kiểu ôn tập có cùng phân phối điểm trong mỗi sinh viên.",
        ("A", "B", "C", "D"),
        ("SV 1", "SV 2", "SV 3", "SV 4"),
        ((80, 82, 84, 86), (76, 72, 74, 70), (89, 85, 83, 87), (73, 77, 71, 75)),
    ),
    "C1": Example(
        "Độ phù hợp với phân phối xúc xắc công bằng",
        "Mỗi mặt có xác suất xuất hiện bằng 1/6.",
        ("1", "2", "3", "4", "5", "6"),
        ("Xúc xắc",),
        ((14, 22, 18, 20, 24, 22),),
        (1 / 6,) * 6,
    ),
    "C2": Example(
        "Mối liên hệ giữa phương pháp học và kết quả",
        "Phương pháp học và kết quả thi độc lập.",
        ("Đạt", "Chưa đạt"),
        ("Nhóm A", "Nhóm B"),
        ((36, 14), (24, 26)),
    ),
    "C3": Example(
        "Phân phối lựa chọn màu tại ba chi nhánh",
        "Ba chi nhánh có cùng phân phối lựa chọn màu.",
        ("Xanh", "Trắng", "Đen"),
        ("CN 1", "CN 2", "CN 3"),
        ((30, 15, 5), (20, 20, 10), (10, 25, 15)),
    ),
}


def analyze(case_id: str) -> Union[FriedmanResult, PearsonResult]:
    example = EXAMPLES[case_id]
    if case_id.startswith("F"):
        return friedman(example.observed, method="exact")
    if example.probabilities:
        return chi_square_goodness_of_fit(example.observed[0], example.probabilities)
    return chi_square_contingency(example.observed)


def _print_table(title, columns, labels, rows):
    print(title)
    print(f"{'':>12}" + "".join(f"{col:>12}" for col in columns))
    for label, row in zip(labels, rows):
        print(f"{label:>12}" + "".join(f"{value:>12.5g}" for value in row))


def run(case_id: str) -> None:
    example = EXAMPLES[case_id]
    result = analyze(case_id)
    print(f"\n{case_id}  {example.title}")
    print(f"H₀  {example.null}")
    _print_table("Dữ liệu quan sát", example.columns, example.labels, example.observed)
    if isinstance(result, FriedmanResult):
        _print_table("Hạng theo từng khối", example.columns, example.labels, result.ranks)
        _print_table("Tổng hạng", example.columns, ("R",), (result.rank_sums,))
        n, k = len(example.observed), len(example.columns)
        p_asymptotic = chi_square_sf(result.statistic, result.df)
        print(f"C = {result.tie_correction:.6g}    W = {result.kendall_w:.6g}")
        print(f"Q = {result.statistic:.6g}    df tham chiếu = {result.df}")
        print(f"p hoán vị = {result.p_value:.6g}    số hoán vị = {factorial(k) ** n:,}")
        print(f"p xấp xỉ chi bình phương = {p_asymptotic:.6g}")
    else:
        _print_table("Tần số kỳ vọng E", example.columns, example.labels, result.expected)
        _print_table("Đóng góp (O − E)²/E", example.columns, example.labels, result.contributions)
        print(f"χ² = {result.statistic:.6g}    df = {result.df}    p = {result.p_value:.6g}")
    decision = "Bác bỏ H₀" if result.p_value <= ALPHA else "Chưa đủ bằng chứng bác bỏ H₀"
    print(f"α = {ALPHA:.2f}    {decision}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo Friedman và chi bình phương Pearson.")
    parser.add_argument("case", nargs="*", metavar="MÃ", help="F1 F2 F3 C1 C2 C3")
    args = parser.parse_args()
    unknown = [code for code in args.case if code not in EXAMPLES]
    if unknown:
        parser.error(f"Mã ví dụ không hợp lệ: {', '.join(unknown)}")
    print("Dữ liệu giả lập dùng để minh họa.")
    for case_id in args.case or EXAMPLES:
        run(case_id)


if __name__ == "__main__":
    main()
