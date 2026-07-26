"""
Module cấu hình logging tập trung cho toàn bộ pipeline.

Tất cả các module khác gọi get_logger(__name__) thay vì tự cấu hình
logging riêng lẻ, để đảm bảo format và level log nhất quán trong toàn dự án.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

_CONFIGURED = False

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%H:%M:%S"


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Cấu hình root logger một lần duy nhất cho cả pipeline.

    Args:
        level: mức log tối thiểu (logging.DEBUG khi cần soi lỗi chi tiết).
        log_file: nếu truyền vào, log sẽ được ghi thêm ra file này
                   (hữu ích khi debug lỗi detection trên nhiều ảnh).
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    # Console Windows mặc định dùng codepage cp1252, không encode được dấu
    # tiếng Việt (ví dụ "Đang", "sẵn") -> ép UTF-8 để log tiếng Việt không
    # làm crash logging handler khi chạy trên terminal Windows mặc định.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, AttributeError):
            pass

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=handlers,
        force=True,
    )
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """
    Lấy logger cho một module cụ thể.

    Nếu setup_logging() chưa được gọi (ví dụ khi import module để unit test
    riêng lẻ), tự động cấu hình với mức INFO mặc định để không bị mất log.
    """
    if not _CONFIGURED:
        setup_logging()
    return logging.getLogger(name)
