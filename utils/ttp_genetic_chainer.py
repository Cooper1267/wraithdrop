import yaml
import random
import os

class TTPGeneticChainer:
    def __init__(self, profile_path, ttp_library_path="modules"):
        self.profile_path = profile_path
        self.ttp_library_path = ttp_library_path
        self.original_chain = self.load_profile()

    def load_profile(self):
        with open(self.profile_path, "r") as f:
            data = yaml.safe_load(f)
        return data.get("steps", [])

    def save_profile(self, steps, name="mutated_profile.yaml"):
        mutated = {
            "name": "Mutated TTP Profile",
            "steps": steps
        }
        with open(os.path.join("profiles", name), "w") as f:
            yaml.dump(mutated, f)
        return os.path.join("profiles", name)

    def mutate_chain(self, mutation_rate=0.3):
        all_ttps = self._gather_all_ttps()
        mutated_chain = []

        for step in self.original_chain:
            if random.random() < mutation_rate:
                mutated_chain.append(random.choice(all_ttps))
            else:
                mutated_chain.append(step)

        return mutated_chain

    def crossover_chain(self, other_chain, point=None):
        if point is None:
            point = random.randint(1, min(len(self.original_chain), len(other_chain)) - 1)
        return self.orig

