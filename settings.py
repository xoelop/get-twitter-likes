import os

from dotenv import load_dotenv

load_dotenv()


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root

if __name__ == "__main__":
    print(ROOT_DIR)
