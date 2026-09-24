"""
Herramienta Independiente: Electrum UTXOs & Derivación
"""
from src.electrum_utxo.key_manager import KeyManager
from src.electrum_utxo.balance_scanner import MempoolScanner

def main():
    print("--- [ Herramienta: Electrum UTXOs & Derivación ] ---")
    mnemonic = input("Introduce tu frase mnemónica (12/24 palabras): ").strip()
    if not mnemonic:
        print("❌ La mnemónica no puede estar vacía.")
        return

    try:
        print("🔑 Derivando direcciones (BIP84, BIP86, BIP49, BIP44)...")
        km = KeyManager(mnemonic)
        batch = km.scan_derivation_matrix(max_index=3)

        print("🌐 Conectando a Mempool.space para buscar saldos y UTXOs...")
        scanner = MempoolScanner(testnet=True)
        report = scanner.scan_addresses(batch)

        print("\n📊 --- RESULTADOS DEL ESCANEO ---")
        print(f"Saldo Confirmado Total: {report['total_confirmed_sats']} sats")
        print(f"UTXOs Encontrados:      {len(report['all_utxos'])}")
        
        if report['active_addresses']:
            print("\nDirecciones con fondos detectadas:")
            for addr in report['active_addresses']:
                print(f" • [{addr['standard']}] {addr['address']} -> {addr['total_sats']} sats")
        else:
            print("ℹ️ No se encontraron fondos activos en los primeros índices analizados.")

    except Exception as e:
        print(f"❌ Error en el proceso: {e}")

if __name__ == "__main__":
    main()
