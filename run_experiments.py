"""Jalankan eksperimen Prompt A/B/C dan simpan output aktual dari API."""

import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:8000"


def main() -> None:
    project_dir = Path(__file__).resolve().parent
    sample_path = project_dir / "sample_input.txt"
    text = sample_path.read_text(encoding="utf-8").strip()

    payload = json.dumps({"text": text}, ensure_ascii=False).encode("utf-8")
    request = Request(
        f"{BASE_URL}/experiments",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=240) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"API mengembalikan HTTP {exc.code}: {detail}")
        print("Periksa apakah server berjalan dan file .env sudah benar.")
        raise SystemExit(1) from exc
    except URLError as exc:
        print(f"Tidak bisa terhubung ke {BASE_URL}: {exc.reason}")
        print("Jalankan server terlebih dahulu dengan: fastapi dev main.py")
        raise SystemExit(1) from exc

    output_dir = project_dir / "experiments"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "actual_outputs.json"
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Eksperimen selesai. Ini adalah output aktual dari API:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\nOutput juga disimpan ke: {output_path}")


if __name__ == "__main__":
    main()
