import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.database import async_session
from services.models import Generation
from common.constants import OUTPUT_DIR, RETENTION_DAYS


def slugify(text: str) -> str:
    """
    Преобразует текст в "slug": латиница, цифры и тире,
    обрезает длину до 20 символов.
    """
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text.lower())
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-')[:20]


def generate_filename_from_prompt(prompt: str) -> str:
    """
    Генерирует уникальное имя файла для хранения HTML-страницы.
    """
    slug = slugify(prompt)
    uid = uuid.uuid4().hex[:6]
    return f"{slug}-{uid}.html"


async def cleanup_old_sites() -> None:
    """
    Удаляет записи в БД и файлы .html/.txt для генераций старше RETENTION_DAYS.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    async with async_session() as session:  # type: AsyncSession
        # достать все старые записи
        result = await session.execute(
            select(Generation).where(Generation.created_at < cutoff)
        )
        old_gens = result.scalars().all()

        # удалить файлы
        for gen in old_gens:
            html_path = OUTPUT_DIR / gen.filename
            txt_path = html_path.with_suffix('.txt')
            for p in (html_path, txt_path):
                if p.exists():
                    try:
                        p.unlink()
                    except Exception:
                        pass

        # удалить записи из БД
        await session.execute(
            delete(Generation).where(Generation.created_at < cutoff)
        )
        await session.commit()


def create_txt_file(html_path: Path) -> Path:
    """
    По существующему HTML-файлу создает .txt-файл с тем же содержимым.
    Возвращает путь к новому .txt-файлу.
    """
    txt_path = html_path.with_suffix('.txt')
    content = html_path.read_text(encoding='utf-8')
    txt_path.write_text(content, encoding='utf-8')
    return txt_path
