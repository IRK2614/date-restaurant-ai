import os
import streamlit as st
from google import genai
from google.genai import types

# ページ基本設定
st.set_page_config(
    page_title="デート飯ナビ AI",
    page_icon="🍽️",
    layout="centered"
)

st.title("🍽️ デート飯ナビ AI")
st.caption("雰囲気・写真映え・忖度なしの口コミから最適なお店をピックアップ")

# サイドバーまたは設定エリアでAPIキーを入力（初回のみ）
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    # 環境変数からの読み込みも試行
    api_key = os.environ.get("GEMINI_API_KEY", "")

st.markdown("---")

# 入力フォーム
col1, col2 = st.columns(2)
with col1:
    location = st.text_input("📍 エリア（駅名・市区町村）", value="栄駅")
with col2:
    genre = st.selectbox(
        "🍳 ジャンル", 
        ["指定なし", "イタリアン", "フレンチ", "和食・割烹", "カフェ・スイーツ", "焼肉・肉料理", "ダイニングバー・居酒屋"]
    )

budget = st.select_slider(
    "💰 予算目安（1人あたり）",
    options=["〜3,000円", "3,000円〜5,000円", "5,000円〜8,000円", "8,000円〜12,000円", "15,000円〜"]
)

# こだわり条件の選択（複数選択可）
preferences = st.multiselect(
    "✨ 重点を置くこだわりポイント",
    ["落ち着いた雰囲気", "店内がおしゃれ", "写真映え・インスタ映え", "デザートが華やか", "コスパ重視", "個室・カウンター重視"],
    default=["落ち着いた雰囲気", "写真映え・インスタ映え"]
)

other_notes = st.text_input("📝 その他リクエスト（例：2軒目利用、デザートプレート対応など）", "")

search_btn = st.button("🔍 忖度なしでおすすめ店を検索する", use_container_width=True)

if search_btn:
    if not api_key:
        st.error("APIキーが設定されていません。サイドバーにGemini API Keyを入力してください。")
    else:
        with st.spinner("Googleマップや最新口コミを分析中..."):
            try:
                # Clientの初期化
                client = genai.Client(api_key=api_key)
                
                # AIへの詳細指示文（プロンプト）
                prompt = f"""
あなたはデート向け飲食店選定のプロフェッショナルです。
以下の条件に最も合致するお店を、Googleマップ検索および実際の最新口コミ情報（Web検索）を徹底分析し、おすすめ順に3店舗選定してください。

【検索条件】
- エリア: {location}
- ジャンル: {genre if genre != '指定なし' else 'デートに適した料理ジャンル'}
- 予算目安: {budget}
- こだわり重視項目: {', '.join(preferences)}
- 追加リクエスト: {other_notes}

【評価・選定基準】
1. 「インスタ映え・写真映え」「店内のおしゃれさ・落ち着いた雰囲気」「デザートの見た目・華やかさ」「コスパ」を総合評価してください。
2. 広告等の忖度は一切排除し、実際のユーザーの口コミに基づいた客観的かつリアルな評価を行ってください。
3. 良い点だけでなく、お店の「懸念点（例：混雑して騒がしい時がある、席間隔が狭い、提供まで時間がかかるなど）」も必ず明記してください。

【出力フォーマット】
店舗ごとに、見やすいMarkdown形式で出力してください。

### 1. 【店舗名】
- **ジャンル**: 
- **最寄り駅**: 
- **予算目安**: 
- **主なメニュー・名物**: 
- **おすすめポイント（雰囲気・写真映えなど）**: 
- **口コミまとめ（良い点）**: 
- **⚠️ 事前に知っておくべき懸念点**: 
- **Googleマップで見る**: [店舗名でGoogle Map検索](https://www.google.com/maps/search/?api=1&query=店舗名+エリア名)

---
(同様に2店舗目、3店舗目を出力)
"""

                # モデル名を gemini-3.8-flash に更新
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    )
                )

                st.success("検索が完了しました！")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
