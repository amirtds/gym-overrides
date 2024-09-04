from setuptools import setup

setup(
    name='gym_overrides',
    version='0.0.1',
    author='Amir Tadrisi',
    author_email='amirtds@gmail.com',
    license='MIT',
    description='Customizing The Gymnasium Open edX Instance Plugin',
    packages=[
        'gym_overrides',
    ],
    entry_points={
        'lms.djangoapp': [
            'gym_overrides = gym_overrides.apps:GymOverridesConfig',
        ],
},
)