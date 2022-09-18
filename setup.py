from setuptools import setup, find_packages

setup(
    name="api",
    description="Uma API simples para uma aplicação que agrega informações sobre viagens locais",
    version="0.1.0",
    author="Patrícia Coelho",
    author_email="patriciacoelho.pts@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "dnspython == 2.2.1",
        "fastapi == 0.85.0",
        "Flask == 2.2.2",
        "Flask-PyMongo==2.3.0",
        "google-auth == 2.11.0",
        "google-auth-oauthlib == 0.5.3",
        "oauthlib == 3.2.1",
        "pydantic == 1.10.2",
        "pymongo == 4.2.0",
        "python-dotenv == 0.21.0",
        "requests == 2.28.1",
        "requests-oauthlib == 1.3.1",
    ],
)