"""Alabama Certificate of Proficiency practice scoring.

The state requires a net speed of at least 50 words per minute with 10 or fewer
errors. Only an approved administrator can issue the certificate.
"""

from __future__ import annotations

from dataclasses import dataclass

CERTIFICATION_TEXT = (
    "Alabama needs at least 50 net words per minute with 10 or fewer errors. "
    "This is a practice score, not a certificate. The official certificate comes "
    "from an Alabama Career Center, a business education teacher at an Alabama "
    "school, or an accredited business school, trade school, or college."
)


@dataclass(frozen=True)
class CertificationResult:
    gross_wpm: float
    net_wpm: float
    error_words: int
    accuracy: float
    passed: bool


def word_errors(typed: str, target: str) -> int:
    typed_words = typed.split()
    target_words = target.split()
    positions = max(len(typed_words), len(target_words))
    errors = 0
    for index in range(positions):
        if index >= len(typed_words) or index >= len(target_words) or typed_words[index] != target_words[index]:
            errors += 1
    return errors


def score_test(typed: str, target: str, seconds: float,
               min_net_wpm: float = 50.0, max_errors: int = 10) -> CertificationResult:
    if seconds <= 0:
        minutes = 0.0
    else:
        minutes = seconds / 60
    errors = word_errors(typed, target)
    positions = max(len(typed.split()), len(target.split()))
    accuracy = ((positions - errors) / positions * 100) if positions else 0.0
    if minutes > 0:
        gross = (len(typed) / 5) / minutes
        net = gross - errors / minutes
    else:
        gross = net = 0.0
    return CertificationResult(
        gross_wpm=gross,
        net_wpm=net,
        error_words=errors,
        accuracy=accuracy,
        passed=net >= min_net_wpm and errors <= max_errors,
    )
