"""
Herramienta Independiente: Muun Emergency Kit & Descriptores
"""
from src.muun_swaps.emergency_kit import MuunEmergencyKitDecoder

def main():
    print("--- [ Herramienta: Muun Emergency Kit & Descriptores ] ---")
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
        
        if info.get('user_xpriv_decrypted'):
            print(f"🔑 Clave Privada Descifrada: {info['user_xpriv_decrypted']}")

    except Exception as e:
        print(f"❌ Error procesando el kit: {e}")

if __name__ == "__main__":
    main()
