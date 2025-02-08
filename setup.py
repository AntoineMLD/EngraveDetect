from setuptools import setup, find_packages

setup(
    name="engravedetect",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'sqlalchemy',
        'pydantic',
        'python-jose[cryptography]',
        'passlib[bcrypt]',
        'pytest',
        'pytest-asyncio',
        'httpx',
        'scrapy',
        'pillow',
        'torch',
        'torchvision',
    ],
    python_requires='>=3.8',
) 