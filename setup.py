from setuptools import setup

setup(
    name="eda_artefact",
    version="0.1.0",
    description="python implementation of the EDA Artefact detection algorithm by Gashi et al.",
    url="https://github.com/LeonardoAlchieri/EDArtifact",
    author="Leonardo Alchieri",
    author_email="leonardo@alchieri.eu",
    license="",
    packages=["eda_artefact_detection", "eda_artefact_detection.detection"],
    install_requires=["pandas", "numpy", "xgboost", "scipy", "cvxEDA", "PyWavelets"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
