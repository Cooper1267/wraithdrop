from modules.recon import decoy_fingerprint

def test_decoy_fingerprint_returns_boolean():
    result = decoy_fingerprint.is_decoy()
    assert isinstance(result, bool)

def test_decoy_fingerprint_run_structure():
    result = decoy_fingerprint.run()
    assert isinstance(result, dict)
    assert result.get("module") == "decoy_fingerprint"
    assert "decoy_detected" in result
    assert isinstance(result["decoy_detected"], bool)

