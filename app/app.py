from datetime import datetime
from random import randint

import streamlit as st
from pymongo import MongoClient

source = {0: "🪨", 1: "✂️", 2: "📄"}


@st.dialog("Имя пользователя")
def ask_username():
    username = st.text_input("Как тебя зовут?")
    if st.button("Submit"):
        st.session_state.username = username
        st.rerun()


if "username" not in st.session_state:
    ask_username()

player = st.session_state.get("username", "Default")
if "winrate" not in st.session_state:
    st.session_state.winrate = {"wins": 0, "loses": 0}


@st.cache_resource
def get_base():
    client = MongoClient(st.secrets.get("DB_URL"))
    db = client["rock_paper_scissors"]
    base = db["game_results"]
    return base


st.subheader("Противник")
bot_res = st.container(height=100)
player_res = st.container(height=100)
st.subheader("Ты")
am = st.session_state.winrate["wins"] + st.session_state.winrate["loses"]
if am > 0:
    st.write(f"Wins: {st.session_state.winrate['wins'] / am:.1%}")
else:
    st.write("Wins:")

def game(player_move: int):
    bot_move = get_move()
    if player_move == bot_move:
        result = 0
    elif (player_move - bot_move) in (-1, 2):
        result = 1
        st.session_state.winrate["wins"] += 1
        player_res.balloons()
    else:
        result = -1
        st.session_state.winrate["loses"] += 1
        player_res.snow()
    
    base.insert_one(
        {
            "player": player,
            "player_move": player_move,
            "bot_move": bot_move,
            "result": result,
            "timestamp": datetime.now(),
        }
    )
    player_res.write(source[player_move])
    bot_res.write(source[bot_move])


def get_move() -> int:
    return randint(0, 2)


base = get_base()

for n, col in enumerate(st.columns(3)):
    with col:
        st.button(source[n], use_container_width=True, on_click=lambda n=n: game(n))
