"""
Setup script for Auto Edit.
Supports standard pip install with optional feature sets.
"""

from setuptools import setup, find_packages
from pathlib import Path
import sys

# Validate Python version
if sys.version_info < (3, 8):
    sys.stderr.write("Error: Auto Edit requires Python 3.8 or higher.\n")
    sys.stderr.write(f"You are using Python {sys.version_info.major}.{sys.version_info.minor}\n")
    sys.exit(1)

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    try:
        long_description = readme_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Warning: Could not read README.md: {e}")

# Read requirements - filter out comments and empty lines
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []

if requirements_file.exists():
    try:
        with open(requirements_file, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    requirements.append(line)
    except Exception as e:
        print(f"Warning: Could not read requirements.txt: {e}")
        sys.exit(1)

# Optional extras for different install types
extras_require = {
    'minimal': [
        'opencv-python>=4.8.0,<5.0.0',
        'ffmpeg-python>=0.2.0,<0.3.0',
        'moviepy>=1.0.3,<2.0.0',
        'librosa>=0.10.0,<0.11.0',
        'soundfile>=0.12.0,<0.13.0',
        'pydub>=0.25.1,<0.26.0',
        'numpy>=1.24.0,<2.0.0',
        'scipy>=1.10.0,<2.0.0',
        'pillow>=10.0.0,<11.0.0',
        'pyyaml>=6.0,<7.0',
        'click>=8.1.0,<9.0',
        'tqdm>=4.65.0,<5.0',
        'colorama>=0.4.6,<0.5.0',
        'python-dotenv>=1.0.0,<2.0.0',
    ],
    'ml': [
        'torch>=2.0.0,<2.2.0',
        'transformers>=4.30.0,<5.0.0',
        'scikit-learn>=1.3.0,<2.0.0',
    ],
    'dev': [
        'pytest>=7.4.0',
        'pytest-cov>=4.1.0',
        'black>=23.7.0',
        'flake8>=6.1.0',
        'mypy>=1.4.0',
    ],
}

# Add 'all' extra that includes everything
extras_require['all'] = (
    extras_require['minimal'] +
    extras_require['ml'] +
    extras_require['dev']
)

setup(
    name="auto-edit",
    version="0.4.0",  # Match current version in README
    description="Automated Stream VOD Highlight Editor with AI-powered clip selection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Auto Edit Team",
    author_email="",
    url="https://github.com/catlandia/Audo-Edit",
    license="MIT",
    python_requires=">=3.8,<3.13",  # Set upper bound for safety
    packages=find_packages(exclude=['tests', 'tests.*', 'docs', 'examples']),
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'auto-edit=auto_edit.cli:main',
            'auto-edit-gui=auto_edit_gui:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Non-Linear Editor",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    keywords="video editing streaming highlights automation",
    project_urls={
        "Bug Reports": "https://github.com/catlandia/Audo-Edit/issues",
        "Source": "https://github.com/catlandia/Audo-Edit",
    },
    zip_safe=False,  # Don't install as a zip file
)
