import streamlit as st

st.set_page_config(page_title="쇼핑 리스트", page_icon="🛒", layout="centered")

# --- 스타일 ---
st.markdown(
    """
    <style>
    /* 본문 폭을 좁혀 리스트 앱처럼 보이게 */
    [data-testid="stMainBlockContainer"] {
        max-width: 620px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }
    /* 버튼 라운드 처리 */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }
    /* 아이템 카드(테두리 컨테이너) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px;
    }
    /* 입력창 */
    .stTextInput input {
        border-radius: 10px;
    }
    /* 헤더 여백 축소 */
    h1 { margin-bottom: 0.2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 상태 초기화 ---
# 주의: st.session_state 는 dict 메서드(items, update 등)와 겹치는 키를
# 속성 접근(st.session_state.items)으로 쓰면 안 되므로 대괄호 접근을 사용한다.
if "cart" not in st.session_state:
    # 각 아이템: {"id": int, "name": str, "checked": bool}
    st.session_state["cart"] = []
if "next_id" not in st.session_state:
    st.session_state["next_id"] = 0
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


def delete_item(item_id: int):
    st.session_state["cart"] = [
        i for i in st.session_state["cart"] if i["id"] != item_id
    ]
    if st.session_state["editing_id"] == item_id:
        st.session_state["editing_id"] = None


def toggle_item(item_id: int):
    for i in st.session_state["cart"]:
        if i["id"] == item_id:
            i["checked"] = not i["checked"]
            break


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


def clear_done():
    st.session_state["cart"] = [
        i for i in st.session_state["cart"] if not i["checked"]
    ]


# --- 헤더 ---
st.title("🛒 쇼핑 리스트")
st.caption("필요한 물건을 추가하고, 담을 때마다 체크하세요.")

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
            "추가", use_container_width=True, type="primary"
        )
    if submitted:
        add_item(new_name)

# --- 진행 상황 ---
cart = st.session_state["cart"]
total = len(cart)
done = sum(1 for i in cart if i["checked"])

if total:
    st.progress(done / total, text=f"**{done} / {total}** 항목 완료")

st.write("")

# --- 아이템 목록 ---
if not cart:
    st.info("아직 담은 물건이 없어요. 위에서 추가해 보세요. 🧺")
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
            st.caption("🎉 장보기 완료!")
        else:
            st.caption(f"남은 항목 {total - done}개")
    with col_clear:
        if done:
            st.button(
                f"완료 항목 {done}개 지우기",
                use_container_width=True,
                on_click=clear_done,
            )
