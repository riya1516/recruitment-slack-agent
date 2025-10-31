"""
Document Evaluation Service
書類選考の評価を行うサービス
"""

import json
import os
from typing import Dict, Any
from datetime import datetime

from .pdf_parser import PDFParser
from .gemini_service import GeminiService


class DocumentEvaluator:
    """書類選考の評価を行うクラス"""

    def __init__(self, knowledge_base_path: str = None):
        """
        DocumentEvaluatorの初期化

        Args:
            knowledge_base_path: ナレッジベースのディレクトリパス
        """
        if knowledge_base_path is None:
            # デフォルトのナレッジベースパスを設定
            current_dir = os.path.dirname(os.path.abspath(__file__))
            knowledge_base_path = os.path.join(
                current_dir, "..", "knowledge"
            )

        self.knowledge_base_path = knowledge_base_path
        self.job_requirements = self._load_job_requirements()
        self.evaluation_template = self._load_evaluation_template()
        self.pdf_parser = PDFParser()
        self.gemini_service = GeminiService()

    def _load_job_requirements(self) -> Dict[str, Any]:
        """募集要項を読み込む"""
        file_path = os.path.join(
            self.knowledge_base_path, "job_requirements.json"
        )
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"募集要項ファイルが見つかりません: {file_path}"
            )
        except json.JSONDecodeError as e:
            raise Exception(
                f"募集要項ファイルのJSON解析に失敗しました: {str(e)}"
            )

    def _load_evaluation_template(self) -> Dict[str, Any]:
        """評価テンプレートを読み込む"""
        file_path = os.path.join(
            self.knowledge_base_path, "evaluation_template.json"
        )
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"評価テンプレートファイルが見つかりません: {file_path}"
            )
        except json.JSONDecodeError as e:
            raise Exception(
                f"評価テンプレートファイルのJSON解析に失敗しました: {str(e)}"
            )

    def evaluate_from_pdf_bytes(
        self,
        pdf_bytes: bytes,
        candidate_name: str = "候補者"
    ) -> Dict[str, Any]:
        """
        PDFバイトデータから書類選考の評価を行う

        Args:
            pdf_bytes: PDFファイルのバイトデータ
            candidate_name: 候補者名

        Returns:
            評価結果のJSON

        Raises:
            Exception: 評価処理に失敗した場合
        """
        try:
            # 1. PDFからテキストを抽出
            resume_text = self.pdf_parser.extract_text_from_bytes(pdf_bytes)

            # 2. Gemini APIで評価
            evaluation_result = self.gemini_service.analyze_resume(
                resume_text=resume_text,
                job_requirements=self.job_requirements,
                evaluation_template=self.evaluation_template
            )

            # 3. メタデータを追加
            evaluation_result["evaluation_format"]["candidate_name"] = candidate_name
            evaluation_result["evaluation_format"]["evaluation_date"] = (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            evaluation_result["evaluation_format"]["position"] = (
                self.job_requirements.get("job_title", "未指定")
            )

            return evaluation_result

        except Exception as e:
            raise Exception(f"評価処理に失敗しました: {str(e)}")

    def evaluate_from_pdf_file(
        self,
        file_path: str,
        candidate_name: str = "候補者"
    ) -> Dict[str, Any]:
        """
        PDFファイルパスから書類選考の評価を行う

        Args:
            file_path: PDFファイルのパス
            candidate_name: 候補者名

        Returns:
            評価結果のJSON

        Raises:
            FileNotFoundError: ファイルが見つからない場合
            Exception: 評価処理に失敗した場合
        """
        try:
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
            return self.evaluate_from_pdf_bytes(pdf_bytes, candidate_name)
        except FileNotFoundError:
            raise FileNotFoundError(f"PDFファイルが見つかりません: {file_path}")
        except Exception as e:
            raise Exception(f"評価処理に失敗しました: {str(e)}")

    def format_evaluation_result(self, evaluation_result: Dict[str, Any]) -> str:
        """
        評価結果を読みやすいテキスト形式にフォーマット

        Args:
            evaluation_result: 評価結果のJSON

        Returns:
            フォーマットされた評価結果のテキスト
        """
        eval_data = evaluation_result.get("evaluation_format", {})

        output = []
        output.append("=" * 60)
        output.append("📋 書類選考評価結果")
        output.append("=" * 60)
        output.append(f"候補者名: {eval_data.get('candidate_name', '未記入')}")
        output.append(f"評価日時: {eval_data.get('evaluation_date', '未記入')}")
        output.append(f"応募職種: {eval_data.get('position', '未記入')}")
        output.append(f"総合スコア: {eval_data.get('overall_score', 0)}/10")
        output.append(f"推薦度: {eval_data.get('recommendation', '未評価')}")
        output.append("")

        sections = eval_data.get("sections", {})

        # 各評価セクション
        for section_key, section_name in [
            ("technical_skills", "💻 技術スキル"),
            ("experience_quality", "📚 経験の質"),
            ("cultural_fit", "🤝 文化適合性"),
            ("growth_potential", "🌱 成長可能性")
        ]:
            section_data = sections.get(section_key, {})
            output.append(f"\n{section_name}")
            output.append("-" * 60)
            output.append(
                f"スコア: {section_data.get('score', 0)}/"
                f"{section_data.get('max_score', 10)}"
            )
            output.append(f"概要: {section_data.get('summary', '未記入')}")
            output.append("")

        # 次のステップ
        next_steps = eval_data.get("next_steps", {})
        output.append("\n📌 次のステップ")
        output.append("-" * 60)
        output.append(
            f"面接進行: {'✅ 推奨' if next_steps.get('proceed_to_interview') else '❌ 非推奨'}"
        )

        focus_areas = next_steps.get("interview_focus_areas", [])
        if focus_areas:
            output.append("\n面接での確認事項:")
            for i, area in enumerate(focus_areas, 1):
                output.append(f"  {i}. {area}")

        questions = next_steps.get("questions_to_clarify", [])
        if questions:
            output.append("\n明確にすべき質問:")
            for i, question in enumerate(questions, 1):
                output.append(f"  {i}. {question}")

        output.append("\n" + "=" * 60)

        return "\n".join(output)
