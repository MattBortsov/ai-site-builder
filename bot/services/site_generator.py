import os
import aiohttp
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from services.utils import (
    generate_filename_from_prompt,
    create_txt_file,
    OUTPUT_DIR,
)
from services.database import async_session
from services.models import Generation


API_URL = os.getenv("API_URL")
HTTP_TIMEOUT = aiohttp.ClientTimeout(total=600)
HOST_URL = os.getenv("HOST_URL", "https://example.com/sites")


async def generate_site(prompt: str) -> str:
    """
    Генерация сайта.
    """
    async with aiohttp.ClientSession(timeout=HTTP_TIMEOUT) as session:
        resp = await session.post(API_URL, json={"prompt": prompt})
        resp.raise_for_status()

        html_chunks = []
        async for chunk in resp.content.iter_chunked(1024):
            html_chunks.append(chunk.decode("utf-8"))
            if "</html>" in html_chunks[-1]:
                break
        html = "".join(html_chunks)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = generate_filename_from_prompt(prompt)
    html_path = OUTPUT_DIR / filename
    html_path.write_text(html, encoding="utf-8")

    async with async_session() as session:
        gen = Generation(filename=filename)
        session.add(gen)
        await session.commit()

    return filename


def get_html_path(filename: str) -> Path:
    """
    Просто возвращает путь к сохранённому HTML по его имени.
    """
    return OUTPUT_DIR / filename


def get_txt_path(filename: str) -> Path:
    """
    Генерирует .txt из существующего HTML (не сохраняет в БД!) и
    возвращает путь к нему.
    """
    html_path = OUTPUT_DIR / filename
    return create_txt_file(html_path)
