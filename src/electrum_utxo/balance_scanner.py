"""
Módulo Escáner de Balances y UTXOs mediante la API REST de Mempool.space.
"""

import time
from typing import Dict, List, Optional
import requests


class MempoolScanner:
    def __init__(self, testnet: bool = False, rate_limit_delay: float = 0.2):
        self.base_url = (
            "https://mempool.space/testnet/api" if testnet else "https://mempool.space/api"
        )
        self.delay = rate_limit_delay

    def get_address_stats(self, address: str) -> Optional[Dict]:
        url = f"{self.base_url}/address/{address}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                chain = data.get("chain_stats", {})
                mempool = data.get("mempool_stats", {})

                funded_txo = chain.get("funded_txo_sum", 0)
                spent_txo = chain.get("spent_txo_sum", 0)
                confirmed_balance = funded_txo - spent_txo

                mempool_funded = mempool.get("funded_txo_sum", 0)
                mempool_spent = mempool.get("spent_txo_sum", 0)
                unconfirmed_balance = mempool_funded - mempool_spent

                return {
                    "address": address,
                    "confirmed_sats": confirmed_balance,
                    "unconfirmed_sats": unconfirmed_balance,
                    "total_sats": confirmed_balance + unconfirmed_balance,
                    "tx_count": chain.get("tx_count", 0) + mempool.get("tx_count", 0),
                }
            return None
        except requests.RequestException as e:
            print(f"Error consultando saldo de {address}: {e}")
            return None

    def get_address_utxos(self, address: str) -> List[Dict]:
        url = f"{self.base_url}/address/{address}/utxo"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                utxos = response.json()
                parsed_utxos = []
                for u in utxos:
                    parsed_utxos.append({
                        "address": address,
                        "txid": u.get("txid"),
                        "vout": u.get("vout"),
                        "value_sats": u.get("value"),
                        "confirmed": u.get("status", {}).get("confirmed", False),
                        "block_height": u.get("status", {}).get("block_height"),
                    })
                return parsed_utxos
            return []
        except requests.RequestException as e:
            print(f"Error consultando UTXOs de {address}: {e}")
            return []

    def scan_addresses(self, address_entries: List[Dict]) -> Dict:
        results = {
            "total_confirmed_sats": 0,
            "total_unconfirmed_sats": 0,
            "active_addresses": [],
            "all_utxos": [],
        }

        for entry in address_entries:
            addr = entry.get("address")
            if not addr:
                continue

            stats = self.get_address_stats(addr)
            if stats and stats["total_sats"] > 0:
                stats["standard"] = entry.get("standard")
                stats["path"] = entry.get("path")
                stats["wif"] = entry.get("wif")

                utxos = self.get_address_utxos(addr)

                results["active_addresses"].append(stats)
                results["all_utxos"].extend(utxos)
                results["total_confirmed_sats"] += stats["confirmed_sats"]
                results["total_unconfirmed_sats"] += stats["unconfirmed_sats"]

            time.sleep(self.delay)

        return results
