"""
PDF Parser Service
PDFファイルからテキストを抽出するサービス
"""

import io
from typing import Optional
import PyPDF2
import pdfplumber


class PDFParser:
    """PDFファイルからテキストを抽出するクラス"""

    @staticmethod
    def extract_text_from_bytes(pdf_bytes: bytes) -> str:
        """
        PDFバイトデータからテキストを抽出

        Args:
            pdf_bytes: PDFファイルのバイトデータ

        Returns:
            抽出されたテキスト

        Raises:
            Exception: PDF解析に失敗した場合
        """
        # まずpdfplumberで試す（テーブルやレイアウトの保持が優れている）
        text = PDFParser._extract_with_pdfplumber(pdf_bytes)

        # pdfplumberで十分なテキストが取れなかった場合、PyPDF2でも試す
        if not text or len(text.strip()) < 100:
            text_pypdf = PDFParser._extract_with_pypdf2(pdf_bytes)
            if len(text_pypdf.strip()) > len(text.strip()):
                text = text_pypdf

        if not text or len(text.strip()) < 50:
            raise Exception("PDFからテキストを抽出できませんでした。画像ベースのPDFの可能性があります。")

        return text.strip()

    @staticmethod
    def _extract_with_pdfplumber(pdf_bytes: bytes) -> str:
        """
        pdfplumberを使用してテキストを抽出

        Args:
            pdf_bytes: PDFファイルのバイトデータ

        Returns:
            抽出されたテキスト
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            text_parts = []

            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

            return "\n\n".join(text_parts)
        except Exception as e:
            print(f"pdfplumber extraction failed: {str(e)}")
            return ""

    @staticmethod
    def _extract_with_pypdf2(pdf_bytes: bytes) -> str:
        """
        PyPDF2を使用してテキストを抽出

        Args:
            pdf_bytes: PDFファイルのバイトデータ

        Returns:
            抽出されたテキスト
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_parts = []

            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

            return "\n\n".join(text_parts)
        except Exception as e:
            print(f"PyPDF2 extraction failed: {str(e)}")
            return ""

    @staticmethod
    def extract_text_from_file(file_path: str) -> str:
        """
        PDFファイルパスからテキストを抽出

        Args:
            file_path: PDFファイルのパス

        Returns:
            抽出されたテキスト

        Raises:
            FileNotFoundError: ファイルが見つからない場合
            Exception: PDF解析に失敗した場合
        """
        try:
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
            return PDFParser.extract_text_from_bytes(pdf_bytes)
        except FileNotFoundError:
            raise FileNotFoundError(f"PDFファイルが見つかりません: {file_path}")
        except Exception as e:
            raise Exception(f"PDF解析エラー: {str(e)}")
