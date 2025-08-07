# management/commands/load_top_pokemons.py

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand

from pokemons.dataclasses import PokemonRawData
from pokemons.pokeapi import get_full_pokemon_data
from pokemons.serializers import PokemonDataSerializer
from pokemons.services import (
    create_or_update_pokemon_from_raw,
    estimate_popularity_score,
    extract_base_stats,
)


class Command(BaseCommand):
    help = "Load top-N most popular Pokémon into the database from PokeAPI"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Number of top popular Pokémon to load (default: 100)",
        )
        parser.add_argument(
            "--concurrent",
            type=int,
            default=5,
            help="Number of concurrent API requests (default: 5)",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        concurrent = options["concurrent"]

        self.load_pokemons_sync(limit, concurrent)

    def load_pokemons_sync(self, limit: int, concurrent: int):
        """Load Pokemon data from PokeAPI with concurrent requests"""
        scores = []

        # Create tasks for all Pokemon IDs (1-1025 available in PokeAPI)
        pokemon_ids = list(range(1, 1026))

        self.stdout.write(
            f"Fetching data for 1025 Pokemon with {concurrent} concurrent requests..."
        )

        # Use ThreadPoolExecutor for concurrent API requests
        with ThreadPoolExecutor(max_workers=concurrent) as executor:
            # Submit all tasks for concurrent processing
            future_to_id = {
                executor.submit(self.fetch_pokemon_data_sync, pokemon_id): pokemon_id
                for pokemon_id in pokemon_ids
            }

            # Process completed tasks and collect scores
            for future in as_completed(future_to_id):
                pokemon_id = future_to_id[future]
                try:
                    result = future.result()
                    if result:
                        scores.append(result)
                        self.stdout.write(
                            f"{result['name']} | score: {result['_score']}"
                        )
                except Exception as e:
                    self.stdout.write(f"Error with #{pokemon_id}: {e}")

        # Sort by popularity score and select top Pokemon
        scores.sort(reverse=True, key=lambda x: x["_score"])
        top = scores[:limit]

        self.stdout.write(f"\nSaving top {len(top)} Pokemon to database...")

        # Save top Pokemon to database with validation
        for rank, pokemon_data in enumerate(top, 1):
            try:
                serializer = PokemonDataSerializer(data=pokemon_data)
                if serializer.is_valid():
                    create_or_update_pokemon_from_raw(pokemon_data)
                    self.stdout.write(f"{rank:3}. {pokemon_data['name']} saved.")
                else:
                    self.stdout.write(f"{rank:3}. Invalid data: {serializer.errors}")
            except Exception as e:
                self.stdout.write(f"{rank:3}. Error saving: {e}")

        self.stdout.write(self.style.SUCCESS(f"\nDone. Saved top {len(top)} Pokémon."))

    def fetch_pokemon_data_sync(self, pokemon_id: int):
        """Fetch Pokemon data from PokeAPI with rate limiting"""
        try:
            # Add small delay to be respectful to the API
            time.sleep(0.1)

            # Get Pokemon data from PokeAPI
            pokemon_data = get_full_pokemon_data(pokemon_id)

            # Create structured data for better type safety
            base_stats = extract_base_stats(pokemon_data.get("base_stats", {}))

            pokemon_raw_data = PokemonRawData(
                name=pokemon_data["name"],
                types=pokemon_data["types"],
                color=pokemon_data.get("color"),
                habitat=pokemon_data.get("habitat"),
                abilities=pokemon_data["abilities"],
                flavor_text=pokemon_data.get("flavor_text"),
                base_stats=base_stats,
                image_url=pokemon_data.get("image_url"),
                cries_url=pokemon_data.get("cries_url"),
                game_indices=pokemon_data.get("game_indices", []),
                held_items=pokemon_data.get("held_items", []),
                moves=pokemon_data.get("moves", []),
            )

            # Calculate popularity score based on game indices, held items, and moves
            score = estimate_popularity_score(pokemon_raw_data)

            # Add score to data for sorting
            pokemon_data["_score"] = score

            return pokemon_data

        except Exception:
            return None
