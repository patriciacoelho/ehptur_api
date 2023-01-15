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
        'anyio==3.6.1'
        'cachetools==5.2.0'
        'certifi==2022.9.14'
        'cffi==1.15.1'
        'charset-normalizer==2.1.1'
        'click==8.1.3'
        'cryptography==38.0.1'
        'dnspython==2.2.1'
        'fastapi==0.85.0'
        'Flask==2.2.2'
        'Flask-PyMongo==2.3.0'
        'google-auth==2.11.0'
        'google-auth-oauthlib==0.5.3'
        'gunicorn==20.0.4'
        'idna==3.4'
        'importlib-metadata==4.12.0'
        'itsdangerous==2.1.2'
        'Jinja2==3.1.2'
        'MarkupSafe==2.1.1'
        'oauthlib==3.2.1'
        'pyasn1==0.4.8'
        'pyasn1-modules==0.2.8'
        'pycparser==2.21'
        'pydantic==1.10.2'
        'pymongo==4.2.0'
        'pyOpenSSL==22.0.0'
        'python-dotenv==0.21.0'
        'requests==2.28.1'
        'requests-oauthlib==1.3.1'
        'rsa==4.9'
        'six==1.16.0'
        'sniffio==1.3.0'
        'starlette==0.20.4'
        'typing-extensions==4.3.0'
        'urllib3==1.26.12'
        'Werkzeug==2.2.2'
        'zipp==3.8.1'
    ],
)