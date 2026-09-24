"""
Herramienta Independiente: Phoenix Channels & SCB Recovery
"""
from src.phoenix_channels.scb_recovery import PhoenixSCBRecovery

def main():
    print("--- [ Herramienta: Phoenix Channels & SCB Recovery ] ---")
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

if __name__ == "__main__":
    main()
