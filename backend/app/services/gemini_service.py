"""
Gemini API Service
GeminiAIを利用してテキスト生成・解析を行うサービス
"""

import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai


class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        """
        GeminiServiceの初期化

        Args:
            api_key: Gemini API Key（未指定の場合は環境変数から取得）
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        プロンプトからテキストを生成

        Args:
            prompt: 生成用のプロンプト
            **kwargs: 追加のパラメータ

        Returns:
            生成されたテキスト
        """
        try:
            response = self.model.generate_content(prompt, **kwargs)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def analyze_resume(
        self,
        resume_text: str,
        job_requirements: Dict[str, Any],
        evaluation_template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        履歴書・職務経歴書を解析し、評価を生成

        Args:
            resume_text: PDFから抽出した履歴書のテキスト
            job_requirements: 募集要項の情報
            evaluation_template: 評価フォーマットのテンプレート

        Returns:
            評価結果のJSON
        """
        prompt = self._create_evaluation_prompt(
            resume_text,
            job_requirements,
            evaluation_template
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,  # 一貫性のある評価のため低めに設定
                    "top_p": 0.8,
                    "top_k": 40,
                }
            )

            # JSON形式で返す
            result_text = response.text

            # ```json ... ``` のマークダウン記法を除去
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            evaluation_result = json.loads(result_text)
            return evaluation_result

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse evaluation result as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Resume analysis error: {str(e)}")

    def _create_evaluation_prompt(
        self,
        resume_text: str,
        job_requirements: Dict[str, Any],
        evaluation_template: Dict[str, Any]
    ) -> str:
        """
        評価用のプロンプトを生成

        Args:
            resume_text: 履歴書のテキスト
            job_requirements: 募集要項
            evaluation_template: 評価テンプレート

        Returns:
            プロンプト文字列
        """
        prompt = f"""
あなたは経験豊富な採用担当者です。以下の履歴書・職務経歴書を分析し、募集要項に基づいて客観的に評価してください。

# 募集要項
{json.dumps(job_requirements, ensure_ascii=False, indent=2)}

# 評価フォーマット
以下のJSON形式で評価結果を出力してください：
{json.dumps(evaluation_template, ensure_ascii=False, indent=2)}

# 履歴書・職務経歴書
{resume_text}

# 評価の指針
1. **技術スキル (technical_skills)**: 必須スキル・優遇スキルとの合致度を詳細に評価
2. **経験の質 (experience_quality)**: プロジェクト経験の深さ、成果、責任範囲を評価
3. **文化適合性 (cultural_fit)**: 企業価値観との一致度、コミュニケーションスタイルを評価
4. **成長可能性 (growth_potential)**: 学習意欲、スキルの発展軌跡、適応力を評価

各項目について：
- スコアは0-10で評価（10が最高）
- 具体的な根拠を履歴書から引用して記載
- 懸念点があれば明確に指摘
- 次の面接で確認すべき点を提案

overall_scoreは各セクションのスコアを重み付けして計算してください。
recommendationは「強く推薦」「推薦」「条件付き推薦」「不合格」のいずれかを選択してください。

**必ずJSON形式のみを出力してください。説明文は不要です。**
"""
        return prompt
