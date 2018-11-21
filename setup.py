from setuptools import setup

setup(
    name="pywpp",
    version="0.1",
    py_modules=["pywpp"],
    install_requires=[
        "Click", "validators", "i3ipc", "python-dotenv", "requests"
    ],
    entry_points="""
        [console_scripts]
        pywpp=pywpp:cli
    """,
)
