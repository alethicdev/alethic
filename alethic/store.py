from __future__ import annotations
import threading
from typing import Dict, List, Optional
import time
from .schema import Record, Slot

class MemoryStore:
    def __init__(self) -> None:
        self._records: Dict[str, Record] = {}
        self._by_slot: Dict[str, List[str]] = {}
        self._lock = threading.RLock()

    def _check_ttl(self, rec: Record) -> None:
        if rec.status == "ACTIVE" and rec.prov.ttl_ms is not None:
            now = int(time.time() * 1000)
            if now >= rec.prov.ts_ms + rec.prov.ttl_ms:
                rec.status = "EXPIRED"
                rec.reason = "TTL_EXPIRED"

    def append(self, rec: Record) -> None:
        with self._lock:
            self._records[rec.id] = rec
            self._by_slot.setdefault(rec.slot, []).append(rec.id)

    def get(self, rec_id: str) -> Optional[Record]:
        with self._lock:
            r = self._records.get(rec_id)
            if r:
                self._check_ttl(r)
            return r

    def list_slot(self, slot: Slot) -> List[Record]:
        with self._lock:
            recs = [self._records[i] for i in self._by_slot.get(slot, [])]
            for r in recs:
                self._check_ttl(r)
            return recs

    def find_active_by_kind(self, slot: Slot, kind: str, trace_id: str) -> Optional[Record]:
        with self._lock:
            for rid in self._by_slot.get(slot, []):
                r = self._records[rid]
                self._check_ttl(r)
                if r.kind == kind and r.prov.trace_id == trace_id and r.status == "ACTIVE":
                    return r
            return None

    def invalidate(self, rec_id: str, reason: str) -> None:
        with self._lock:
            r = self._records.get(rec_id)
            if r:
                r.status = "INVALIDATED"
                r.reason = reason

    def close(self) -> None:
        pass
