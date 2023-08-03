from streamlit.connections import ExperimentalBaseConnection
import streamlit as st
import pokebase as pb
from collections import defaultdict
import pandas as pd


class PokebaseConn(ExperimentalBaseConnection):
    def __init__(self, connection_name):
        self._connection_name = connection_name

    def _connect(self, **kwargs):
        return super()._connect(**kwargs)
    
    def fetch_all_pokemon(self, ttl=None) -> list:
        @st.cache_data(ttl=ttl)
        def _fetch_all_pokemon():
            return [p['name'].capitalize() for p in pb.APIResourceList('pokemon')][:151]
        return _fetch_all_pokemon()

    def query(self, pokemon_name: str, ttl=None) -> dict[str, str | pd.DataFrame]:
        @st.cache_data(ttl=ttl)
        def _fetch_pokemon_data(pokemon_name):
            pokemon_data = pb.pokemon(pokemon_name.lower())
            return {
                'images': self._fetch_images(pokemon_data),
                'description': self._fetch_description(pokemon_name),
                'stats': self._fetch_stats(pokemon_data),
                'metadata': self._fetch_metadata(pokemon_data),
                'damage_relations': self._fetch_damage_relations(pokemon_data),
                'moves': self._fetch_moves(pokemon_data),
            }
        
        return _fetch_pokemon_data(pokemon_name)

    def _fetch_stats(self, pokemon_data: pb.APIResource) -> pd.DataFrame:
        stats = {s.stat.name.capitalize(): s.base_stat for s in pokemon_data.stats}
        return pd.DataFrame(stats, index=['Stat Value']).T.rename_axis('Stat Name')

    def _fetch_damage_relations(self, pokemon_data: pb.APIResource) -> pd.DataFrame:
        damage_relations = defaultdict(list)
        for pokemon_type in pokemon_data.types:
            type_data = pb.type_(pokemon_type.type.name)
            for effect, types in type_data.damage_relations.__dict__.items():
                damage_relations[effect.capitalize().replace("_", " ")].extend([type_.name.capitalize() for type_ in types])
        return pd.DataFrame([damage_relations], index=['Types']).T.rename_axis('Effect')

    def _fetch_metadata(self, pokemon_data: pb.APIResource) -> pd.DataFrame:
        metadata = {
            'Name': pokemon_data.name.capitalize(),
            'ID': pokemon_data.id,
            'Height': pokemon_data.height,
            'Weight': pokemon_data.weight,
            'Types': ', '.join(t.type.name.capitalize() for t in pokemon_data.types),
        }
        return pd.DataFrame(metadata, index=['Value']).T.rename_axis('Attribute')

    def _fetch_description(self, pokemon_name: str) -> str:
        return pb.pokemon_species(pokemon_name.lower()).flavor_text_entries[0].flavor_text.replace('\x0c', ' ')

    def _fetch_moves(self, pokemon_data: pb.APIResource) -> pd.DataFrame:
        moves = [move.move.name.capitalize() for move in pokemon_data.moves]
        return pd.DataFrame(moves).rename(columns={0: 'Available Moves'})

    def _fetch_images(self, pokemon_data: pb.APIResource) -> dict:
        sprites = [sprite for sprite in pokemon_data.sprites.__dict__.values() if isinstance(sprite, str)]
        other_sprites_url = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other'
        return {
            'image_url': f'{other_sprites_url}/official-artwork/{pokemon_data.id}.png',
            'gif_url': f"{other_sprites_url}/showdown/{pokemon_data.id}.gif",
            'sprites': sprites,
        }
