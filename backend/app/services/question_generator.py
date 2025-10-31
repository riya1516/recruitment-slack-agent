"""
AI Question Generator Service
AI質問生成サービス
"""

import os
import json
from typing import List, Dict
import google.generativeai as genai


class QuestionGenerator:
    """面接質問を生成するサービス"""

    def __init__(self, api_key: str = None):
        """
        初期化

        Args:
            api_key: Gemini API Key
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def generate_questions(
        self,
        candidate_name: str,
        stage_name: str,
        job_title: str,
        candidate_resume: str = None,
        evaluation_summary: Dict = None,
        num_questions: int = 30
    ) -> List[Dict[str, str]]:
        """
        面接質問を生成

        Args:
            candidate_name: 候補者名
            stage_name: 選考段階名（例: 一次面接、二次面接）
            job_title: 職種
            candidate_resume: 候補者の履歴書テキスト
            evaluation_summary: これまでの評価サマリー
            num_questions: 生成する質問数

        Returns:
            質問のリスト [{"question": "質問内容", "purpose": "質問の目的", "category": "カテゴリ"}]
        """
        prompt = self._create_question_prompt(
            candidate_name,
            stage_name,
            job_title,
            candidate_resume,
            evaluation_summary,
            num_questions
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.8,  # 多様性を高める
                    "top_p": 0.9,
                    "top_k": 40,
                }
            )

            # JSONとして解析
            result_text = response.text.strip()

            # Markdown コードブロックを除去
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]

            result_text = result_text.strip()

            questions = json.loads(result_text)

            return questions

        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON解析エラー: {str(e)}")
            print(f"[DEBUG] レスポンステキスト: {response.text}")
            # フォールバック: シンプルな質問を返す
            return self._get_fallback_questions(stage_name, num_questions)

        except Exception as e:
            print(f"[ERROR] 質問生成エラー: {str(e)}")
            return self._get_fallback_questions(stage_name, num_questions)

    def _create_question_prompt(
        self,
        candidate_name: str,
        stage_name: str,
        job_title: str,
        candidate_resume: str,
        evaluation_summary: Dict,
        num_questions: int
    ) -> str:
        """質問生成用のプロンプトを作成"""

        resume_section = ""
        if candidate_resume:
            resume_section = f"""
【候補者の履歴書・職務経歴書】
{candidate_resume[:2000]}  # 長すぎる場合は切り詰め
"""

        evaluation_section = ""
        if evaluation_summary:
            strengths = evaluation_summary.get("strengths", [])
            concerns = evaluation_summary.get("concerns", [])
            evaluation_section = f"""
【これまでの評価サマリー】
強み: {', '.join(strengths) if strengths else 'なし'}
懸念点: {', '.join(concerns) if concerns else 'なし'}
"""

        stage_guidance = self._get_stage_guidance(stage_name)

        prompt = f"""あなたは優秀な人事担当者です。以下の情報を基に、{stage_name}で使用する面接質問を{num_questions}問生成してください。

【候補者情報】
名前: {candidate_name}
応募職種: {job_title}
選考段階: {stage_name}

{resume_section}

{evaluation_section}

【質問生成のガイドライン】
{stage_guidance}

【出力形式】
以下のJSON形式で、{num_questions}問の質問を生成してください：

[
  {{
    "question": "質問内容",
    "purpose": "この質問で何を確認したいか",
    "category": "技術スキル/経験/文化適合性/成長可能性/動機/価値観/コミュニケーション/問題解決力"
  }},
  ...
]

**重要**:
- 各質問は具体的で、候補者が詳しく答えられるようにしてください
- 候補者の履歴書の内容に基づいた質問を含めてください
- オープンエンドな質問を中心に
- はい/いいえで答えられる質問は避ける
- 面接官が深掘りしやすい質問にする
- 違法な質問（年齢、性別、家族構成など）は避ける
"""

        return prompt

    def _get_stage_guidance(self, stage_name: str) -> str:
        """選考段階に応じたガイダンスを取得"""

        if "書類" in stage_name:
            return """
- 履歴書・職務経歴書の内容を深掘りする質問
- 経歴の詳細確認
- 技術スキルの実務経験確認
- 転職理由・志望動機
"""
        elif "一次" in stage_name or "1次" in stage_name:
            return """
- 技術スキルの深掘り質問
- 具体的なプロジェクト経験
- 問題解決能力の確認
- チームワーク経験
- 基本的な価値観の確認
"""
        elif "二次" in stage_name or "2次" in stage_name:
            return """
- リーダーシップ経験
- 困難な状況での対応
- キャリアビジョン
- 企業文化への適合性
- より深い技術的な質問
"""
        elif "最終" in stage_name:
            return """
- 長期的なキャリアプラン
- 企業への貢献意欲
- 条件面の確認（給与、勤務地など）
- 意思決定の確認
- 入社後の抱負
"""
        else:
            return """
- 候補者の経験とスキルを確認する質問
- 企業文化への適合性
- 動機と意欲の確認
- キャリアプラン
"""

    def _get_fallback_questions(self, stage_name: str, num_questions: int) -> List[Dict[str, str]]:
        """フォールバック用の基本的な質問を返す"""

        base_questions = [
            {
                "question": "これまでの職務経験について教えてください。",
                "purpose": "職務経歴の確認",
                "category": "経験"
            },
            {
                "question": "最も誇りに思うプロジェクトや成果について教えてください。",
                "purpose": "実績と自己認識の確認",
                "category": "経験"
            },
            {
                "question": "なぜ当社に応募されたのですか？",
                "purpose": "志望動機の確認",
                "category": "動機"
            },
            {
                "question": "チームで働く際に大切にしていることは何ですか？",
                "purpose": "チームワーク能力の確認",
                "category": "コミュニケーション"
            },
            {
                "question": "困難な状況に直面した時、どのように対処しますか？具体例を教えてください。",
                "purpose": "問題解決能力の確認",
                "category": "問題解決力"
            },
            {
                "question": "5年後、どのようなキャリアを築いていたいですか？",
                "purpose": "キャリアビジョンの確認",
                "category": "成長可能性"
            },
            {
                "question": "新しい技術やスキルをどのように学んでいますか？",
                "purpose": "学習意欲の確認",
                "category": "成長可能性"
            },
            {
                "question": "仕事で最も重視する価値観は何ですか？",
                "purpose": "価値観の確認",
                "category": "価値観"
            },
            {
                "question": "ストレスをどのように管理していますか？",
                "purpose": "ストレス耐性の確認",
                "category": "価値観"
            },
            {
                "question": "フィードバックを受けた時、どのように対応しますか？",
                "purpose": "成長マインドセットの確認",
                "category": "成長可能性"
            }
        ]

        # num_questionsに合わせて質問を返す
        questions = []
        for i in range(num_questions):
            questions.append(base_questions[i % len(base_questions)])

        return questions
