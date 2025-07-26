import os
import dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

dotenv.load_dotenv(dotenv_path)

class Config:
    
    """Class for getting value from env."""
    
    @staticmethod
    def GetValue(key: str) -> str | None:
        envvar = os.getenv(key)
        return envvar