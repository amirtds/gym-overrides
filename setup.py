from setuptools import setup

setup(
    name='gym_overrides',
    version='0.0.1',
    license='MIT',
    description='Customizing The Gymnasium Open edX Instance Plugin',
    entry_points={
        'lms.djangoapp': [
            'gym_overrides = gym_overrides.apps:GymOverridesConfig',
        ],
},
)