import streamlit as st
import json
from datetime import datetime, timedelta
import os

DATA_FILE = "train_data.json"
SCHEDULE_FILE = "train_schedule.json"

# データ読み込み
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"trains": [], "last_updated": None}
    else:
        return {"trains": [], "last_updated": None}

# データ保存
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 時刻表読み込み
def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    else:
        return {}

st.set_page_config(page_title="新幹線遅延情報", layout="centered")
st.title("🚄 新幹線遅延情報共有アプリ")

tab1, tab2, tab3 = st.tabs(["📋 情報を見る", "📝 情報を入力する", "📦 登録情報"])

with tab1:
    st.subheader("現在の登録情報")

    full_data = load_data()
    trains = full_data.get("trains", [])
    last_updated = full_data.get("last_updated")

    # 最終更新表示
    if last_updated:
        dt = datetime.fromisoformat(last_updated)
        elapsed = datetime.now() - dt
        minutes_ago = int(elapsed.total_seconds() // 60)
        st.markdown(f"⏱️ 最終更新：{minutes_ago} 分前")

    # 更新ボタン
    if st.button("🔄 更新"):
        st.rerun()

    if not trains:
        st.info("現在登録されている情報はありません。")
    else:
        for train in trains:
            st.markdown("---")
            st.write(f"🚆 **{train['train_name']}**")
            st.write(f"📍 区間：{train['section']}")
            st.write(f"🚉 名古屋駅 所定発車時刻：{train['departure_time']}")
            delay = int(train["delay_minutes"])
            if delay > 0:
                delayed_time = datetime.strptime(train["departure_time"], "%H:%M") + timedelta(minutes=delay)
                delayed_time_str = delayed_time.strftime("%H:%M")
                st.markdown(f"<span style='color:red;'>🕒 発車予定時刻：{delayed_time_str}（{delay}分遅れ）</span>", unsafe_allow_html=True)
            else:
                st.write("🕒 発車予定時刻：定刻")

with tab2:
    st.subheader("新幹線の遅延情報を入力")

    schedule_data = load_schedule()

    with st.form("input_form"):
        train_type = st.selectbox("列車種別", ["のぞみ", "ひかり", "こだま"], key="train_type")
        train_number = st.text_input("号数（例：99）", key="train_number")
        section = st.selectbox("走行区間", ["新大阪→京都", "京都→岐阜羽島", "岐阜羽島→名古屋"], key="section")

        train_key = f"{train_type}{train_number}"
        departure_time_str = schedule_data.get(train_key, "--:--")

        st.markdown(f"### 所定発車時刻： {departure_time_str}")
        delay_minutes = st.number_input("遅れ（分）", min_value=0, max_value=120, step=1, key="delay_minutes")

        submitted = st.form_submit_button("登録する")

        if submitted:
            train_name = f"{train_type}{train_number}"
            full_data = load_data()
            new_entry = {
                "train_name": train_name,
                "section": section,
                "departure_time": departure_time_str,
                "delay_minutes": int(delay_minutes),
                "station": "名古屋"
            }
            full_data["trains"].append(new_entry)
            full_data["last_updated"] = datetime.now().isoformat()
            save_data(full_data)
            st.success(f"{train_name} を登録しました！")
            st.rerun()

with tab3:
    st.subheader("現在の登録情報一覧と削除・並び替え")

    full_data = load_data()
    trains = full_data.get("trains", [])

    if not trains:
        st.info("登録されている列車情報はありません。")
    else:
        for i, train in enumerate(trains):
            with st.container():
                st.markdown("----")
                st.markdown(f"**🚆 {train['train_name']}**  | {train['section']} | {train['departure_time']} | 遅れ: {train['delay_minutes']}分")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("⬆️ 上へ", key=f"up_{i}") and i > 0:
                        trains[i], trains[i - 1] = trains[i - 1], trains[i]
                        full_data["trains"] = trains
                        save_data(full_data)
                        st.rerun()
                with col2:
                    if st.button("⬇️ 下へ", key=f"down_{i}") and i < len(trains) - 1:
                        trains[i], trains[i + 1] = trains[i + 1], trains[i]
                        full_data["trains"] = trains
                        save_data(full_data)
                        st.rerun()
                with col3:
                    if st.button("🗑️ 削除", key=f"delete_{i}"):
                        del trains[i]
                        full_data["trains"] = trains
                        full_data["last_updated"] = datetime.now().isoformat()
                        save_data(full_data)
                        st.success("削除しました！")
                        st.rerun()
