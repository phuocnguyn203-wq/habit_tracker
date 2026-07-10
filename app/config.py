from pathlib import Path

DATABASE_URL = Path(__file__).resolve().parents[0] / 'database/dev.db'
SECRET_KEY = 'a760f84c11ea8d115d0df7b416d782835aea6b10dc35378c53c4d581521dbf1f'