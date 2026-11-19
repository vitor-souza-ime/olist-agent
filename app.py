"""Entrypoint for the real-data Olist Intelligent Reviews application."""
import app_real

if __name__ == "__main__":
    if app_real.DEFAULT_ZIP.exists():
        try:
            app_real.STATE["tables"] = app_real.load_zip(app_real.DEFAULT_ZIP.read_bytes())
            app_real.STATE["analysis"] = app_real.analyze_dataset(app_real.STATE["tables"])
        except Exception as exc:
            print(f"Não foi possível carregar o ZIP padrão: {exc}")
    app_real.launch()
