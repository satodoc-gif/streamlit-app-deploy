# app.py
from dotenv import load_dotenv
load_dotenv()  # .env（ローカル）や Streamlit Secrets の値を使います

import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# --- 画面情報 ---
st.set_page_config(page_title="専門家モード LLM", page_icon="🤖")
st.title("専門家モード LLM デモ")
st.write("""
このアプリは、入力テキストを **LangChain** 経由で **LLM** に渡し、\
選択した**専門家の視点**で回答します。

**操作方法**  
1. 下のラジオボタンで「専門家の種類」を選択  
2. テキストを入力  
3. 「送信」を押すと、LLMの回答が表示されます  
""")

# --- APIキー確認（.env または Streamlit Secrets） ---
if not (os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)):
    st.error("OPENAI_API_KEY が見つかりません。.env または（Streamlit Cloudなら）Secretsに設定してください。")
    st.stop()

# --- LLM クライアント生成（1回だけ） ---
# ※ langchain-openai 0.2系では model= を推奨
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# --- 専門家プロンプト定義（A/B 自由に編集可能） ---
EXPERT_PROMPTS = {
    "A: キャリアコーチ": (
        "あなたは経験豊富なキャリアコーチです。日本のビジネス文化とテック業界の慣習に詳しく、"
        "現実的で実行可能な提案を行います。回答は3つの箇条書きと、最後にワンポイントアドバイスを1行添えてください。"
    ),
    "B: 栄養士": (
        "あなたは国家資格を持つ栄養士です。科学的根拠に基づいて、食品例とおおよその分量を交えた"
        "具体的な改善案を提示してください。最後にアレルギー配慮の注意点を1つ付けてください。"
    ),
}

# --- UI ---
expert = st.radio("専門家の種類を選択：", list(EXPERT_PROMPTS.keys()))
user_text = st.text_area("入力テキスト（相談内容・質問など）", height=160, placeholder="例：転職面接で短所をどう伝えるべき？")

# --- 課題要件：関数化（入力テキスト & 選択値 → 回答を返す） ---
def run_llm(input_text: str, selected_expert: str) -> str:
    """ラジオの選択に応じたシステムメッセージで LLM を実行し、回答テキストを返す。"""
    system = SystemMessage(content=EXPERT_PROMPTS[selected_expert])
    user = HumanMessage(content=input_text)
    resp = llm.invoke([system, user])
    return resp.content

if st.button("送信"):
    if not user_text.strip():
        st.warning("テキストを入力してください。")
    else:
        with st.spinner("LLMに問い合わせ中..."):
            try:
                answer = run_llm(user_text, expert)
                st.success("回答")
                st.write(answer)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
