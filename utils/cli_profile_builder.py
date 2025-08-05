import argparse
import os
import yaml

class CLIProfileBuilder:
    def __init__(self, modules_path="modules"):
        self.modules_path = modules_path

    def list_available_ttps(self):
        steps = []
        for root, _, files in os.walk(self.modules_path):
            for file in files:
                if file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file), self.modules_path)
                    step = rel_path.replace("\\", ".").replace("/", ".").replace(".py", "")
                    steps.append(step)
        return steps

    def validate_steps(self, steps):
        available = set(self.list_available_ttps())
        return [s for s in steps if s in available]

    def build_profile(self, name, steps, output_path="profiles"):
        valid_steps = self.validate_steps(steps)
        profile = {
            "name": name,
            "steps": valid_steps
        }
        os.makedirs(output_path, exist_ok=True)
        with open(os.path.join(output_path, f"{name}.yaml"), "w") as f:
            yaml.dump(profile, f)
        return os.path.join(output_path, f"{name}.yaml")

def load_profile(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Profile not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="WraithDrop TTP Profile Builder")
    parser.add_argument("--name", required=True, help="Name of the profile")
    parser.add_argument("--steps", nargs="+", required=True, help="List of TTP steps to include")

    args = parser.parse_args()
    builder = CLIProfileBuilder()
    profile_path = builder.build_profile(args.name, args.steps)
    print(f"Profile saved to {profile_path}")

if __name__ == "__main__":
    main()

