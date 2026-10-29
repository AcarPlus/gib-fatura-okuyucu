"""Taranmış (metinsiz) PDF sayfalarını Windows'un kendi OCR motoruyla okur."""
import asyncio

import pypdfium2 as pdfium

try:
    from winrt.windows.globalization import Language
    from winrt.windows.graphics.imaging import BitmapPixelFormat, SoftwareBitmap
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.storage.streams import DataWriter
except ImportError:  # Windows dışı / paket yok
    OcrEngine = None

SCALE = 300 / 72  # 300 DPI


def available() -> bool:
    return OcrEngine is not None and OcrEngine.is_language_supported(Language("tr"))


async def _recognize(engine, bgra: bytes, w: int, h: int) -> str:
    writer = DataWriter()
    writer.write_bytes(bgra)
    bmp = SoftwareBitmap.create_copy_from_buffer(writer.detach_buffer(), BitmapPixelFormat.BGRA8, w, h)
    result = await engine.recognize_async(bmp)
    return "\n".join(line.text for line in result.lines)


def pdf_text(path) -> str:
    """PDF'in tüm sayfalarını görüntüye çevirip OCR metnini döndürür."""
    if not available():
        return ""
    engine = OcrEngine.try_create_from_language(Language("tr"))
    pdf = pdfium.PdfDocument(str(path))
    try:
        pages = []
        for page in pdf:
            # OcrEngine.max_image_dimension sınırı (genelde 10000 px)
            scale = min(SCALE, OcrEngine.max_image_dimension / max(page.get_size()))
            bmp = page.render(scale=scale, force_bitmap_format=pdfium.raw.FPDFBitmap_BGRA)
            w, h, stride = bmp.width, bmp.height, bmp.stride
            buf = bytes(bmp.buffer)
            if stride != w * 4:
                buf = b"".join(buf[y * stride:y * stride + w * 4] for y in range(h))
            pages.append(asyncio.run(_recognize(engine, buf, w, h)))
        return "\n".join(pages)
    finally:
        pdf.close()
