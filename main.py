"""
Script Principal de Control (CLI) - BTC Recovery Suite
Unifica los módulos de Electrum, Muun y Phoenix en una sola herramienta interactiva.
"""

import sys
from src.electrum_utxo.key_manager import KeyManager
from src.electrum_utxo.balance_scanner import MempoolScanner
from src.muun_swaps.emergency_kit import MuunEmergencyKitDecoder
from src.phoenix_channels.scb_recovery import PhoenixSCBRecovery


def print_banner():
    print("\n" + "=" * 55)
    print("         BTC RECOVERY SUITE - HERRAMIENTA PROPIA         ")
    print("     Inspirado en: Electrum | Muun | Phoenix Wallet      ")
    print("=" * 55)


def menu_electrum():
    print("\n--- [ Módulo 1: Electrum UTXOs & Derivación ] ---")
    mnemonic = input("Introduce tu frase mnemónica (12/24 palabras): ").strip()
    if not mnemonic:
        print("❌ La mnemónica no puede estar vacía.")
        return

    try:
        print("🔑 Derivando direcciones (BIP84, BIP86, BIP49, BIP44)...")
        km = KeyManager(mnemonic)
        batch = km.scan_derivation_matrix(max_index=3)

        print("🌐 Conectando a Mempool.space para buscar saldos y UTXOs...")
        scanner = MempoolScanner(testnet=True)  # Cambiar a False si usas Mainnet
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


def menu_muun():
    print("\n--- [ Módulo 2: Muun Emergency Kit & Descriptores ] ---")
    print("Pega el contenido JSON de tu kit de emergencia:")
    json_content = input("JSON: ").strip()
    
    code = input("Introduce el código de recuperación (opcional, para descifrar xpriv): ").strip()

    try:
        decoder = MuunEmergencyKitDecoder(json_content)
        info = decoder.parse_recovery_data(recovery_code=code if code else None)

        print(f"\n✅ Kit analizado correctamente (Versión: {info['version']})")
        print(f"User xpub:      {info['user_xpub']}")
        print(f"Muun xpub:      {info['muun_xpub']}")
        print(f"Descriptor WSH: {info['descriptors']['p2wsh_multisig_descriptor']}")
        
        if info['user_xpriv_decrypted']:
            print(f"🔑 Clave Privada Descifrada: {info['user_xpriv_decrypted']}")

    except Exception as e:
        print(f"❌ Error procesando el kit: {e}")


def menu_phoenix():
    print("\n--- [ Módulo 3: Phoenix Channels & SCB Recovery ] ---")
    node_id = input("ID del nodo Peer contraparte: ").strip()
    txid = input("TXID de financiamiento del canal: ").strip()
    vout_str = input("Índice de salida (vout, ej. 0): ").strip()
    capacity_str = input("Capacidad del canal en satoshis: ").strip()

    try:
        vout = int(vout_str) if vout_str else 0
        capacity = int(capacity_str) if capacity_str else 0

        channel_info = PhoenixSCBRecovery.parse_channel_peer_info(node_id, txid, vout, capacity)
        phoenix_mgr = PhoenixSCBRecovery()
        plan = phoenix_mgr.generate_recovery_plan([channel_info])

        print("\n🛠️ --- PLAN DE RESCATE GENERADO ---")
        print(f"Total de Canales: {plan['total_channels']}")
        for action in plan['actions']:
            print(f" • Canal #{action['channel_index']}: {action['instructions']}")
            print(f"   Fondos en riesgo: {action['funds_at_risk_sats']} sats")

    except Exception as e:
        print(f"❌ Error generando plan de canales: {e}")


def main():
    while True:
        print_banner()
        print("1. Escanear Saldos y UTXOs (Inspirado en Electrum)")
        print("2. Decodificar Kit de Emergencia (Inspirado en Muun)")
        print("3. Plan de Canales Lightning / SCB (Inspirado en Phoenix)")
        print("4. Salir")

        choice = input("\nSelecciona una opción (1-4): ").strip()

        if choice == "1":
            menu_electrum()
        elif choice == "2":
            menu_muun()
        elif choice == "3":
            menu_phoenix()
        elif choice == "4":
            print("\nSaliendo de la herramienta de recuperación. ¡Hasta pronto!")
            break
        else:
            print("⚠️ Opción no válida. Por favor elige entre 1 y 4.")

        input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    main()
