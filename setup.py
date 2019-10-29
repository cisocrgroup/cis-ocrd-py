"""
Installs:
    - ocrd-cis-align
    - ocrd-cis-training
    - ocrd-cis-profile
    - ocrd-cis-wer
    - ocrd-cis-data
    - ocrd-cis-ocropy-clip
    - ocrd-cis-ocropy-denoise
    - ocrd-cis-ocropy-deskew
    - ocrd-cis-ocropy-binarize
    - ocrd-cis-ocropy-resegment
    - ocrd-cis-ocropy-segment
    - ocrd-cis-ocropy-dewarp
    - ocrd-cis-ocropy-recognize
    - ocrd-cis-ocropy-train
"""

from setuptools import setup
from setuptools import find_packages

print(find_packages())
setup(
    name='ocrd_cis',
    version='0.0.6',
    description='description',
    long_description='long description',
    author='Florian Fink, Tobias Englmeier, Christoph Weber',
    author_email='finkf@cis.lmu.de, englmeier@cis.lmu.de, web_chris@msn.com',
    url='https://github.com/cisocrgroup/ocrd_cis',
    license='MIT',
    #packages=['ocrd_cis', 'ocrd_cis.ocropy', 'ocrd_cis.data', 'ocrd_cis.wer', 'ocrd_cis.profile'],
    packages=find_packages(),
    include_package_data = True,
    install_requires=[
        'ocrd>=1.0.0b19',
        'click',
        'scipy',
        'numpy>=1.17.0',
        'pillow==6.2.0',
        'matplotlib>3.0.0',
        'python-Levenshtein',
        'calamari_ocr'
    ],
    package_data={
        '': ['*.json', '*.yml', '*.yaml', '*.csv.gz', '*.jar'],
        # 'ocrd_cis': ['ocrd_cis/data/ocrd-cis.jar', 'ocrd_cis/data/3gs.csv.gz'],
    },
    scripts=[
        'bashlib/ocrd-cis-lib.sh',
        'bashlib/ocrd-cis-train.sh',
        'bashlib/ocrd-cis-post-correct.sh',
    ],
    entry_points={
        'console_scripts': [
            'ocrd-cis-align=ocrd_cis.align.cli:cis_ocrd_align',
            'ocrd-cis-profile=ocrd_cis.profile.cli:cis_ocrd_profile',
            'ocrd-cis-wer=ocrd_cis.wer.cli:cis_ocrd_wer',
            'ocrd-cis-data=ocrd_cis.data.__main__:main',
            'ocrd-cis-ocropy-binarize=ocrd_cis.ocropy.cli:cis_ocrd_ocropy_binarize',
            'ocrd-cis-ocropy-clip=ocrd_cis.ocropy.cli:cis_ocrd_ocropy_clip',
            'ocrd-cis-ocropy-denoise=ocrd_cis.ocropy.cli:cis_ocrd_ocropy_denoise',
            'ocrd-cis-ocropy-deskew=ocrd_cis.ocropy.cli:cis_ocrd_ocropy_deskew',
            'ocrd-cis-ocropy-dewarp=ocrd_cis.ocropy.cli:cis_ocrd_ocropy_dewarp',
            'ocrd-cis-ocropy-recognize=ocrd_cis.ocropy.cli:cis_ocrd_ocropy_recognize',
            'ocrd-cis-ocropy-rec=ocrd_cis.ocropy.cli:cis_ocrd_ocropy_rec',
            'ocrd-cis-ocropy-resegment=ocrd_cis.ocropy.cli:cis_ocrd_ocropy_resegment',
            'ocrd-cis-ocropy-segment=ocrd_cis.ocropy.cli:cis_ocrd_ocropy_segment',
        ]
    },
)
