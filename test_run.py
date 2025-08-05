from server.emulator import Emulator

if __name__ == "__main__":
    print("[TEST] Starting test run...")
    emu = Emulator("ttp_profiles/payload_dropper.yaml")
    emu.run()
    print("[TEST] Test run complete.")

