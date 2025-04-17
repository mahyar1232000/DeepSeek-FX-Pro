# ---------- setup.py ----------
from setuptools import setup, find_packages

setup(
    name='DeepSeek-FX-Pro',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'MetaTrader5>=5.0',
        'scikit-learn>=1.4',
        'pandas>=2.2',
        'numpy>=1.26',
        'tqdm',
        'PyYAML',
        'cryptography',
        'joblib',
        'tensorflow',
        'np_utils'
    ],
    author='Mahyar',
    description='AI-powered multi-timeframe Forex trading system.',
    entry_points={
        'console_scripts': [
            'deepseekfx = main:main'
        ]
    },
)
