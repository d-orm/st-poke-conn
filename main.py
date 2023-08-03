import streamlit as st
from conn import PokebaseConn


def set_page():
    st.set_page_config(
        layout="centered",
        page_title="Pokebase API Demo",
        page_icon="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/dream-world/poke-ball.png",)


def set_ttl():
    ttl_in_minutes = 30
    st.session_state['ttl'] = ttl_in_minutes * 60


def get_conn():
    if 'conn' not in st.session_state:
        st.session_state['conn'] = st.experimental_connection("pokebase_conn", type=PokebaseConn) 


def title_and_intro():
    _, col2, _ = st.columns((4, 1, 4))
    with col2:
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/dream-world/poke-ball.png", use_column_width=True)
    _, col2, _ = st.columns((4, 3, 4))
    with col2:
        st.image("https://raw.githubusercontent.com/PokeAPI/media/master/logo/pokeapi_256.png", use_column_width=True)
        for _ in range(3): st.write("") 

    with st.expander("About", expanded=False):
        st.write("* This is a demo Streamlit app that uses 'st.experimental_connection' to fetch data from the [Pokebase API](https://github.com/PokeAPI/pokebase).")
        st.write("* Select a Pokemon from the dropdown to see its image, stats, type effectiveness, and moves.")
        st.write("* The API usually takes around 10-30 seconds to fetch all the data for a Pokemon.")
        st.write(f"* Visited Pokemon data will be cached for {st.session_state['ttl'] // 60} minutes.")
        for _ in range(3): st.write("") 


def fetch_pokemon_data():
    all_pokes = st.session_state['conn'].fetch_all_pokemon(ttl=st.session_state['ttl'])
    st.selectbox(label="Select a Pokemon", options=all_pokes, key="active_pokemon_name", index=24)
    st.session_state['active_pokemon_data'] = st.session_state['conn'].query(ttl=st.session_state['ttl'], pokemon_name=st.session_state['active_pokemon_name'])


def img_and_desc():
    _, col2, _ = st.columns((1, 3, 1))
    with col2:
        st.image(st.session_state['active_pokemon_data']['images']['image_url'], use_column_width=True)
    st.subheader("Description")        
    st.write(st.session_state['active_pokemon_data']['description'])


def stats_and_metadata():
    st.subheader("Stats and Metadata")        
    _, col2, _ = st.columns((1, 5, 1))
    with col2:
        col1, col2, _ = st.columns([2, 2, 1])
        with col1: st.dataframe(st.session_state['active_pokemon_data']['stats'], width=1000)
        with col2: st.dataframe(st.session_state['active_pokemon_data']['metadata'], width=1000)


def damage_relations():
    st.subheader("Damage Relations")
    st.dataframe(st.session_state['active_pokemon_data']['damage_relations'], width=1000)


def moves_and_sprites():
    st.subheader("Moves and Sprites")
    col1, col2, col3 = st.columns([3, 2, 3])
    with col1:
        st.dataframe(st.session_state['active_pokemon_data']['moves'], hide_index=True, width=200)
    with col2:
        for _ in range(2): st.write("") 
        st.image(st.session_state['active_pokemon_data']['images']['gif_url'])
    with col3:
        st.image(st.session_state['active_pokemon_data']['images']['sprites'])


def main():
    set_page()
    set_ttl()
    get_conn()
    title_and_intro()
    fetch_pokemon_data()
    img_and_desc()
    stats_and_metadata()
    damage_relations()
    moves_and_sprites()

if __name__ == "__main__":
    main()
