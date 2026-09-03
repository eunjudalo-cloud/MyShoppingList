import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="쇼핑 리스트", page_icon="🛒", layout="centered")

# --- 데이터 저장 (새로고침해도 유지되도록 파일에 보관) ---
DATA_FILE = Path(__file__).parent / "shopping_list.json"


def load_data() -> dict:
    """저장된 쇼핑 리스트를 파일에서 불러온다. 없거나 손상됐으면 빈 리스트."""
    try:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        cart = raw.get("cart", [])
        # 저장된 id 중 최대값 다음부터 새 id 부여
        next_id = raw.get("next_id", max((i["id"] for i in cart), default=-1) + 1)
        return {"cart": cart, "next_id": next_id}
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        return {"cart": [], "next_id": 0}


def save_data() -> None:
    """현재 상태를 파일에 저장한다."""
    payload = {
        "cart": st.session_state["cart"],
        "next_id": st.session_state["next_id"],
    }
    DATA_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

# --- 스타일 (아기자기 파스텔) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Jua&family=Gaegu:wght@400;700&display=swap');

    /* 배경: 크림색 + 은은한 물방울 무늬 */
    .stApp {
        background-color: #FFF9F3;
        background-image: radial-gradient(#FFE1EC 1.4px, transparent 1.4px);
        background-size: 24px 24px;
    }

    /* 본문 폭 */
    [data-testid="stMainBlockContainer"] {
        max-width: 580px;
        padding-top: 2.5rem;
        padding-bottom: 5rem;
    }

    /* 전체 글꼴 */
    html, body, [class*="css"], .stMarkdown, input, textarea, button {
        font-family: 'Gaegu', 'Jua', system-ui, sans-serif;
    }

    /* 제목 */
    .cute-title {
        font-family: 'Jua', sans-serif;
        font-size: 2.4rem;
        color: #FF7EA0;
        text-align: center;
        text-shadow: 2px 2px 0 #FFE1EC;
        letter-spacing: 1px;
        margin: 0.2rem 0 0.1rem;
    }
    .cute-sub {
        font-family: 'Gaegu', sans-serif;
        font-size: 1.15rem;
        color: #C08A72;
        text-align: center;
        margin-bottom: 1.2rem;
    }

    /* 추가 입력 폼: 점선 카드 */
    [data-testid="stForm"] {
        background: #FFFFFF;
        border: 2.5px dashed #FFC2D4;
        border-radius: 22px;
        padding: 1rem 1.1rem 0.6rem;
        box-shadow: 0 6px 0 #FFE8F0;
    }

    /* 입력창 */
    .stTextInput input {
        border-radius: 14px !important;
        border: 2px solid #FFD6E2 !important;
        background: #FFFDFC !important;
        font-size: 1.15rem !important;
        color: #6B5545 !important;
    }
    .stTextInput input::placeholder { color: #E0B7C4 !important; }
    .stTextInput input:focus {
        border-color: #FF8FB0 !important;
        box-shadow: 0 0 0 3px #FFE8F0 !important;
    }

    /* 버튼 공통: 알약 모양 + 눌리는 느낌 */
    .stButton > button, [data-testid="stForm"] button {
        border-radius: 999px !important;
        border: none !important;
        font-family: 'Jua', sans-serif !important;
        transition: transform .08s ease;
    }
    .stButton > button:active, [data-testid="stForm"] button:active {
        transform: translateY(2px);
    }
    /* 강조 버튼 (추가 / 저장) */
    [data-testid^="stBaseButton-primary"] {
        background: #FF8FB0 !important;
        color: #fff !important;
        box-shadow: 0 4px 0 #E86F92 !important;
    }
    [data-testid^="stBaseButton-primary"]:hover { background: #FF7EA0 !important; }
    /* 보조 버튼 (완료 항목 지우기 / 취소) */
    [data-testid^="stBaseButton-secondary"] {
        background: #FFFFFF !important;
        color: #FF7EA0 !important;
        border: 2px solid #FFC2D4 !important;
        box-shadow: 0 4px 0 #FFE8F0 !important;
    }
    /* 아이콘 버튼 (연필 / 휴지통) */
    [data-testid^="stBaseButton-tertiary"] {
        font-size: 1.35rem !important;
        padding: 0.1rem 0.3rem !important;
        filter: grayscale(0.1);
    }
    [data-testid^="stBaseButton-tertiary"]:hover {
        transform: scale(1.15) rotate(-6deg);
        background: transparent !important;
    }

    /* 아이템 카드 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 2.5px solid #FFC5D6 !important;
        border-radius: 20px !important;
        background: #FFFFFF;
        box-shadow: 0 4px 0 #FFE0EB;
        margin-bottom: 6px;
    }
    /* 완료된 아이템 카드는 민트빛으로 (:has 지원 브라우저) */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(input:checked),
    div[data-testid="stVerticalBlockBorderWrapper"]:has([aria-checked="true"]) {
        background: #F1FBF6;
        border-color: #A9E2CC !important;
        box-shadow: 0 4px 0 #DBF1E8;
    }

    /* 체크박스 살짝 키우고 동글동글하게 */
    [data-testid="stCheckbox"] label { font-size: 1.2rem !important; }
    [data-testid="stCheckbox"] label > span:first-child {
        transform: scale(1.2);
        margin-right: 0.5rem;
        border-radius: 8px !important;
    }

    /* 진행 바 */
    [data-testid="stProgress"] p {
        font-family: 'Jua', sans-serif !important;
        color: #C08A72 !important;
        margin-bottom: 0.45rem !important;
    }
    [data-testid="stProgress"] > div > div {
        background: #FFE8F0 !important;
        border-radius: 999px !important;
        height: 16px !important;
        border: 2px solid #FFD6E2;
    }
    [data-testid="stProgress"] > div > div > div {
        background: linear-gradient(90deg, #FFB3C8, #FFD59E) !important;
        border-radius: 999px !important;
    }

    /* 안내 박스 (빈 목록) */
    [data-testid="stAlert"], [data-testid="stAlertContainer"] {
        border-radius: 20px !important;
        border: 2.5px dashed #FFC2D4 !important;
        background: #FFF4F8 !important;
        color: #C08A72 !important;
    }
    [data-testid="stAlert"] p { font-size: 1.15rem !important; color: #C08A72 !important; }
    [data-testid="stAlert"] svg { display: none; }

    /* 캡션 */
    [data-testid="stCaptionContainer"] p { font-size: 1.05rem !important; color: #C08A72 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 상태 초기화 ---
# 주의: st.session_state 는 dict 메서드(items, update 등)와 겹치는 키를
# 속성 접근(st.session_state.items)으로 쓰면 안 되므로 대괄호 접근을 사용한다.
if "cart" not in st.session_state:
    # 각 아이템: {"id": int, "name": str, "checked": bool}
    saved = load_data()
    st.session_state["cart"] = saved["cart"]
    st.session_state["next_id"] = saved["next_id"]
if "editing_id" not in st.session_state:
    st.session_state["editing_id"] = None


def add_item(name: str):
    name = name.strip()
    if not name:
        return
    st.session_state["cart"].append(
        {"id": st.session_state["next_id"], "name": name, "checked": False}
    )
    st.session_state["next_id"] += 1
    save_data()


def delete_item(item_id: int):
    st.session_state["cart"] = [
        i for i in st.session_state["cart"] if i["id"] != item_id
    ]
    if st.session_state["editing_id"] == item_id:
        st.session_state["editing_id"] = None
    save_data()


def toggle_item(item_id: int):
    for i in st.session_state["cart"]:
        if i["id"] == item_id:
            i["checked"] = not i["checked"]
            break
    save_data()


def start_edit(item_id: int):
    # 이전에 남아있을 수 있는 수정 입력값을 비워 현재 이름부터 편집하도록 한다.
    st.session_state.pop(f"edit_{item_id}", None)
    st.session_state["editing_id"] = item_id


def cancel_edit():
    st.session_state["editing_id"] = None


def update_item(item_id: int):
    new_name = st.session_state.get(f"edit_{item_id}", "").strip()
    if not new_name:
        return
    for i in st.session_state["cart"]:
        if i["id"] == item_id:
            i["name"] = new_name
            break
    st.session_state["editing_id"] = None
    save_data()


def clear_done():
    st.session_state["cart"] = [
        i for i in st.session_state["cart"] if not i["checked"]
    ]
    save_data()


# --- 헤더 ---
st.markdown('<div class="cute-title">🛒 쇼핑 리스트 🎀</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="cute-sub">오늘은 뭘 사러 갈까요? 🧺✨</div>', unsafe_allow_html=True
)

# --- 아이템 추가 ---
with st.form("add_form", clear_on_submit=True):
    col_input, col_btn = st.columns([4, 1], vertical_alignment="center")
    with col_input:
        new_name = st.text_input(
            "아이템 추가",
            placeholder="예: 우유, 계란, 빵",
            label_visibility="collapsed",
        )
    with col_btn:
        submitted = st.form_submit_button(
            "담기 🧺", use_container_width=True, type="primary"
        )
    if submitted:
        add_item(new_name)

# --- 진행 상황 ---
cart = st.session_state["cart"]
total = len(cart)
done = sum(1 for i in cart if i["checked"])

if total:
    st.progress(done / total, text=f"🛍️ {done} / {total} 개 담았어요")

st.write("")

# --- 아이템 목록 ---
if not cart:
    st.info("아직 담은 게 없어요! 위에 콕 적어주세요 🐣")
else:
    # 완료되지 않은 항목을 위로, 완료된 항목을 아래로 (입력 순서는 유지)
    for item in sorted(cart, key=lambda i: i["checked"]):
        with st.container(border=True):
            if st.session_state["editing_id"] == item["id"]:
                # 수정 모드
                col_edit, col_save, col_cancel = st.columns(
                    [3, 1, 1], vertical_alignment="center"
                )
                with col_edit:
                    st.text_input(
                        "수정",
                        value=item["name"],
                        key=f"edit_{item['id']}",
                        label_visibility="collapsed",
                    )
                with col_save:
                    st.button(
                        "저장",
                        key=f"save_{item['id']}",
                        use_container_width=True,
                        type="primary",
                        on_click=update_item,
                        args=(item["id"],),
                    )
                with col_cancel:
                    st.button(
                        "취소",
                        key=f"cancel_{item['id']}",
                        use_container_width=True,
                        on_click=cancel_edit,
                    )
            else:
                # 일반 모드
                col_check, col_edit, col_del = st.columns(
                    [6, 1, 1], vertical_alignment="center"
                )
                with col_check:
                    label = f"~~{item['name']}~~" if item["checked"] else item["name"]
                    st.checkbox(
                        label,
                        value=item["checked"],
                        key=f"check_{item['id']}",
                        on_change=toggle_item,
                        args=(item["id"],),
                    )
                with col_edit:
                    st.button(
                        "✏️",
                        key=f"editbtn_{item['id']}",
                        use_container_width=True,
                        type="tertiary",
                        help="이름 수정",
                        on_click=start_edit,
                        args=(item["id"],),
                    )
                with col_del:
                    st.button(
                        "🗑️",
                        key=f"delbtn_{item['id']}",
                        use_container_width=True,
                        type="tertiary",
                        help="삭제",
                        on_click=delete_item,
                        args=(item["id"],),
                    )

    # --- 하단 요약 / 정리 ---
    st.write("")
    col_summary, col_clear = st.columns([3, 2], vertical_alignment="center")
    with col_summary:
        if done == total:
            st.caption("🎉 다 담았어요! 집에 가도 좋아요 🏡")
        else:
            st.caption(f"앞으로 {total - done}개 더! 🐾")
    with col_clear:
        if done:
            st.button(
                f"완료한 {done}개 치우기 🧹",
                use_container_width=True,
                on_click=clear_done,
            )
