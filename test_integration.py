"""Simple integration test for blueprint-cleaner with Ollama service."""

from __future__ import annotations

import sys
import os

# Add src directories to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ollama_service", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "blueprint-cleaner", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_ollama_service_import():
    """Test that ollama_service can be imported."""
    try:
        from ollama_service.client import ask_ollama_question
        from ollama_service.models import OllamaRequest, OllamaResponse

        print("✓ ollama_service imports successful")
        return True
    except ImportError as e:
        print(f"✗ ollama_service import failed: {e}")
        return False


def test_blueprint_cleaner_integration():
    """Test that blueprint-cleaner can use ollama service."""
    try:
        from blueprint_cleaner.pipeline import _default_summariser

        # Test Pieces service (default)
        pieces_summariser = _default_summariser("pieces")
        print("✓ Pieces summariser created")

        # Test Ollama service
        ollama_summariser = _default_summariser("ollama")
        print("✓ Ollama summariser created")

        return True
    except ImportError as e:
        print(f"✗ Blueprint-cleaner integration failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    """Run integration tests."""
    print("Running integration tests...")
    print()

    tests = [
        test_ollama_service_import,
        test_blueprint_cleaner_integration,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
