from setuptools import setup, find_packages

setup(
    name='gpu_monitor',
    version='1.1',
    packages=find_packages(),
    py_modules=['gpu_monitor'],
    entry_points={
        'console_scripts': [
            'gpu_monitor=gpu_monitor.gpu_monitor:main',
        ],
    },
    install_requires=[
        'fire',
    ],
    author='rosmarinocc',
    author_email='377704784@qq.com',
    description='A tool to monitor GPU usage and send email notifications.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/rosmarinocc/gpu_monitor',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
