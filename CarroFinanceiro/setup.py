from setuptools import setup, find_packages

setup(
    name="CarroFinanceiro",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.43.2",
        "pandas>=2.2.3",
        "pillow>=11.1.0", 
        "requests>=2.32.3",
        "cachetools>=5.5.2",
        "tenacity>=9.0.0",  # Adicionada dependência
    ],
    python_requires=">=3.11",
)
