
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class InterviewStore:
    def __init__(self, base_dir: Path):
        self.path = base_dir / "data" / "interviews.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, payload: dict) -> None:
        record = {
            "received_at": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
        logger.info("Interview request saved to %s", self.path)
