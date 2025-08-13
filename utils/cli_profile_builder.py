import argparse
import os
import re
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
                    # Use os.sep for robustness, then replace with dots
                    step = rel_path.replace(os.sep, ".").replace(".py", "")
                    steps.append(step)
        return steps

    def validate_steps(self, steps):
        available = set(self.list_available_ttps())
        valid = [s for s in steps if s in available]
        invalid = [s for s in steps if s not in available]
        return valid, invalid

    def sanitize_filename(self, name):
        # Replace all non-alphanumeric, dash, underscore, or dot with underscore
        return re.sub(r"[^a-zA-Z0-9._-]", "_", name)

    def build_profile(self, name, steps, output_path="profiles"):
        valid_steps, invalid_steps = self.validate_steps(steps)
        if not valid_steps:
            raise ValueError("No valid steps were provided. Aborting profile creation.")
        profile = {
            "name": name,
            "steps": valid_steps
        }
        os.makedirs(output_path, exist_ok=True)
        safe_name = self.sanitize_filename(name)
        profile_path = os.path.join(output_path, f"{safe_name}.yaml")
        with open(profile_path, "w") as f:
            yaml.dump(profile, f, default_flow_style=False)
        return profile_path, invalid_steps

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
    try:
        profile_path, invalid_steps = builder.build_profile(args.name, args.steps)
        print(f"Profile saved to {profile_path}")
        if invalid_steps:
            print("Warning: The following steps were not found and were not included in the profile:")
            for step in invalid_steps:
                print(f"  - {step}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
