#!/usr/bin/env python3
"""
Tests for the dependency_analyzer module.

Tests package manager detection, dependency file reading,
and outdated package checking functionality.
"""

import json
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock

import pytest

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependency_analyzer import (
    clone_repository,
    detect_package_manager,
    read_dependency_file,
    check_npm_outdated,
    check_pip_outdated,
    cleanup_repository
)


class TestDetectPackageManager:
    """Test cases for detect_package_manager function."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_repo_")
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def test_detect_npm_package_manager(self, temp_repo):
        """Test detection of npm package manager."""
        # Create package.json
        with open(os.path.join(temp_repo, "package.json"), "w") as f:
            json.dump({"name": "test", "version": "1.0.0"}, f)

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "npm" in result
        assert "package.json" in result["npm"]["files"]

    def test_detect_npm_with_package_lock(self, temp_repo):
        """Test detection of npm with package-lock.json."""
        with open(os.path.join(temp_repo, "package.json"), "w") as f:
            json.dump({"name": "test"}, f)
        with open(os.path.join(temp_repo, "package-lock.json"), "w") as f:
            json.dump({}, f)

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "npm" in result
        assert "package-lock.json" in result["npm"]["lock_files"]

    def test_detect_yarn(self, temp_repo):
        """Test detection of yarn lock file."""
        with open(os.path.join(temp_repo, "package.json"), "w") as f:
            json.dump({"name": "test"}, f)
        with open(os.path.join(temp_repo, "yarn.lock"), "w") as f:
            f.write("")

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "npm" in result
        assert "yarn.lock" in result["npm"]["lock_files"]

    def test_detect_pnpm(self, temp_repo):
        """Test detection of pnpm lock file."""
        with open(os.path.join(temp_repo, "package.json"), "w") as f:
            json.dump({"name": "test"}, f)
        with open(os.path.join(temp_repo, "pnpm-lock.yaml"), "w") as f:
            f.write("")

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "npm" in result
        assert "pnpm-lock.yaml" in result["npm"]["lock_files"]

    def test_detect_pip(self, temp_repo):
        """Test detection of pip package manager."""
        with open(os.path.join(temp_repo, "requirements.txt"), "w") as f:
            f.write("requests==2.28.0\n")

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "pip" in result
        assert "requirements.txt" in result["pip"]["files"]

    def test_detect_pipenv(self, temp_repo):
        """Test detection of pipenv package manager."""
        with open(os.path.join(temp_repo, "Pipfile"), "w") as f:
            f.write("[packages]\n")

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "pipenv" in result
        assert "Pipfile" in result["pipenv"]["files"]

    def test_detect_poetry(self, temp_repo):
        """Test detection of poetry package manager."""
        with open(os.path.join(temp_repo, "pyproject.toml"), "w") as f:
            f.write("[tool.poetry]\nname = 'test'\n")

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "poetry" in result
        assert "pyproject.toml" in result["poetry"]["files"]

    def test_detect_cargo(self, temp_repo):
        """Test detection of cargo (Rust) package manager."""
        with open(os.path.join(temp_repo, "Cargo.toml"), "w") as f:
            f.write("[package]\nname = 'test'\n")

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "cargo" in result
        assert "Cargo.toml" in result["cargo"]["files"]

    def test_detect_go_mod(self, temp_repo):
        """Test detection of Go modules."""
        with open(os.path.join(temp_repo, "go.mod"), "w") as f:
            f.write("module test\n")

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "go" in result
        assert "go.mod" in result["go"]["files"]

    def test_detect_bundler(self, temp_repo):
        """Test detection of bundler (Ruby) package manager."""
        with open(os.path.join(temp_repo, "Gemfile"), "w") as f:
            f.write("source 'https://rubygems.org'\n")

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "bundler" in result
        assert "Gemfile" in result["bundler"]["files"]

    def test_detect_maven(self, temp_repo):
        """Test detection of Maven (Java) package manager."""
        with open(os.path.join(temp_repo, "pom.xml"), "w") as f:
            f.write("<project></project>")

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "maven" in result
        assert "pom.xml" in result["maven"]["files"]

    def test_detect_gradle(self, temp_repo):
        """Test detection of Gradle (Java) package manager."""
        with open(os.path.join(temp_repo, "build.gradle"), "w") as f:
            f.write("plugins {}")

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "gradle" in result
        assert "build.gradle" in result["gradle"]["files"]

    def test_detect_composer(self, temp_repo):
        """Test detection of Composer (PHP) package manager."""
        with open(os.path.join(temp_repo, "composer.json"), "w") as f:
            json.dump({"name": "test/project"}, f)

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "composer" in result
        assert "composer.json" in result["composer"]["files"]

    def test_detect_multiple_package_managers(self, temp_repo):
        """Test detection of multiple package managers in same repo."""
        # Create both npm and pip files
        with open(os.path.join(temp_repo, "package.json"), "w") as f:
            json.dump({"name": "test"}, f)
        with open(os.path.join(temp_repo, "requirements.txt"), "w") as f:
            f.write("requests==2.28.0\n")

        result = json.loads(detect_package_manager.invoke(temp_repo))

        assert "npm" in result
        assert "pip" in result

    def test_detect_no_package_manager(self, temp_repo):
        """Test detection when no package manager files exist."""
        result = json.loads(detect_package_manager.invoke(temp_repo))
        assert result == {}


class TestReadDependencyFile:
    """Test cases for read_dependency_file function."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_repo_")
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def test_read_package_json(self, temp_repo):
        """Test reading package.json file."""
        content = {"name": "test", "version": "1.0.0", "dependencies": {"lodash": "^4.17.0"}}
        with open(os.path.join(temp_repo, "package.json"), "w") as f:
            json.dump(content, f)

        result = read_dependency_file.invoke({"repo_path": temp_repo, "file_path": "package.json"})

        assert "test" in result
        assert "lodash" in result

    def test_read_requirements_txt(self, temp_repo):
        """Test reading requirements.txt file."""
        with open(os.path.join(temp_repo, "requirements.txt"), "w") as f:
            f.write("requests==2.28.0\nflask>=2.0.0\n")

        result = read_dependency_file.invoke({"repo_path": temp_repo, "file_path": "requirements.txt"})

        assert "requests==2.28.0" in result
        assert "flask>=2.0.0" in result

    def test_read_nonexistent_file(self, temp_repo):
        """Test reading a file that doesn't exist."""
        result = read_dependency_file.invoke({"repo_path": temp_repo, "file_path": "nonexistent.txt"})

        assert "Error" in result


class TestCheckNpmOutdated:
    """Test cases for check_npm_outdated function."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_repo_")
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def test_no_package_json(self, temp_repo):
        """Test check_npm_outdated when no package.json exists."""
        original_dir = os.getcwd()

        result = json.loads(check_npm_outdated.invoke({"repo_path": temp_repo}))

        assert result["status"] == "error"
        assert "No package.json found" in result["message"]
        # Verify working directory is restored
        assert os.getcwd() == original_dir

    def test_working_directory_restored_on_error(self, temp_repo):
        """Test that working directory is restored even on error."""
        original_dir = os.getcwd()

        # Call without package.json
        check_npm_outdated.invoke({"repo_path": temp_repo})

        # Verify we're back in original directory
        assert os.getcwd() == original_dir

    @patch("dependency_analyzer.subprocess.run")
    def test_npm_outdated_success(self, mock_run, temp_repo):
        """Test successful npm outdated check."""
        # Create package.json
        with open(os.path.join(temp_repo, "package.json"), "w") as f:
            json.dump({"name": "test", "dependencies": {"lodash": "^4.17.0"}}, f)

        # Mock npm outdated response
        mock_run.return_value = MagicMock(
            returncode=1,  # npm outdated returns 1 when packages are outdated
            stdout=json.dumps({
                "lodash": {
                    "current": "4.17.0",
                    "wanted": "4.17.21",
                    "latest": "4.17.21",
                    "location": "node_modules/lodash"
                }
            }),
            stderr=""
        )

        result = json.loads(check_npm_outdated.invoke({"repo_path": temp_repo}))

        assert result["status"] == "success"
        assert result["package_manager"] == "npm"
        assert result["outdated_count"] == 1
        assert result["outdated_packages"][0]["name"] == "lodash"

    @patch("dependency_analyzer.subprocess.run")
    def test_npm_all_up_to_date(self, mock_run, temp_repo):
        """Test when all npm packages are up to date."""
        with open(os.path.join(temp_repo, "package.json"), "w") as f:
            json.dump({"name": "test"}, f)

        # Mock empty response (all up to date)
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = json.loads(check_npm_outdated.invoke({"repo_path": temp_repo}))

        assert result["status"] == "success"
        assert result["outdated_count"] == 0


class TestCheckPipOutdated:
    """Test cases for check_pip_outdated function."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_repo_")
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def test_no_requirements_txt(self, temp_repo):
        """Test check_pip_outdated when no requirements.txt exists."""
        result = json.loads(check_pip_outdated.invoke({"repo_path": temp_repo}))

        assert result["status"] == "error"
        assert "No requirements.txt found" in result["message"]

    @patch("dependency_analyzer.requests.get")
    def test_pip_outdated_success(self, mock_get, temp_repo):
        """Test successful pip outdated check."""
        # Create requirements.txt
        with open(os.path.join(temp_repo, "requirements.txt"), "w") as f:
            f.write("requests==2.25.0\n")

        # Mock PyPI response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"info": {"version": "2.31.0"}}
        mock_get.return_value = mock_response

        result = json.loads(check_pip_outdated.invoke({"repo_path": temp_repo}))

        assert result["status"] == "success"
        assert result["package_manager"] == "pip"
        assert len(result["outdated_packages"]) == 1
        assert result["outdated_packages"][0]["name"] == "requests"
        assert result["outdated_packages"][0]["current"] == "2.25.0"
        assert result["outdated_packages"][0]["latest"] == "2.31.0"

    def test_parse_requirements_with_comments(self, temp_repo):
        """Test parsing requirements.txt with comments."""
        with open(os.path.join(temp_repo, "requirements.txt"), "w") as f:
            f.write("# This is a comment\nrequests==2.25.0\n# Another comment\n")

        with patch("dependency_analyzer.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"info": {"version": "2.31.0"}}
            mock_get.return_value = mock_response

            result = json.loads(check_pip_outdated.invoke({"repo_path": temp_repo}))

            assert result["status"] == "success"
            # Should only have 1 package, not the comments
            assert len(result["outdated_packages"]) == 1

    def test_parse_requirements_with_version_operators(self, temp_repo):
        """Test parsing requirements with different version operators."""
        with open(os.path.join(temp_repo, "requirements.txt"), "w") as f:
            f.write("requests>=2.25.0\nflask==2.0.0\n")

        with patch("dependency_analyzer.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"info": {"version": "3.0.0"}}
            mock_get.return_value = mock_response

            result = json.loads(check_pip_outdated.invoke({"repo_path": temp_repo}))

            assert result["status"] == "success"


class TestCleanupRepository:
    """Test cases for cleanup_repository function."""

    def test_cleanup_valid_path(self):
        """Test cleanup of a valid temporary repository path.

        Note: cleanup_repository only accepts paths starting with /tmp/dep_analyzer_
        or /tmp/repo_check_ for safety. We create the directory explicitly in /tmp.
        """
        # Create directory explicitly in /tmp with the expected prefix
        temp_dir = "/tmp/dep_analyzer_test_cleanup"
        os.makedirs(temp_dir, exist_ok=True)
        with open(os.path.join(temp_dir, "test.txt"), "w") as f:
            f.write("test")

        result = json.loads(cleanup_repository.invoke(temp_dir))

        assert result["status"] == "success"
        assert not os.path.exists(temp_dir)

    def test_cleanup_repo_check_prefix(self):
        """Test cleanup with repo_check_ prefix."""
        temp_dir = "/tmp/repo_check_test_cleanup"
        os.makedirs(temp_dir, exist_ok=True)
        with open(os.path.join(temp_dir, "test.txt"), "w") as f:
            f.write("test")

        result = json.loads(cleanup_repository.invoke(temp_dir))

        assert result["status"] == "success"
        assert not os.path.exists(temp_dir)

    def test_cleanup_invalid_path(self):
        """Test cleanup with invalid path prefix."""
        temp_dir = tempfile.mkdtemp(prefix="invalid_prefix_")

        result = json.loads(cleanup_repository.invoke(temp_dir))

        assert result["status"] == "error"
        # Directory should still exist
        assert os.path.exists(temp_dir)

        # Cleanup manually
        shutil.rmtree(temp_dir)

    def test_cleanup_nonexistent_path(self):
        """Test cleanup of non-existent path."""
        result = json.loads(cleanup_repository.invoke("/tmp/nonexistent_path_12345"))

        assert result["status"] == "error"


class TestCloneRepository:
    """Test cases for clone_repository function."""

    @patch("dependency_analyzer.subprocess.run")
    @patch("dependency_analyzer.get_cache")
    def test_clone_success(self, mock_cache, mock_run):
        """Test successful repository cloning."""
        mock_cache.return_value.get_cached_repository.return_value = None
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = json.loads(clone_repository.invoke("https://github.com/test/repo"))

        assert result["status"] == "success"
        assert "repo_path" in result

    @patch("dependency_analyzer.subprocess.run")
    @patch("dependency_analyzer.get_cache")
    def test_clone_failure(self, mock_cache, mock_run):
        """Test repository clone failure."""
        mock_cache.return_value.get_cached_repository.return_value = None
        mock_run.return_value = MagicMock(
            returncode=128,
            stdout="",
            stderr="fatal: repository not found"
        )

        result = json.loads(clone_repository.invoke("https://github.com/nonexistent/repo"))

        assert result["status"] == "error"
        assert "Failed to clone" in result["message"]

    @patch("dependency_analyzer.get_cache")
    def test_clone_from_cache(self, mock_cache):
        """Test loading repository from cache."""
        # Create a temp directory to simulate cached repo
        temp_cache = tempfile.mkdtemp(prefix="cached_repo_")
        with open(os.path.join(temp_cache, "package.json"), "w") as f:
            json.dump({"name": "cached"}, f)

        mock_cache.return_value.get_cached_repository.return_value = temp_cache

        result = json.loads(clone_repository.invoke("https://github.com/test/repo"))

        assert result["status"] == "success"
        assert result["from_cache"] is True

        # Cleanup
        shutil.rmtree(temp_cache, ignore_errors=True)
        if "repo_path" in result and os.path.exists(result["repo_path"]):
            shutil.rmtree(result["repo_path"], ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
