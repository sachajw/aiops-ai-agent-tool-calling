LANGUAGE_PACKAGE_BUILD_MAP = {
    "python": {
        "detect_files": [
            "requirements.txt",
            "requirements.in",
            "pyproject.toml",
            "Pipfile",
            "setup.py",
        ],
        "package_managers": {
            "pip": {
                "lock_files": [],
                "install": "pip install -r requirements.txt",
                "build": None,
                "outdated_cmd": "pip list --outdated",
            },
            "pip-tools": {
                "lock_files": ["requirements.txt"],
                "install": "pip install -r requirements.txt",
                "build": None,
                "outdated_cmd": "pip list --outdated",
            },
            "pipenv": {
                "lock_files": ["Pipfile.lock"],
                "install": "pipenv install --deploy",
                "build": None,
                "outdated_cmd": "pipenv update --outdated",
            },
            "poetry": {
                "lock_files": ["poetry.lock"],
                "install": "poetry install --no-root",
                "build": None,
                "outdated_cmd": "poetry show --outdated",
            },
        },
    },
    "nodejs": {
        "detect_files": ["package.json"],
        "package_managers": {
            "npm": {
                "lock_files": ["package-lock.json"],
                "install": "npm install",
                "build": "npm run build",
                "outdated_cmd": "npm outdated",
            },
            "yarn": {
                "lock_files": ["yarn.lock"],
                "install": "yarn install",
                "build": "yarn build",
                "outdated_cmd": "yarn outdated",
            },
            "pnpm": {
                "lock_files": ["pnpm-lock.yaml"],
                "install": "pnpm install",
                "build": "pnpm build",
                "outdated_cmd": "pnpm outdated",
            },
        },
    },
    "go": {
        "detect_files": ["go.mod"],
        "package_managers": {
            "go-mod": {
                "lock_files": ["go.sum"],
                "install": "go mod download",
                "build": "go build ./...",
                "outdated_cmd": "go list -u -m all",
            }
        },
    },
    "java": {
        "detect_files": ["pom.xml", "build.gradle", "build.gradle.kts"],
        "package_managers": {
            "maven": {
                "lock_files": [],
                "install": "mvn dependency:resolve",
                "build": "mvn package",
                "outdated_cmd": "mvn versions:display-dependency-updates",
            },
            "gradle": {
                "lock_files": ["gradle.lockfile"],
                "install": "gradle build",
                "build": "gradle build",
                "outdated_cmd": "./gradlew dependencyUpdates",
            },
        },
    },
    "rust": {
        "detect_files": ["Cargo.toml"],
        "package_managers": {
            "cargo": {
                "lock_files": ["Cargo.lock"],
                "install": "cargo fetch",
                "build": "cargo build --release",
                "outdated_cmd": "cargo install cargo-outdated && cargo outdated",
            }
        },
    },
    "ruby": {
        "detect_files": ["Gemfile"],
        "package_managers": {
            "bundler": {
                "lock_files": ["Gemfile.lock"],
                "install": "bundle install",
                "build": None,
                "outdated_cmd": "bundle outdated",
            }
        },
    },
    "php": {
        "detect_files": ["composer.json"],
        "package_managers": {
            "composer": {
                "lock_files": ["composer.lock"],
                "install": "composer install",
                "build": None,
                "outdated_cmd": "composer outdated",
            }
        },
    },
    "dotnet": {
        "detect_files": ["*.csproj", "*.fsproj", "*.vbproj"],
        "package_managers": {
            "nuget": {
                "lock_files": ["packages.lock.json"],
                "install": "dotnet restore",
                "build": "dotnet build",
                "outdated_cmd": "dotnet list package --outdated",
            }
        },
    },
    "dart": {
        "detect_files": ["pubspec.yaml"],
        "package_managers": {
            "pub": {
                "lock_files": ["pubspec.lock"],
                "install": "dart pub get",
                "build": "dart compile exe",
                "outdated_cmd": "dart pub outdated",
            }
        },
    },
    "flutter": {
        "detect_files": ["pubspec.yaml"],
        "package_managers": {
            "flutter": {
                "lock_files": ["pubspec.lock"],
                "install": "flutter pub get",
                "build": "flutter build",
                "outdated_cmd": "flutter pub outdated",
            }
        },
    },
    "swift": {
        "detect_files": ["Package.swift"],
        "package_managers": {
            "swiftpm": {
                "lock_files": ["Package.resolved"],
                "install": "swift package resolve",
                "build": "swift build",
                "outdated_cmd": "swift package update --dry-run",
            }
        },
    },
    "terraform": {
        "detect_files": ["*.tf"],
        "package_managers": {
            "terraform": {
                "lock_files": [".terraform.lock.hcl"],
                "install": "terraform init",
                "build": "terraform plan",
                "outdated_cmd": "terraform providers lock -platform=all && terraform providers mirror ./mirror",
            }
        },
    },
}
