from setuptools import find_packages,setup

setup(
    name='mcqgenrator',
    version='0.0.1',
    author='Umesh Jadhav',
    author_email='ujadhav25@gmail.com',
    install_requires=["langchain","streamlit","python-dotenv","PyPDF2"],
    packages=find_packages()
)